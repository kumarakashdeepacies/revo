from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "kore_investment.users"
    verbose_name = _("Users")

    def ready(self):
        # import kore_investment.users.signals  # noqa F401
        from kore_investment.users.queue_manager import start_queues

        start_queues()
        import kore_investment.users.scheduler as schedulerfunc

        if settings.SCHEDULER_AUTOSTART:
            schedulerfunc.start()
