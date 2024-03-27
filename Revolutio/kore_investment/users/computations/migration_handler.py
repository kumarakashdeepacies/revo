from django.core.management import execute_from_command_line


def central_db_migration_handler(schema="public"):
    migration_arguments = ["manage.py", "migrate"]
    execute_from_command_line(migration_arguments)
    return True
