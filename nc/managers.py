import pytz

from algoliasearch_django import update_records

from django.db import models
from django.utils.dateparse import parse_datetime


class ActivityManager(models.Manager):
    def create_from_stream_response(self, resp):
        """
        Create an activity instance from the response of
        stream_feed.add_activity().
        """
        inv_verb_choices = { v: k for k, v in dict(self.model.VERB_CHOICES).iteritems() }
        verb = inv_verb_choices.get(resp.get('verb'))
        user_id = int(resp.get('actor'))
        activity_id = resp.get('id')
        tx_hash = resp.get('tx_hash')
        created = pytz.timezone("UTC").localize(parse_datetime(resp.get('time')), is_dst=None) # NOTE: resp['time'] is in UTC but stream stores as timezone unaware
        return self.create(verb=verb, user_id=user_id,
            activity_id=activity_id, tx_hash=tx_hash, created=created)

    def update_from_stream_response(self, resp):
        """
        Update an activity instance from the response of
        stream_feed.add_activity().

        resp['foreign_id'] will be the instance.id of the Activity looking
        to update.
        """
        id = int(resp.get('foreign_id'))
        activity_id = resp.get('id')
        return self.filter(id=id).update(activity_id=activity_id)


class AssetManager(models.Manager):
    def bulk_create(self, objs, batch_size=None):
        """
        Set asset_id field to each given Asset instance in objs since
        the pre_save signal won't be fired on bulk_create.
        """
        # Bulk create with cleaned asset instances
        for asset in objs:
            issuer = asset.issuer_address if asset.issuer_address else 'native'
            asset.asset_id = '{0}-{1}'.format(asset.code, issuer)
        created = super(AssetManager, self).bulk_create(objs, batch_size)

        # TODO: Figure out how to bulk create search index records. Until then,
        # rely on issuer editing asset page for asset pic/banner/color/verified
        # (good so in search only getting issuers Nucleo knows that have assets)

        # Return created assets
        return created


class CommentManager(models.Manager):
    def create_from_stream_response(self, resp):
        """
        Create a comment instance from the response of
        stream_feed.add_activity().
        """
        parent_id = int(resp.get('object')) # NOTE: object is the id of parent activity user commented on
        activity_id = resp.get('id')
        user_id = int(resp.get('actor')) # NOTE: actor is the user making the comment
        created = pytz.timezone("UTC").localize(parse_datetime(resp.get('time')), is_dst=None) # NOTE: resp['time'] is in UTC but stream stores as timezone unaware
        return self.create(parent_id=parent_id, activity_id=activity_id,
            user_id=user_id, created=created)

    def update_from_stream_response(self, resp):
        """
        Update a comment instance from the response of
        stream_feed.add_activity().

        resp['foreign_id'] will be the instance.id of the Comment looking
        to update.
        """
        id = int(resp.get('foreign_id'))
        activity_id = resp.get('id')
        return self.filter(id=id).update(activity_id=activity_id)
