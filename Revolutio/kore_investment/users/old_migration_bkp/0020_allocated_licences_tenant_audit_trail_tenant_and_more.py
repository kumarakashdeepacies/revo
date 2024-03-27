# Generated by Django 4.0.7 on 2023-04-05 15:45

import datetime

from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        (
            "users",
            "0019_rename_category_subelement_attributes_category_subelement_category_subelement_attributes_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="allocated_licences",
            name="tenant",
            field=models.CharField(default="public", max_length=255),
        ),
        migrations.AddField(
            model_name="audit_trail",
            name="tenant",
            field=models.CharField(default="public", max_length=255),
        ),
        migrations.AddField(
            model_name="configuration_parameter",
            name="tenant",
            field=models.CharField(default="public", max_length=255),
        ),
        migrations.AddField(
            model_name="dashboard_config",
            name="tenant",
            field=models.CharField(default="public", max_length=255),
        ),
        migrations.AddField(
            model_name="group_details",
            name="tenant",
            field=models.CharField(default="public", max_length=255),
        ),
        migrations.AddField(
            model_name="login_trail",
            name="tenant",
            field=models.CharField(default="public", max_length=255),
        ),
        migrations.AddField(
            model_name="permissionaccess",
            name="tenant",
            field=models.CharField(default="public", max_length=255),
        ),
        migrations.AddField(
            model_name="profile",
            name="tenant",
            field=models.CharField(default="public", max_length=255),
        ),
        migrations.AddField(
            model_name="user_approval",
            name="tenant",
            field=models.CharField(default="public", max_length=255),
        ),
        migrations.AddField(
            model_name="user_model",
            name="tenant",
            field=models.CharField(default="public", max_length=255),
        ),
        migrations.AddField(
            model_name="usergroup_approval",
            name="tenant",
            field=models.CharField(default="public", max_length=255),
        ),
        migrations.AddField(
            model_name="userpermission_interim",
            name="tenant",
            field=models.CharField(default="public", max_length=255),
        ),
        migrations.AddField(
            model_name="userpermission_master",
            name="tenant",
            field=models.CharField(default="public", max_length=255),
        ),
        migrations.AlterField(
            model_name="profile",
            name="date_joined",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(2023, 4, 5, 15, 44, 59, 555033, tzinfo=utc),
                null=True,
                verbose_name="date joined",
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="date_joined",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(2023, 4, 5, 15, 44, 59, 575443, tzinfo=utc),
                null=True,
                verbose_name="date joined",
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="first_name",
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="last_name",
            field=models.CharField(max_length=30, null=True),
        ),
    ]
