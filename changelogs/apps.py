from django.apps import AppConfig


class ChangelogsConfig(AppConfig):
    name = "changelogs"

    def ready(self):
        import changelogs.signals
