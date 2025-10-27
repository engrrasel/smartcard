from django.apps import AppConfig

class AppAccountConfig(AppConfig):
    name = 'app_accounts'

    def ready(self):
        import app_accounts.signals
