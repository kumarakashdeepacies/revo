# Generated by Django 4.0.7 on 2022-11-17 06:59

import datetime

from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0014_login_trail_alter_profile_date_joined_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="audit_trail",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("session_id", models.CharField(max_length=255, null=True)),
                ("ip", models.CharField(max_length=255, null=True)),
                ("user_name", models.CharField(max_length=255, null=True)),
                ("app_code", models.CharField(max_length=255, null=True)),
                ("url_current", models.CharField(max_length=255, null=True)),
                ("url_from", models.CharField(max_length=255, null=True)),
                ("screen", models.CharField(max_length=255, null=True)),
                ("logged_date", models.DateField(null=True)),
                ("logged_time", models.TimeField(null=True)),
                ("time_spent", models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name="profile",
            name="date_joined",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(2022, 11, 17, 6, 59, 29, 644257, tzinfo=utc),
                null=True,
                verbose_name="date joined",
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="date_joined",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(2022, 11, 17, 6, 59, 29, 664620, tzinfo=utc),
                null=True,
                verbose_name="date joined",
            ),
        ),
    ]
