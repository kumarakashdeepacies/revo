# Generated by Django 4.0.10 on 2023-06-20 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0022_external_application_master_external_app_ui_config_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user_approval",
            name="is_developer",
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name="Developer"),
        ),
    ]