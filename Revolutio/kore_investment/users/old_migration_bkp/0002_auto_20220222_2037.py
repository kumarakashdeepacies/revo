# Generated by Django 3.2.11 on 2022-02-22 15:07

import datetime

from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="flow_monitor_error_log",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("table_name", models.CharField(max_length=255, null=True)),
                ("transaction_id_data", models.CharField(max_length=255, null=True)),
                ("error_dic", models.TextField(null=True)),
                ("error_description", models.TextField(null=True)),
                ("flow", models.TextField(null=True)),
                ("element_id", models.CharField(max_length=255, null=True)),
                ("subprocess", models.CharField(max_length=255, null=True)),
                ("process", models.CharField(max_length=255, null=True)),
                ("app_code", models.CharField(max_length=255, null=True)),
                ("created_by", models.CharField(max_length=100)),
                ("created_date", models.DateTimeField(auto_now=True)),
                ("modified_by", models.CharField(max_length=100, null=True)),
                ("modified_date", models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="user_navbar",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("user_name", models.CharField(max_length=255, null=True)),
                ("app_code", models.CharField(max_length=255, null=True)),
                ("tenant", models.CharField(max_length=255, null=True)),
                ("navbar_list", models.TextField(null=True)),
                ("build_process_type", models.CharField(max_length=255, null=True)),
                ("created_by", models.CharField(max_length=100, verbose_name="Created by")),
                ("created_date", models.DateTimeField(auto_now=True, verbose_name="Created date")),
                ("modified_by", models.CharField(max_length=100, null=True, verbose_name="Modified by")),
                (
                    "modified_date",
                    models.DateTimeField(auto_now=True, null=True, verbose_name="Modified date"),
                ),
            ],
        ),
        migrations.AddField(
            model_name="computation_model_flowchart",
            name="output_elements",
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name="profile",
            name="date_joined",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(2022, 2, 22, 15, 7, 13, 388730, tzinfo=utc),
                null=True,
                verbose_name="date joined",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="first_name",
            field=models.CharField(blank=True, max_length=150, verbose_name="first name"),
        ),
        migrations.AlterField(
            model_name="userpermission_interim",
            name="permission_level1",
            field=models.TextField(null=True, verbose_name="Permission level1"),
        ),
        migrations.AlterField(
            model_name="userpermission_interim",
            name="permission_name",
            field=models.TextField(null=True, verbose_name="Permission name"),
        ),
        migrations.AlterField(
            model_name="userpermission_master",
            name="permission_name",
            field=models.TextField(null=True, verbose_name="Permission name"),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="date_joined",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(2022, 2, 22, 15, 7, 13, 412848, tzinfo=utc),
                null=True,
                verbose_name="date joined",
            ),
        ),
    ]