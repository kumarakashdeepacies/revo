import logging

from django.contrib.auth import get_user_model
from django.core.management import execute_from_command_line

from config.settings.base import env


def migrate_tenant():
    migration_arguements = ["manage.py", "migrate"]
    execute_from_command_line(migration_arguements)
    return True


def run_custom_command(command, mode="user", role="User"):
    if command:
        from kore_investment.users.models import Instance

        tenant_object = Instance.objects.get(name=command)
        User = get_user_model()
        is_developer = False

        if command not in ["public", "platform_admin"]:
            if mode == "user":
                first_username = f'{env("DJANGO_SUPERUSER_USERNAME", default="revolutio_admin")}.{command}'
                second_username = f"revolutio_admin2.{command}"
                is_developer = True
            elif mode == "tenant_admin":
                first_username = f"tenant_admin1.{command}"
                second_username = f"tenant_admin2.{command}"
            else:
                first_username = f"platform_admin1"
                second_username = f"platform_admin2"
        else:
            if mode == "user":
                first_username = f'{env("DJANGO_SUPERUSER_USERNAME", default="revolutio_admin")}'
                second_username = f"revolutio_admin2"
                is_developer = True
            elif mode == "tenant_admin":
                first_username = f"tenant_admin1"
                second_username = f"tenant_admin2"
            else:
                first_username = f"platform_admin1"
                second_username = f"platform_admin2"

        User.objects.create_user(
            username=first_username,
            email=env("DJANGO_SUPERUSER_EMAIL", default="contact@acies.holdings"),
            password=env("DJANGO_SUPERUSER_PASSWORD", default="Revadmin@2023"),
            is_staff=True,
            is_active=True,
            is_superuser=True,
            is_developer=is_developer,
            instance=tenant_object,
            role=role,
        )
        User.objects.create_user(
            username=second_username,
            email=env("DJANGO_SUPERUSER_EMAIL", default="contact@acies.holdings"),
            password=env("DJANGO_SUPERUSER_PASSWORD", default="Revadmin@2023"),
            is_staff=True,
            is_active=True,
            is_superuser=True,
            is_developer=is_developer,
            instance=tenant_object,
            role=role,
        )
    else:
        logging.error("No Custom Command Passed")
    return True
