from __future__ import absolute_import, unicode_literals

from allauth.account.adapter import get_adapter

from django.core.mail import send_mass_mail

from celery import shared_task

from stream_django.feed_manager import feed_manager


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
    feed.add_activity(context)

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
