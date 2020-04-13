from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "aws_ecs_deploy.users"
    verbose_name = _("Users")

    def ready(self):
        try:
            import aws_ecs_deploy.users.signals  # noqa F401
        except ImportError:
            pass
