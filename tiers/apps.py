from django.apps import AppConfig


class TiersConfig(AppConfig):
    name = 'tiers'
    label = 'tiers'

    def ready(self):
        from tiers import models

