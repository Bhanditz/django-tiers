from datetime import timedelta
from functools import wraps

from django.utils import timezone
from django.db import models

from .app_settings import TIERS_ORGANIZATION_MODEL

from dateutil.relativedelta import relativedelta
from model_utils.models import TimeStampedModel
from model_utils import Choices


def set_default_expiration():
    timezone.now() + timedelta(days=30)


def check_if_exempt(f):
    @wraps(f)
    def wrapper(self):
        if self.tier_enforcement_exempt:
            return False
        return f(self)
    return wrapper


class Tier(TimeStampedModel):
    TIERS = Choices(
        ('trial', 'TRIAL', 'Trial'),  # Expires in 30 days
    )

    name = models.CharField(
        max_length=255,
        choices=TIERS,
        default=TIERS.TRIAL)
    organization = models.OneToOneField(TIERS_ORGANIZATION_MODEL, related_name='tier')
    tier_enforcement_exempt = models.BooleanField(default=False)
    tier_enforcement_grace_period = models.PositiveIntegerField(default=14)
    tier_expires_at = models.DateTimeField(
        default=set_default_expiration)

    def __unicode__(self):
        return u"{0} - {1}".format(self.organization.name, self.name)

    @check_if_exempt
    def has_tier_expired(self):
        """Helper function that checks whether a tier has expired"""
        return timezone.now() > self.tier_expires_at

    @check_if_exempt
    def has_tier_grace_period_expired(self):
        """Helper function that checks whether a tier's grace period has expired"""
        return (timezone.now() >
               (self.tier_expires_at + timedelta(days=self.tier_enforcement_grace_period)))

    @check_if_exempt
    def time_til_tier_expires(self):
        """Pretty prints time left til expiration"""
        rd = relativedelta(self.tier_expires_at, timezone.now())
        if abs(rd.days) != 0:
            return "{0} days and {1} hours".format(abs(rd.days), abs(rd.hours))
        else:
            return "{0} hours".format(abs(rd.hours))

