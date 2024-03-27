import os
import sys

from django.core.management import execute_from_command_line
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
        current_path = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(os.path.join(current_path, "kore_investment"))
        migration_arguements = ["manage.py", "migrate"]
        execute_from_command_line(migration_arguements)
