from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'
    verbose_name = 'CCStore'

    def ready(self):
        import apps.core.signals.handlers  # noqa
