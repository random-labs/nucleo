from allauth.account.adapter import DefaultAccountAdapter
from allauth.utils import build_absolute_uri

from django.conf import settings
from django.core.mail import send_mass_mail
from django.db.models import Sum
from django.urls import reverse

from . import tasks as nc_tasks
from .models import Activity, Asset, Comment, Portfolio, Profile, Reward
from .queues import get_queue_backend


class AccountAdapter(DefaultAccountAdapter):
    """
    Extension of the allauth.account default adapter for mass mailing
    and feed activity.
    """
    def add_activity(self, context):
        """
        Add activity to user feed.
        """
        if self.request.user.is_authenticated:
            # Create the new Activity instance for our db
            # NOTE: instance will be updated with stream.activity_id after contact stream with adapter below.
            inv_verb_choices = { v: k for k, v in dict(Activity.VERB_CHOICES).iteritems() }
            created_time = context.get('time')
            verb = inv_verb_choices.get(context.get('verb'))
            instance = Activity.objects.create(verb=verb, user_id=self.request.user.id,
                tx_hash=context.get('tx_hash'), created=created_time)

            print 'instance created'
            print instance.id

            # Update the context to include foreign_id as instance.id
            context['foreign_id'] = instance.id
            context['activity_url'] = build_absolute_uri(
                self.request,
                reverse('nc:feed-activity-detail', kwargs={'pk': instance.id})
            )

            print context

            # Queue task to add activity to user feed
            get_queue_backend().delay(
                nc_tasks.add_activity_to_feed,
                feed_type=settings.STREAM_USER_FEED,
                feed_id=self.request.user.id,
                context=context
            )

            # Return the new Activity object instance
            return instance

    def like_feed_item(self, feed_item):
        """
        Add a like to the item (activity or comment) in feed.
        """
        if self.request.user.is_authenticated:
            # Add to list of users who have liked
            feed_item.liked_by.add(self.request.user)

            # Queue task to update likes on feed item
            liked_by = [ u.id for u in feed_item.liked_by.all() ]
            likes_count = feed_item.liked_by.count()
            get_queue_backend().delay(
                nc_tasks.update_activity_in_feed,
                activity_id=feed_item.activity_id,
                set={
                    'liked_by': liked_by,
                    'likes_count': likes_count,
                }
            )

    def unlike_feed_item(self, feed_item):
        """
        Remove a like on the item (activity or comment) in feed.
        """
        if self.request.user.is_authenticated:
            # Remove from list of users who have liked
            feed_item.liked_by.remove(self.request.user)

            # Queue task to update likes on feed item
            liked_by = [ u.id for u in feed_item.liked_by.all() ]
            likes_count = feed_item.liked_by.count()
            get_queue_backend().delay(
                nc_tasks.update_activity_in_feed,
                activity_id=feed_item.activity_id,
                set={
                    'liked_by': liked_by,
                    'likes_count': likes_count,
                }
            )

    def reward_feed_item(self, feed_item, kwargs):
        """
        Add an reward to the item (activity or comment) in feed.

        NOTE: reward creation happens elsewhere in RewardCreateForm.
        """
        if self.request.user.is_authenticated:
            # Create the reward instance with the context
            instance = Reward.objects.create(**kwargs)

            # Queue task to update rewards on feed item
            rewarded_by = [ u.id for u in feed_item.rewarded_by.all() ]
            rewards_total = feed_item.rewards.aggregate(Sum('xlm_value'))
            get_queue_backend().delay(
                nc_tasks.update_activity_in_feed,
                activity_id=feed_item.activity_id,
                set={
                    'rewarded_by': rewarded_by,
                    'rewards_total': rewards_total,
                }
            )

            # Return the new Reward object instance
            return instance

    def add_comment_to_activity(self, activity, context):
        """
        Add comment to an activity in user feed.
        """
        if self.request.user.is_authenticated:
            # Create the new Comment instance for our db
            # NOTE: instance will be updated with stream.activity_id after contact stream with adapter below.
            created_time = context.get('time')
            instance = Comment.objects.create(parent=activity,
                user_id=self.request.user.id, created=created_time)

            # Update the context to include foreign_id as instance.id
            context['foreign_id'] = instance.id

            # Queue task to add comment to activity feed
            get_queue_backend().delay(
                nc_tasks.add_activity_to_feed,
                feed_type=settings.STREAM_ACTIVITY_FEED,
                feed_id=activity.id,
                context=context
            )

            # Queue task to update comments on activity within user feed
            commented_by = [ u.id for u in activity.commented_by.all() ]
            comments_count = activity.commented_by.count()
            get_queue_backend().delay(
                nc_tasks.update_activity_in_feed,
                activity_id=activity.activity_id,
                set={
                    'commented_by': commented_by,
                    'comments_count': comments_count,
                }
            )

            # Return the new Comment object instance
            return instance

    def follow_own_feed(self, user):
        """
        Used for initialization of user so they're own activity is
        in timeline activity feed.
        """
        get_queue_backend().delay(
            nc_tasks.follow_user_feed,
            follower_id=user.id,
            user_id=user.id
        )

    def follow_user(self, user):
        """
        Follow user's feed.
        """
        if self.request.user.is_authenticated:
            get_queue_backend().delay(
                nc_tasks.follow_user_feed,
                follower_id=self.request.user.id,
                user_id=user.id
            )

    def unfollow_user(self, user):
        """
        Unfollow user's feed.
        """
        if self.request.user.is_authenticated:
            get_queue_backend().delay(
                nc_tasks.unfollow_user_feed,
                follower_id=self.request.user.id,
                user_id=user.id
            )

    def save_user(self, request, user, form):
        """
        Saves a new `User` instance using information provided in the
        signup form.

        Extends to create a profile and portfolio for this new user and
        follows own timeline.
        """
        user = super(AccountAdapter, self).save_user(request, user, form)
        profile = Profile.objects.create(user=user)
        portfolio = Portfolio.objects.create(profile=profile)
        self.follow_own_feed(user)
        return user

    def send_mail(self, template_prefix, email, context):
        """
        Override to queue as a task.
        """
        message = self.render_mail(template_prefix, email, context)
        datatuple = tuple( (msg.subject, msg.body, msg.from_email, msg.to) for msg in [ message ] )

        # Queue task to send email
        get_queue_backend().delay(nc_tasks.send_mail, datatuple=datatuple)

    def send_mail_to_many(self, template_prefix, recipient_list, context):
        """
        Use django.core.mail.send_mass_mail() to bulk email with same
        message to all recipients in recipient_list.

        https://docs.djangoproject.com/en/2.0/topics/email/#send-mass-mail
        """
        # Reformat EmailMessage instances into list of tuples (subject, message, from_email, recipient_list)
        msgs = self.render_mail_to_many(template_prefix, recipient_list, context)
        datatuple = tuple( (msg.subject, msg.body, msg.from_email, msg.to) for msg in msgs )

        # Queue task to send emails
        get_queue_backend().delay(nc_tasks.send_mail, datatuple=datatuple)

    def render_mail_to_many(self, template_prefix, recipient_list, context):
        """
        Extends allauth adapter.render_mail to account for multiple recipients.

        Returns iterable of email messages to be sent out.

        See: https://github.com/pennersr/django-allauth/blob/master/allauth/account/adapter.py
        """
        msgs = [
            self.render_mail(template_prefix, recipient, context)
            for recipient in recipient_list
        ]
        return msgs

    def send_bulk_mail(self, template_prefix, recipient_context_list):
        """
        Use django.core.mail.send_mass_mail() to bulk email with different
        messages for each recipient in recipient_context_list.

        recipient_context_list is of form [ (recipient, context) ]
        """
        # Reformat EmailMessage instances into list of tuples (subject, message, from_email, recipient_list)
        msgs = self.render_bulk_mail(template_prefix, recipient_context_list)
        datatuple = tuple( (msg.subject, msg.body, msg.from_email, msg.to) for msg in msgs )

        # Queue task to send emails
        get_queue_backend().delay(nc_tasks.send_mail, datatuple=datatuple)

    def render_bulk_mail(self, template_prefix, recipient_context_list):
        """
        Extends allauth adapter.render_mail to account for multiple recipients
        with different context for each recipient.

        Returns iterable of email messages to be sent out.

        See: https://github.com/pennersr/django-allauth/blob/master/allauth/account/adapter.py
        """
        msgs = [
            self.render_mail(template_prefix, recipient, context)
            for recipient, context in recipient_context_list
        ]
        return msgs
