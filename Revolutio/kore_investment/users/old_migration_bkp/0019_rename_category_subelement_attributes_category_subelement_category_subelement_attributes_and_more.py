# Generated by Django 4.0.7 on 2023-03-29 06:48

import datetime

from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0018_profile_tagged_user_alter_audit_operation_message_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="category_subelement",
            old_name="Category_Subelement_Attributes",
            new_name="category_subelement_attributes",
        ),
        migrations.RenameField(
            model_name="category_subelement",
            old_name="Category_Subelement_Name",
            new_name="category_subelement_name",
        ),
        migrations.RenameField(
            model_name="category_subelement",
            old_name="Category_Subelement_Type",
            new_name="category_subelement_type",
        ),
        migrations.RenameField(
            model_name="category_subelement",
            old_name="Dependency",
            new_name="dependency",
        ),
        migrations.RenameField(
            model_name="category_subelement",
            old_name="Description",
            new_name="description",
        ),
        migrations.RenameField(
            model_name="category_subelement",
            old_name="Image",
            new_name="image",
        ),
        migrations.RenameField(
            model_name="category_subelement_attributes",
            old_name="Category_Subelement_Attributes",
            new_name="category_subelement_attributes",
        ),
        migrations.RenameField(
            model_name="category_subelement_attributes",
            old_name="Choice",
            new_name="choice",
        ),
        migrations.RenameField(
            model_name="category_subelement_attributes",
            old_name="Choice_Type",
            new_name="choice_type",
        ),
        migrations.RenameField(
            model_name="category_subelement_attributes",
            old_name="Corresponding_HTML_element",
            new_name="corresponding_html_element",
        ),
        migrations.RenameField(
            model_name="category_subelement_attributes",
            old_name="Style_Applicable",
            new_name="style_applicable",
        ),
        migrations.RenameField(
            model_name="profile",
            old_name="Bio",
            new_name="bio",
        ),
        migrations.RenameField(
            model_name="profile",
            old_name="First_name",
            new_name="first_name",
        ),
        migrations.RenameField(
            model_name="profile",
            old_name="Last_name",
            new_name="last_name",
        ),
        migrations.RenameField(
            model_name="profile",
            old_name="Location",
            new_name="location",
        ),
        migrations.RenameField(
            model_name="templates",
            old_name="Category_Attributes",
            new_name="category_attributes",
        ),
        migrations.RenameField(
            model_name="templates",
            old_name="Category_Name",
            new_name="category_name",
        ),
        migrations.RenameField(
            model_name="templates",
            old_name="Category_Subelements",
            new_name="category_subelements",
        ),
        migrations.RenameField(
            model_name="templates",
            old_name="Category_Type",
            new_name="category_type",
        ),
        migrations.RenameField(
            model_name="templates",
            old_name="Description",
            new_name="description",
        ),
        migrations.RenameField(
            model_name="templates",
            old_name="Image",
            new_name="image",
        ),
        migrations.RenameField(
            model_name="userprofile",
            old_name="Bio",
            new_name="bio",
        ),
        migrations.RenameField(
            model_name="userprofile",
            old_name="First_name",
            new_name="first_name",
        ),
        migrations.RenameField(
            model_name="userprofile",
            old_name="Last_name",
            new_name="last_name",
        ),
        migrations.RenameField(
            model_name="userprofile",
            old_name="Location",
            new_name="location",
        ),
    ]
