from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone

from nc.models import Asset
from nc.views import AssetIngestUpdateView


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        For each asset in our db, update details using toml files.
        """
        asset_ingest_view = AssetIngestUpdateView()

        # Keep track of the time cron job takes for performance reasons
        cron_start = timezone.now()

        # For all assets in db,refresh attributes from toml
        asset_ingest_view._ingest_assets_from_horizon()

        # Print out length of time cron took
        cron_duration = timezone.now() - cron_start
        print 'Asset ingest update cron job took {0} seconds'.format(
            cron_duration.total_seconds()
        )
