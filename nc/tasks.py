from __future__ import absolute_import, unicode_literals

from allauth.account.adapter import get_adapter

from django.core.mail import send_mass_mail

from celery import shared_task

from stream_django.client import stream_client
from stream_django.feed_manager import feed_manager

from .models import Activity, Comment


@shared_task
def send_mail(datatuple):
    """
    Task to send emails.
    """
    send_mass_mail(datatuple)

@shared_task
def add_activity_to_feed(feed_type, feed_id, context):
    """
    Task to add activity to feed.
    """
    feed = feed_manager.get_feed(feed_type, feed_id)
    print context
    resp = feed.add_activity(context)
    inv_verb_choices = { v: k for k, v in dict(Activity.VERB_CHOICES).iteritems() }
    verb = inv_verb_choices.get(resp.get('verb', ''), -1)
    if verb != -1:
        model_cls = Activity if verb != Activity.COMMENT else Comment
        model_cls.objects.update_from_stream_response(resp)

@shared_task
def update_activity_in_feed(activity_id, set={}, unset=[]):
    """
    Update an activity in feed.
    """
    stream_client.activity_partial_update(id=activity_id, set=set, unset=unset)

@shared_task
def follow_user_feed(follower_id, user_id):
    """
    Task to follow a user feed.
    """
    feed_manager.follow_user(follower_id, user_id)

@shared_task
def unfollow_user_feed(follower_id, user_id):
    """
    Task to unfollow a user feed.
    """
    feed_manager.unfollow_user(follower_id, user_id)
