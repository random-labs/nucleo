from allauth.account.adapter import DefaultAccountAdapter

from django.conf import settings
from django.core.mail import send_mass_mail

from . import tasks as nc_tasks
from .models import Asset, Portfolio, Profile
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
        # Queue task to add activity to user feed
        if self.request.user.is_authenticated:
            get_queue_backend().delay(
                nc_tasks.add_activity_to_feed,
                feed_type=settings.STREAM_USER_FEED,
                feed_id=self.request.user.id,
                context=context
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

        Extends to create a profile and portfolio for this new user and to note
        that XLM is always a trusted asset.
        """
        user = super(AccountAdapter, self).save_user(request, user, form)
        profile = Profile.objects.create(user=user)
        portfolio = Portfolio.objects.create(profile=profile)
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
        Use django.core.mail.send_mass_mail() to bulk email.

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
