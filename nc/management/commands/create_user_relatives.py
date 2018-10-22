from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Count

from nc.models import Portfolio, Profile
from nc.tasks import follow_user_feed

from stream_django.feed_manager import feed_manager


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Management command to ensure each user object has
        an associated profile, portfolio instance, is
        following his/her own activity feed for proper timeline,
        and has a default account to receive awards.
        """
        # NOTE: Expensive but necessary. Not using bulk_create to ensure that
        # search indices are also updated
        created_profile = 0
        for u in get_user_model().objects.filter(profile=None):
            p = Profile.objects.create(user=u)
            if p:
                created_profile += 1

        created_portfolio = 0
        for p in Profile.objects.filter(portfolio=None):
            port = Portfolio.objects.create(profile=p)
            if port:
                created_portfolio += 1

        # NOTE: only include this if necessary, otherwise
        # stream.exceptions.RateLimitReached likely to be thrown
        # created_self_feed_follows = 0
        # for u in get_user_model().objects.all():
        #     feed_manager.follow_user(u.id, u.id)
        #     created_self_feed_follows += 1

        created_award_default = 0
        for p in Profile.objects.filter(default_award_account=None)\
            .annotate(num_accounts=Count('user__accounts'))\
            .exclude(num_accounts=0):
            # Save first account as award default
            p.default_award_account = p.user.accounts.first()
            p.save()
            created_award_default += 1

        print 'Created {0} profiles, {1} portfolios, {2} award account defaults'.format(
            created_profile, created_portfolio, created_award_default
        )
