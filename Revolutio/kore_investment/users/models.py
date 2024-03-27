from django import template
from django.contrib.auth.models import AbstractUser
import django.core.validators
from django.db import models
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

register = template.Library()
from datetime import datetime
import json
import os
import re

# Used to Auto Detect Local Timezone
from django.db.models.fields import DateField
from django_multitenant.mixins import TenantModelMixin
from django_multitenant.models import TenantModel
import pycountry

from config.settings.base import PLATFORM_DATA_PATH

directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + r"\media"


class Instance(TenantModel):
    name = models.CharField(max_length=50, unique=True)
    subdomain = models.CharField(max_length=50, null=True)
    tenant_id = "id"

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "id",
                ]
            ),
            models.Index(
                fields=[
                    "name",
                ]
            ),
        ]


class User(TenantModelMixin, AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = CharField(
        _("Name of User"),
        blank=True,
        max_length=255,
    )
    last_password_update_date = DateField(default=datetime.now, blank=False)
    password_history = models.TextField(blank=False, default="[]")
    is_developer = models.BooleanField(default=False)
    mfa_hash = models.CharField(max_length=50, null=True, blank=True)
    from_ldap = models.BooleanField(verbose_name="LDAP user", editable=False, default=False)
    department = models.CharField(max_length=256, null=True, blank=True)
    job_title = models.CharField(max_length=30, blank=True)
    contact_number = models.CharField(max_length=10, blank=True)
    location = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=20, default="User", blank=True)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    @property
    def tenant_field(self):
        return "instance_id"

    class Meta:
        unique_together = [("username", "instance")]
        indexes = [
            models.Index(
                fields=[
                    "instance",
                ]
            ),
            models.Index(
                fields=[
                    "username",
                ]
            ),
        ]


class UserPermission_Master(TenantModel):
    id = models.AutoField(primary_key=True, verbose_name="Id")
    usergroup = models.CharField(null=True, max_length=256, verbose_name="User group")
    accesschoices = [("Navbar", "Navbar"), ("Data hierarchy", "Data hierarchy")]
    permission_type = models.CharField(
        null=True, max_length=256, choices=accesschoices, verbose_name="Permission type"
    )
    accesschoices1 = [
        ("0", "Process"),
        ("1", "Sub-process"),
        ("2", "Category"),
        ("3", "Category Button Access"),
    ]
    permission_level = models.CharField(
        null=True, max_length=256, choices=accesschoices1, verbose_name="Permission level"
    )
    level_button_access = models.TextField(null=True)
    permission_name = models.TextField(null=True, verbose_name="Permission name")
    application = models.CharField(null=True, max_length=256)
    application_dev = models.CharField(null=True, max_length=256)
    app_code = models.CharField(null=True, max_length=256)
    app_name = models.CharField(null=True, max_length=256)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    tenant_id = "instance_id"

    def __str__(self):
        return self.permission_name

    def get_absolute_url(self):
        return reverse("users:user_management")

    @property
    def tenant_field(self):
        return "instance_id"

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "instance",
                ]
            ),
        ]


class Profile(TenantModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    job_title = models.CharField(max_length=30, blank=True)
    contact_number = models.CharField(max_length=10, blank=True)
    bio = models.CharField(max_length=1000, blank=True)
    location = models.CharField(max_length=30, blank=True)
    profile_pic = models.ImageField(
        upload_to="users/profile_pics",
        blank=True,
        verbose_name="Profile photo (Note - Upload only jpg/png file)",
    )
    cover_photo = models.ImageField(
        upload_to="users/cover_photos",
        blank=True,
        verbose_name="Cover photo (Note - Upload only jpg/png file)",
    )
    date_joined = models.DateTimeField(
        verbose_name="date joined",
        unique=False,
        null=True,
        blank=True,
    )
    last_login = models.DateTimeField(null=True, verbose_name="last login", blank=True)
    username = models.CharField(
        unique=False,
        null=True,
        db_index=True,
        verbose_name="username",
        validators=[
            django.core.validators.RegexValidator(
                re.compile("^[\\w.@+-]+$", 152), "Enter a valid username.", "invalid"
            )
        ],
        help_text="Required. 150 characters or fewer. Letters, numbers and @/./+/-/_ characters",
        max_length=150,
    )
    email = models.EmailField(unique=False, null=True, max_length=254, verbose_name="email")
    is_superuser = models.BooleanField(
        default=False,
        help_text="Designates that this user has all permissions without explicitly assigning them.",
        verbose_name="superuser status",
    )
    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into this admin site.",
        verbose_name="staff status",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
        verbose_name="active",
    )
    linkedin = models.CharField(max_length=150, null=True, blank=True)
    twitter = models.CharField(max_length=150, null=True, blank=True)
    facebook = models.CharField(max_length=150, null=True, blank=True)
    github = models.CharField(max_length=150, null=True, blank=True)
    no_of_alert = models.IntegerField(null=True)
    department = models.CharField(max_length=150, null=True, blank=True)
    tagged_user = models.CharField(null=True, blank=True, max_length=30)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    tenant_id = "instance_id"

    @property
    def tenant_field(self):
        return "instance_id"

    class Meta:
        unique_together = [("username", "instance")]
        indexes = [
            models.Index(
                fields=[
                    "instance",
                ]
            ),
        ]


class permissionaccess(TenantModel):
    userid = models.IntegerField(default=0, verbose_name="UserId")
    username = models.CharField(max_length=255, null=True)
    firstname = models.CharField(max_length=255, null=True)
    lastname = models.CharField(max_length=255, null=True)
    emailid = models.CharField(max_length=255, null=True)
    permission_level = models.IntegerField(default=0, verbose_name="UserId")
    permission_name = models.CharField(max_length=255, null=True)
    requested_permission = models.CharField(max_length=255, null=True)
    approved_by = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=255, null=True)
    permission_type = models.CharField(max_length=255, null=True)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    tenant_id = "instance_id"

    @property
    def tenant_field(self):
        return "instance_id"

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "instance",
                ]
            ),
        ]


class usergroup_approval(TenantModel):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(default=0, verbose_name="User Id")
    group_id = models.IntegerField(default=0, verbose_name="Group Id")
    approval_status = models.CharField(max_length=255, null=True)
    user_name = models.CharField(max_length=255, null=True)
    group_name = models.CharField(max_length=255, null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    tenant_id = "instance_id"

    @property
    def tenant_field(self):
        return "instance_id"

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "instance",
                ]
            ),
        ]


class user_approval(TenantModel):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, null=True)
    password = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=255, null=True)
    approval_status = models.CharField(max_length=255, null=True)
    authentication_type = models.CharField(max_length=255, null=True)
    action_requested = models.CharField(max_length=255, null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)
    is_developer = models.BooleanField(verbose_name="Developer", null=True, blank=True, default=False)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    tenant_id = "instance_id"

    @property
    def tenant_field(self):
        return "instance_id"

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "instance",
                ]
            ),
        ]


class allocated_licences(TenantModel):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, null=True)
    authentication_type = models.CharField(max_length=255, null=True)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    tenant_id = "instance_id"

    @property
    def tenant_field(self):
        return "instance_id"

    class Meta:
        unique_together = [("username", "instance")]
        indexes = [
            models.Index(
                fields=[
                    "instance",
                ]
            ),
        ]


class user_model(TenantModel):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, null=True)
    password = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=255, null=True)
    ldap_login = models.BooleanField(verbose_name="LDAP-login")
    application_login = models.BooleanField(verbose_name="Application-login")
    is_developer = models.BooleanField(verbose_name="Developer", null=True, blank=True, default=False)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    tenant_id = "instance_id"

    @property
    def tenant_field(self):
        return "instance_id"

    class Meta:
        unique_together = [("username", "instance")]
        indexes = [
            models.Index(
                fields=[
                    "instance",
                ]
            ),
        ]


class configuration_parameter(TenantModel):
    id = models.AutoField(primary_key=True)
    parameter = models.CharField(max_length=255, null=True)
    value = models.TextField(null=True)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    tenant_id = "instance_id"

    @property
    def tenant_field(self):
        return "instance_id"

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "instance",
                ]
            ),
        ]


class userpermission_interim(TenantModel):
    id = models.AutoField(primary_key=True, verbose_name="Id")
    usergroup = models.CharField(null=True, max_length=256, verbose_name="User group")
    permission_type = models.CharField(null=True, max_length=256, verbose_name="Permission type")
    permission_level = models.CharField(null=True, max_length=256, verbose_name="Permission level")
    permission_name = models.TextField(null=True, verbose_name="Permission name")
    level_button_access = models.TextField(null=True)
    permission_level1 = models.TextField(null=True, verbose_name="Permission level1")
    approval_status = models.CharField(null=True, max_length=256, verbose_name="Approval Status")
    application = models.CharField(null=True, max_length=256)
    application_dev = models.CharField(null=True, max_length=256)
    app_code = models.CharField(null=True, max_length=256)
    app_name = models.CharField(null=True, max_length=256)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    tenant_id = "instance_id"

    @property
    def tenant_field(self):
        return "instance_id"

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "instance",
                ]
            ),
        ]


class group_details(TenantModel):
    id = models.AutoField(primary_key=True, verbose_name="Id")
    name = models.CharField(null=True, max_length=256, verbose_name="Name")
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    tenant_id = "instance_id"

    @property
    def tenant_field(self):
        return "instance_id"

    class Meta:
        unique_together = [("name", "instance")]
        indexes = [
            models.Index(
                fields=[
                    "instance",
                ]
            ),
        ]


class user_navbar(TenantModel):
    id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=255, null=True)
    app_code = models.CharField(max_length=255, null=True)
    navbar_list = models.TextField(null=True)
    build_process_type = models.CharField(max_length=255, null=True)
    created_by = models.CharField(max_length=100, verbose_name="Created by")
    created_date = models.DateTimeField(auto_now=True, editable=False, verbose_name="Created date")
    modified_by = models.CharField(max_length=100, null=True, verbose_name="Modified by")
    modified_date = models.DateTimeField(
        auto_now=True, editable=False, null=True, verbose_name="Modified date"
    )
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    tenant_id = "instance_id"

    @property
    def tenant_field(self):
        return "instance_id"

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "instance",
                ]
            ),
            models.Index(
                fields=[
                    "user_name",
                ]
            ),
        ]

    def __str__(self):
        return self.user_name


class failed_login_alerts(TenantModel):
    id = models.AutoField(primary_key=True)
    usergroup = models.CharField(null=True, max_length=256)
    alert_instance = models.CharField(null=True, max_length=256)
    alert_options = models.CharField(null=True, max_length=256)
    app_code = models.CharField(null=True, max_length=256)
    events = models.CharField(null=True, max_length=256)
    approval_status = models.CharField(null=True, max_length=256)
    approval_code = models.CharField(null=True, max_length=256)
    created_by = models.CharField(null=True, max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    tenant_id = "instance_id"

    @property
    def tenant_field(self):
        return "instance_id"

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "instance",
                ]
            ),
        ]

    def __str__(self):
        return self.user_name


class login_trail(TenantModel):
    id = models.AutoField(primary_key=True)
    session_id = models.CharField(max_length=255, null=True, unique=False)
    user_name = models.CharField(max_length=255, null=True, unique=False)
    time_logged_in = models.DateTimeField(auto_now=True, null=True, editable=False)
    time_logged_out = models.DateTimeField(auto_now=False, null=True, editable=False)
    logout_type = models.CharField(max_length=255, null=True, unique=False)
    ip = models.CharField(max_length=255, null=True, unique=False)
    inactivity_time = models.DateTimeField(auto_now=False, null=True, editable=False)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    tenant_id = "instance_id"

    @property
    def tenant_field(self):
        return "instance_id"

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "instance",
                ]
            ),
        ]


class audit_trail(TenantModel):
    id = models.AutoField(primary_key=True)
    session_id = models.CharField(max_length=255, null=True, unique=False)
    ip = models.CharField(max_length=255, null=True, unique=False)
    user_name = models.CharField(max_length=255, null=True, unique=False)
    app_code = models.CharField(max_length=255, null=True, unique=False)
    url_current = models.CharField(max_length=255, null=True, unique=False)
    url_from = models.CharField(max_length=255, null=True, unique=False)
    screen = models.CharField(max_length=255, null=True, unique=False)
    logged_date = models.DateField(null=True)
    logged_time = models.TimeField(null=True)
    time_spent = models.CharField(max_length=255, null=True, unique=False)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    tenant_id = "instance_id"

    @property
    def tenant_field(self):
        return "instance_id"

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "instance",
                ]
            ),
        ]


class notification_management(models.Model):
    id = models.AutoField(primary_key=True)
    notification_message = models.CharField(max_length=526, null=True, blank=True)
    user_name = models.CharField(max_length=30, null=True, blank=True, unique=False)
    category = models.CharField(max_length=30, null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)
    created_date = models.DateTimeField(auto_now=True, null=True, editable=False, verbose_name="Created date")
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    tenant_id = "instance_id"

    @property
    def tenant_field(self):
        return "instance_id"

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "instance",
                ]
            ),
            models.Index(
                fields=[
                    "user_name",
                ]
            ),
        ]


class dashboard_config(models.Model):
    id = models.AutoField(primary_key=True)
    app_code = models.CharField(max_length=255, null=True)
    application_name = models.CharField(max_length=255, null=True)
    subprocess_code = models.CharField(max_length=255, null=True)
    subprocess_name = models.CharField(max_length=255, null=True)
    element_id = models.CharField(max_length=255, null=True)
    config_id = models.CharField(max_length=255, null=True)
    dashboard_type = models.CharField(max_length=255, null=True)
    dashboard_index = models.CharField(max_length=255, null=True)
    dashboard_id = models.CharField(max_length=255, null=True)
    dashboard_config_id = models.CharField(max_length=255, null=True)
    edit_type = models.CharField(max_length=255, null=True)
    tab_id = models.CharField(max_length=255, null=True)
    tab_name = models.CharField(max_length=255, null=True)
    plots_id = models.CharField(max_length=255, null=True)
    plots_name = models.CharField(max_length=255, null=True)
    shared_username = models.CharField(max_length=255, null=True)
    shared_type = models.CharField(max_length=255, null=True)
    subprocess_group = models.CharField(max_length=255, null=True)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    tenant_id = "instance_id"

    @property
    def tenant_field(self):
        return "instance_id"

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "instance",
                ]
            ),
        ]


class applicationAccess(models.Model):
    id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=256, null=False, unique=False)
    app_code = models.CharField(max_length=256, null=False, unique=False)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    tenant_id = "instance_id"

    @property
    def tenant_field(self):
        return "instance_id"

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "instance",
                ]
            ),
            models.Index(
                fields=[
                    "app_code",
                ]
            ),
            models.Index(
                fields=[
                    "user_name",
                ]
            ),
        ]


class CountryMaster(models.Model):
    id = models.AutoField(primary_key=True)
    countrychoices = []
    isocodechoices = []
    country = []
    for i in range(0, len(pycountry.countries)):
        a = list(pycountry.countries)[i].name
        b = list(pycountry.countries)[i].alpha_2
        c = {"country": a, "iso_code": b}
        countrychoices.append((a, a))
        isocodechoices.append((b, b))
    country_name = models.CharField(
        verbose_name="Country",
        max_length=100,
        choices=countrychoices,
        default=countrychoices[104][0],
        unique=True,
    )
    active_from = models.DateField(null=True, blank=True, verbose_name="Active From")
    active_to = models.DateField(null=True, auto_now=False, verbose_name="Active To")
    perpetuity = models.BooleanField(verbose_name="Perpetuity")
    iso_code = models.CharField(
        max_length=100,
        unique=True,
        default=isocodechoices[104][0],
        verbose_name="ISO Code",
    )
    default_name = models.CharField(max_length=100, verbose_name="Default name", null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)
    transaction_id = models.CharField(max_length=300, null=True)

    def __str__(self):
        return self.country_name

    def get_absolute_url(self):
        return reverse("users:countrymasterlist")


class CurrencyMaster(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    currencychoices = []
    for i in range(0, len(pycountry.currencies)):
        a = list(pycountry.currencies)[i].alpha_3
        currencychoices.append((a, a))
    currency_code = models.CharField(max_length=100, choices=currencychoices, verbose_name="Currency code")
    currency_name = models.CharField(max_length=100, unique=True, verbose_name="Currency name")
    defaultcountryid = 1
    country_name = models.ForeignKey(
        CountryMaster,
        db_column="country_name",
        on_delete=models.CASCADE,
        default=defaultcountryid,
        verbose_name="Country",
    )
    default_holiday_calendar = models.CharField(
        max_length=100, verbose_name="Default holiday calendar", null=True
    )
    configuration_date = models.DateField(auto_now=False, editable=True, null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)
    transaction_id = models.CharField(max_length=300, null=True)

    def __str__(self):
        return self.currency_code

    def get_absolute_url(self):
        return reverse("users:currencymasterlist")


class Hierarchy_table(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Id")
    hierarchy_type = models.CharField(max_length=255, verbose_name="Hierarchy Type")
    hierarchy_group = models.CharField(max_length=255, verbose_name="Hierarchy Group")
    hierarchy_name = models.CharField(max_length=255, verbose_name="Hierarchy Name")
    hierarchy_description = models.CharField(max_length=255, null=True, verbose_name="Hierarchy Description")
    hierarchy_parent_name = models.CharField(max_length=255, null=True, verbose_name="Hierarchy Parent Name")
    hierarchy_level = models.IntegerField(default=0, verbose_name="Hierarchy Level")
    hierarchy_level_name = models.CharField(max_length=255, null=True, verbose_name="Hierarchy Level Name")
    configuration_date = models.DateField(auto_now=False, editable=True, null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)
    transaction_id = models.CharField(max_length=300, null=True)


class Hierarchy_levels(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Id")
    hierarchy_level_name = models.CharField(max_length=255, null=True, verbose_name="Hierarchy Level Name")
    configuration_date = models.DateTimeField(auto_now=False, editable=True)
    hierarchy_level = models.IntegerField(default=0, verbose_name="Hierarchy Level")
    hierarchy_type = models.CharField(max_length=255, verbose_name="Hierarchy Type")
    hierarchy_group = models.CharField(max_length=255, verbose_name="Hierarchy Group")
    configuration_date = models.DateField(auto_now=False, editable=True, null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)
    transaction_id = models.CharField(max_length=300, null=True)


class Hierarchy_groups(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Id")
    hierarchy_type = models.CharField(max_length=255, verbose_name="Hierarchy Type")
    hierarchy_group = models.CharField(max_length=255, verbose_name="Hierarchy Group")
    configuration_date = models.DateTimeField(auto_now=False, editable=True, null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)
    transaction_id = models.CharField(max_length=300, null=True)


class UserConfig(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)
    datatablesconfig = models.BinaryField(null=True)
    screen_url = models.CharField(max_length=256, null=True)
    navbarconfig = models.BinaryField(null=True)
    plot_config_home_page = models.BinaryField(null=True)
    analysis_config = models.BinaryField(null=True)
    tab_config_home_page = models.BinaryField(null=True)
    shared_config = models.BinaryField(null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)

    def __str__(self):
        return self.name


class NavigationSideBar(models.Model):
    id = models.AutoField(primary_key=True)
    item_code = models.CharField(max_length=100, null=True, blank=True)
    item_name = models.CharField(max_length=255, null=True, blank=True)
    item_shortname = models.CharField(max_length=10, null=True, blank=True)
    item_group_code = models.CharField(max_length=100, null=True, blank=True)
    item_group_name = models.CharField(max_length=100, null=True, blank=True)
    item_group_shortname = models.CharField(max_length=10, null=True, blank=True)
    hover_option = models.CharField(max_length=3, null=True, blank=True)
    item_level = models.CharField(max_length=100, null=True, blank=True)
    item_popup_config = models.BinaryField(null=True)
    item_url = models.CharField(max_length=256, null=True)
    item_extra_details = models.CharField(max_length=526, null=True)
    related_entity = models.CharField(max_length=255, null=True, blank=True)
    app_allocation_status = models.CharField(max_length=255, null=True, blank=True, default="unallocated")
    share_with_group = models.BinaryField(null=True)
    theme_name = models.CharField(max_length=255, null=True)
    breadcrumbs = models.BinaryField(null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    process_flow_design = models.BinaryField(null=True)
    tab_header_color_config = models.BinaryField(null=True)
    design_mode = models.BooleanField(null=True, default=False, verbose_name="design mode")
    process_icon = models.CharField(max_length=255, null=True, blank=True)
    subprocess_icon = models.CharField(max_length=255, null=True, blank=True)


class ProcessScheduler(models.Model):
    id = models.AutoField(primary_key=True)
    app_code = models.CharField(max_length=50, null=False)
    item_code = models.CharField(max_length=50, null=False)
    item_group_code = models.CharField(max_length=50, null=False)
    element_id = models.CharField(max_length=50, null=True)
    scheduler_type = models.CharField(max_length=20, null=True)
    trigger_option = models.CharField(max_length=20, null=True)
    dependent_block = models.CharField(max_length=50, null=True)
    config = models.BinaryField(null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)


class DraftProcess(models.Model):
    id = models.AutoField(primary_key=True)
    item_code = models.CharField(max_length=100, null=True, blank=True)
    item_name = models.CharField(max_length=255, null=True, blank=True)
    item_shortname = models.CharField(max_length=10, null=True, blank=True)
    item_group_code = models.CharField(max_length=100, null=True, blank=True)
    item_group_name = models.CharField(max_length=100, null=True, blank=True)
    item_group_shortname = models.CharField(max_length=10, null=True, blank=True)
    hover_option = models.CharField(max_length=3, null=True, blank=True)
    item_level = models.CharField(max_length=100, null=True, blank=True)
    item_popup_config = models.BinaryField(null=True)
    item_url = models.CharField(max_length=255, null=True)
    item_extra_details = models.BinaryField(null=True)
    related_entity = models.CharField(max_length=255, null=True, blank=True)
    app_allocation_status = models.CharField(max_length=255, null=True, blank=True)
    share_with_group = models.BinaryField(null=True)
    application = models.CharField(max_length=255, null=True, blank=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    process_icon = models.CharField(max_length=255, null=True, blank=True)
    subprocess_icon = models.CharField(max_length=255, null=True, blank=True)


class TabScreens(models.Model):
    id = models.AutoField(primary_key=True)
    tab_header_name = models.CharField(max_length=255, null=True)
    tab_icon = models.CharField(max_length=255, null=True)
    tab_type = models.CharField(max_length=255, null=True)
    tab_body_content = models.BinaryField(null=True)
    user_configuration = models.BinaryField(null=True)
    related_item_code = models.CharField(max_length=100, null=True)
    element_id = models.CharField(max_length=300, null=True, unique=True)
    shape = models.CharField(max_length=256, null=True)
    user_name = models.CharField(max_length=100, null=True)
    table_name = models.BinaryField(null=True)
    computation_name = models.CharField(max_length=300, null=True)
    dependent_computations = models.CharField(max_length=2000, null=True)
    fields = models.BinaryField(null=True)
    tabs_multi_function = models.BinaryField(null=True)
    custom_validation_condition = models.BinaryField(null=True)
    other_config = models.BinaryField(null=True)
    update_version = models.CharField(max_length=50, null=True, default="1.0.0")


class Tables(models.Model):
    id = models.AutoField(primary_key=True)
    tablename = models.CharField(max_length=255, null=False, unique=True)
    fields = models.BinaryField(null=True)
    model_type = models.CharField(max_length=255, null=False)
    linked_table = models.CharField(max_length=255, null=True)
    other_config = models.BinaryField(null=True)
    version = models.CharField(max_length=10, default="1.0.0", null=False, verbose_name="Version")


class Templates(models.Model):
    id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100, null=True, verbose_name="Category Name")
    category_type = models.CharField(max_length=100, null=True, verbose_name="Category Type")
    category_attributes = models.BinaryField(null=True, verbose_name="Category Attributes")
    category_subelements = models.BinaryField(null=True, verbose_name="Category Subelements")
    description = models.BinaryField(null=True, verbose_name="Description")
    image = models.ImageField(blank=True, verbose_name="Image", null=True)

    def __str__(self):
        return self.category_name


class Category_Subelement(models.Model):
    id = models.AutoField(primary_key=True)
    category_subelement_name = models.CharField(
        max_length=264, null=True, verbose_name="Category Subelement Name"
    )
    category_subelement_type = models.CharField(
        max_length=264, null=True, verbose_name="Category Sublement Type"
    )
    dependency = models.BinaryField(null=True, verbose_name="Dependency")
    category_subelement_attributes = models.BinaryField(
        null=True, verbose_name="Category Subelement Attributes"
    )
    description = models.BinaryField(null=True, verbose_name="Description")
    image = models.ImageField(blank=True, verbose_name="Image", null=True)

    def __str__(self):
        return self.category_subelement_name


class Category_Subelement_Attributes(models.Model):
    id = models.AutoField(primary_key=True)
    category_subelement_attributes = models.CharField(
        max_length=264, null=True, verbose_name="Category Subelement Attributes"
    )
    choice_type = models.CharField(max_length=264, null=True)
    choice = models.BinaryField(null=True, verbose_name="Choices")
    corresponding_html_element = models.BinaryField(null=True)
    style_applicable = models.CharField(max_length=264, null=True)

    def __str__(self):
        return self.category_subelement_attributes


class Users_urlMap(models.Model):
    url = models.CharField(max_length=264, null=True)
    name = models.CharField(max_length=264, null=True)


class audit_operation(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=526, null=True)
    operation = models.CharField(max_length=264, null=True)
    message = models.TextField(null=True)
    datetime = models.DateTimeField(auto_now=True, editable=False)
    username = models.CharField(max_length=264, null=True)


class Process_subprocess_flowchart(models.Model):
    id = models.AutoField(primary_key=True)
    related_item_code = models.CharField(max_length=255, unique=True)
    flowchart_xml = models.BinaryField(null=True)
    flowchart_dict = models.BinaryField(null=True)
    filename_xml = models.CharField(max_length=255, null=True)
    flowchart_elements = models.BinaryField(null=True)

    def __str__(self):
        return self.related_item_code


class computation_model_flowchart(models.Model):
    id = models.AutoField(primary_key=True)
    model_name = models.CharField(max_length=255, null=True, unique=True)
    flowchart_xml = models.BinaryField(null=True)
    flowchart_dict = models.BinaryField(null=True)
    flowchart_elements = models.BinaryField(null=True)
    scenario_comparative_config = models.BinaryField(null=True)
    output_elements = models.BinaryField(null=True)
    execution_parameters = models.BinaryField(null=True)

    def __str__(self):
        return self.model_name


class computation_model_configuration(models.Model):
    id = models.AutoField(primary_key=True)
    model_name = models.CharField(max_length=255, null=True)
    element_id = models.CharField(max_length=255, null=True)
    element_name = models.CharField(max_length=255, null=True)
    element_config = models.BinaryField(null=True)

    def __str__(self):
        return self.element_id


class computation_model_run_history(models.Model):
    id = models.AutoField(primary_key=True)
    model_name = models.CharField(max_length=255, null=True)
    data_json = models.BinaryField(null=True)
    output_type = models.CharField(max_length=255, null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)


class jobs_scheduled(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)
    start_date = models.DateField(auto_now=True, editable=False)
    end_date = models.DateField(auto_now=True, editable=False)
    periodicity = models.CharField(max_length=256)
    time = models.CharField(max_length=256)
    job_id = models.CharField(max_length=256)
    task_config = models.BinaryField(null=True)


# Approval Table For Decision Box
class ApprovalTable(models.Model):
    id = models.AutoField(primary_key=True)
    tablename = models.CharField(verbose_name="Table Name", max_length=255, null=False)
    json_data = models.BinaryField(verbose_name="Json Data", null=False)
    approval_status = models.CharField(verbose_name="Approval Status", max_length=100, null=False)
    approval_code = models.CharField(verbose_name="Approval Code", null=True, max_length=256)
    create_view_element_id = models.CharField(verbose_name="Source Element Id", max_length=256, null=False)
    approver_group = models.CharField(verbose_name="Approver Group", max_length=526, null=True, default="[]")
    approval_type = models.CharField(verbose_name="Approval Type", max_length=256, null=False)
    approval_comments = models.BinaryField(verbose_name="Approval Comments", null=True)
    transaction_id = models.CharField(
        verbose_name="Transaction Id", max_length=255, null=True, default="NULL"
    )
    created_by = models.CharField(verbose_name="Created By", max_length=100)
    created_date = models.DateTimeField(verbose_name="Created Date", auto_now=True, editable=False)
    modified_by = models.CharField(verbose_name="Modified By", max_length=100, null=True)
    modified_date = models.DateTimeField(
        verbose_name="Modified Date", auto_now=True, editable=False, null=True
    )
    modify_column = models.TextField(verbose_name="Modify Column", null=True)
    type_of_approval = models.CharField(
        verbose_name="Type Of Approval", max_length=256, default="static", null=True
    )
    hierarchy_group = models.CharField(verbose_name="Hierarchy Group", max_length=256, null=True)
    approval_level_config = models.BinaryField(verbose_name="Approval Level Config", null=True)
    approver_user = models.CharField(verbose_name="Approver User", max_length=1026, null=True)
    approval_decision_mailer_config = models.CharField(
        verbose_name="Approval Decision Mailer Config", max_length=1026, null=True
    )
    current_decision_box_id = models.CharField(
        verbose_name="Current Decision Box Id", max_length=50, null=True
    )
    approver_type = models.CharField(
        verbose_name="Approver Type", max_length=20, null=True, default="several"
    )
    approved_by = models.CharField(verbose_name="Approved By", max_length=526, null=True)
    approval_audit_log = models.BinaryField(verbose_name="Audit Log", null=True)
    mentioned_usernames = models.CharField(verbose_name="Mentioned Usernames", max_length=526, null=True)
    approval_information = models.BinaryField(verbose_name="Approval Information", null=True)
    messages = models.CharField(verbose_name="Messages", max_length=256, null=True)


class Business_Models(models.Model):
    id = models.AutoField(primary_key=True)
    business_model_code = models.CharField(max_length=255, null=True)
    business_model_name = models.CharField(max_length=255, null=True)
    application_codes = models.BinaryField(null=True)
    process_group_codes = models.BinaryField(null=True)
    process_group_names = models.BinaryField(null=True)
    description = models.CharField(max_length=526, null=True)
    computation_model_codes = models.BinaryField(null=True)
    computation_model_names = models.BinaryField(null=True)
    table_names = models.BinaryField(null=True)
    additional_table_names = models.BinaryField(null=True)


class Application(models.Model):
    id = models.AutoField(primary_key=True)
    application_code = models.CharField(max_length=255, null=True)
    application_name = models.CharField(max_length=255, null=True)
    no_of_alert = models.IntegerField(null=True)
    approval_email = models.TextField(null=True)
    business_model_codes = models.BinaryField(null=True)
    business_model_names = models.BinaryField(null=True)
    process_group_codes = models.BinaryField(null=True)
    process_group_names = models.BinaryField(null=True)
    computation_model_codes = models.BinaryField(null=True)
    computation_model_names = models.BinaryField(null=True)
    table_names = models.BinaryField(null=True)
    description = models.TextField(null=True)
    app_icon = models.CharField(max_length=255, null=True)
    app_icon_color = models.CharField(max_length=255, null=True)
    app_card_color = models.CharField(max_length=255, null=True)
    app_text_color = models.CharField(max_length=255, null=True)
    navbar_order = models.BinaryField(null=True)
    app_ui_config = models.BinaryField(null=True)
    created_by = models.CharField(max_length=150, editable=False, null=True)
    created_date = models.DateTimeField(auto_now=True, editable=False, null=True)


class external_application_master(models.Model):
    id = models.AutoField(primary_key=True)
    hyperlink_code = models.CharField(max_length=255, null=True)
    hyperlink_name = models.CharField(max_length=255, null=True)
    hyperlink_desc = models.CharField(max_length=255, null=True)
    hyperlink_url = models.CharField(max_length=255, null=True)
    hyperlink_icon = models.CharField(max_length=255, null=True)
    hyperlink_icon_color = models.CharField(max_length=255, null=True)
    hyperlink_card_color = models.CharField(max_length=255, null=True)
    hyperlink_text_color = models.CharField(max_length=255, null=True)
    hyperlink_description_text_color = models.CharField(max_length=255, null=True)
    external_app_ui_config = models.BinaryField(null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)


class Upload_Error_History(models.Model):
    id = models.AutoField(primary_key=True)
    file_name = models.CharField(max_length=255, null=True)
    error_data = models.BinaryField(null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)


class summary_table(models.Model):
    id = models.AutoField(primary_key=True)
    input_file_name = models.CharField(max_length=255, null=True)
    table_name = models.CharField(max_length=255, null=True)
    frequency = models.CharField(max_length=255, null=True)
    upload_date = models.CharField(max_length=255, null=True)
    upload = models.CharField(max_length=255, null=True)
    report_module = models.CharField(max_length=255, null=True)


class Plans(models.Model):
    id = models.AutoField(primary_key=True)
    plan_name = models.CharField(max_length=255, null=True, unique=True)
    plan_description = models.CharField(max_length=526, null=True)
    plan_access = models.CharField(max_length=255, null=True)
    plan_members = models.BinaryField(null=True)
    plan_labels = models.BinaryField(null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)


class Plan_Buckets(models.Model):
    id = models.AutoField(primary_key=True)
    bucket_name = models.CharField(max_length=255, null=True)
    bucket_id = models.CharField(max_length=255, null=True, unique=True)
    plan_name = models.CharField(max_length=255, null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)


class Tasks_Planner(models.Model):
    id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=255, null=True)
    task_id = models.CharField(max_length=255, null=True, unique=True)
    bucket_name = models.CharField(max_length=255, null=True)
    bucket_id = models.CharField(max_length=255, null=True)
    plan_name = models.CharField(max_length=255, null=True)
    due_date = models.DateField(null=True)
    progress_status = models.CharField(max_length=255, null=True)
    priority_status = models.CharField(max_length=255, null=True)
    task_description = models.TextField(null=True)
    task_members = models.BinaryField(null=True)
    task_labels = models.BinaryField(null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)


## Cashflow models
class Curve_Repository(models.Model):
    id = models.AutoField(primary_key=True)
    curve_name = models.CharField(max_length=255, null=True, unique=True)
    quote_type = models.CharField(max_length=255, null=True)
    curve_type = models.CharField(max_length=255, null=True)
    curve_reference = models.CharField(max_length=255, null=True)
    interpolation_algorithm = models.CharField(max_length=255, null=True)
    bootstrap_algorithm = models.CharField(max_length=255, null=True)
    generator_algorithm = models.CharField(max_length=255, null=True)
    holiday_calendar = models.CharField(max_length=255, null=True)
    curve_currency = models.CharField(max_length=255, null=True)
    rate_index = models.CharField(max_length=255, null=True)
    reference_data = models.CharField(max_length=255, null=True)
    custom_reference_data = models.CharField(max_length=255, null=True)
    tenor_name = models.CharField(max_length=255, null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)
    transaction_id = models.CharField(max_length=300, null=True)


class Curve_Data(models.Model):
    id = models.AutoField(primary_key=True)
    curve_name = models.CharField(max_length=255, null=True, unique=True)
    quote_date = models.DateField(null=True)
    curve_points = models.BinaryField(null=True)
    interpolation_algorithm = models.CharField(max_length=255, null=True)
    holiday_calendar = models.CharField(max_length=255, null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)
    transaction_id = models.CharField(max_length=300, null=True)


class Holiday_Calendar_Repository(models.Model):
    id = models.AutoField(primary_key=True)
    holiday_calendar = models.CharField(
        verbose_name="Holiday calendar",
        max_length=255,
        null=True,
    )
    holiday_calendar_tag = models.CharField(
        verbose_name="Holiday calendar tag",
        max_length=255,
        null=True,
    )
    holiday_date = models.DateField(verbose_name="Holiday date", auto_now=False, editable=True, null=True)
    holiday_description = models.BinaryField(verbose_name="Holiday description", null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)
    transaction_id = models.CharField(max_length=300, null=True)


class Model_Repository(models.Model):
    id = models.AutoField(primary_key=True)
    model_code = models.CharField(max_length=255, unique=True)
    model_type = models.CharField(max_length=255)
    model_name = models.CharField(max_length=255)
    model_category = models.CharField(max_length=255)
    model_subcategory = models.CharField(max_length=255)
    model_parent_group = models.CharField(max_length=255)
    model_description = models.TextField(null=True)
    model_inputs = models.BinaryField(null=True)
    model_config = models.BinaryField(null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)


class Error_Master_Table(models.Model):
    id = models.AutoField(primary_key=True)
    feature_category = models.CharField(max_length=255, null=True)
    feature_subcategory = models.CharField(max_length=255, null=True)
    table_file_name = models.CharField(max_length=255, null=True)
    error_description = models.TextField(null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)


class Draft_FormData(models.Model):
    id = models.AutoField(primary_key=True)
    table_name = models.CharField(max_length=255, null=True)
    create_view_element_id = models.CharField(max_length=255, null=True)
    user_info = models.BinaryField(verbose_name="User Data", null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)


# Pivot Reporting
class ConfigTable(models.Model):
    id = models.AutoField(primary_key=True)
    app_code = models.CharField(null=True, max_length=256)
    element_id = models.CharField(max_length=255, null=True)
    reportname = models.CharField(null=True, max_length=256)
    reportconfig = models.BinaryField(verbose_name="Report Config")
    categoryname = models.CharField(max_length=255, null=True)
    dbname = models.CharField(max_length=150, null=True)
    created_by = models.CharField(max_length=100, null=True)
    created_date = models.DateTimeField(auto_now=True, editable=False, null=True)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)


# group config analysis dashboard model
class group_config(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False)
    group_config = models.BinaryField(null=True)
    screen_url = models.CharField(max_length=255, null=False)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)


class Ocr_Template(models.Model):
    id = models.AutoField(primary_key=True)
    template_name = models.CharField(max_length=255, blank=False)
    table_name = models.CharField(max_length=255, blank=False)
    region_of_interest = models.BinaryField(null=False)
    template_image = models.ImageField(upload_to="users/ocr_templates", null=False)
    created_by = models.CharField(max_length=100)
    created_date = models.DateField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateField(auto_now=True, editable=False, null=True)


class computation_output_repository(models.Model):
    id = models.AutoField(primary_key=True)
    model_name = models.CharField(max_length=255, blank=False)
    model_outputs = models.BinaryField(null=True)


class data_mapping_error_report(models.Model):
    id = models.AutoField(primary_key=True)
    base_data_name = models.CharField(max_length=256, blank=False)
    mapping_ruleset_name = models.CharField(max_length=256, blank=False)
    list_of_items_not_mapped = models.BinaryField(blank=False)
    created_by = models.CharField(max_length=100)
    created_date = models.DateField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateField(auto_now=True, editable=False, null=True)


class ml_model_repository(models.Model):
    id = models.AutoField(primary_key=True)
    model_type = models.CharField(max_length=255, blank=False)
    element_id = models.CharField(max_length=255, blank=False)
    element_name = models.CharField(max_length=255, blank=False)
    model = models.BinaryField(null=True)
    model_output = models.BinaryField(null=True)
    target_column_data_mapper = models.BinaryField(null=True)
    use_case = models.CharField(max_length=256, null=True)
    model_name = models.CharField(max_length=256, null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)


class UserProfile(models.Model):
    first_name = models.CharField(max_length=30, blank=False, null=True)
    last_name = models.CharField(max_length=30, blank=False, null=True)
    job_title = models.CharField(max_length=30, null=True)
    bio = models.CharField(max_length=1000, null=True)
    location = models.CharField(max_length=30, null=True)
    profile_pic = models.ImageField(
        upload_to="users/profile_pics",
        null=True,
        verbose_name="Profile photo (Note - Upload only jpg/png file)",
    )
    date_joined = models.DateTimeField(
        verbose_name="date joined",
        unique=False,
        null=True,
        blank=True,
    )
    last_login = models.DateTimeField(null=True, verbose_name="last login", blank=True)
    username = models.CharField(
        unique=True,
        null=True,
        db_index=True,
        verbose_name="username",
        validators=[
            django.core.validators.RegexValidator(
                re.compile("^[\\w.@+-]+$", 152), "Enter a valid username.", "invalid"
            )
        ],
        help_text="Required. 150 characters or fewer. Letters, numbers and @/./+/-/_ characters",
        max_length=150,
    )
    email = models.EmailField(unique=False, null=True, max_length=254, verbose_name="email")
    is_superuser = models.BooleanField(
        default=False,
        help_text="Designates that this user has all permissions without explicitly assigning them.",
        verbose_name="superuser status",
    )
    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into this admin site.",
        verbose_name="staff status",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
        verbose_name="active",
    )
    contact_number = models.CharField(max_length=10, null=True, blank=True)
    linkedin = models.CharField(max_length=150, null=True, blank=True)
    twitter = models.CharField(max_length=150, null=True, blank=True)
    facebook = models.CharField(max_length=150, null=True, blank=True)
    github = models.CharField(max_length=150, null=True, blank=True)
    department = models.CharField(max_length=150, null=True, blank=True)


class Process_flow_model(models.Model):
    app_code = models.CharField(max_length=300, blank=True)
    process = models.CharField(max_length=300, blank=True)
    subprocess = models.CharField(max_length=300, blank=True)
    transaction_id = models.CharField(max_length=300, null=True)
    flow_id = models.CharField(max_length=300, blank=True, null=True)
    flow = models.BinaryField(max_length=2000, blank=True)
    current_status = models.CharField(max_length=300, blank=True)
    element_name = models.CharField(max_length=300, blank=True, null=True)
    tab_type = models.CharField(max_length=300, blank=True, null=True)
    data_id = models.CharField(max_length=1000, blank=True, null=True)
    element_id = models.CharField(max_length=300, blank=True)
    detailed_status = models.CharField(max_length=2000, blank=True, null=True)
    total_batch_data = models.CharField(max_length=100, blank=True, null=True)
    pass_batch_data = models.CharField(max_length=100, blank=True, null=True)
    redirect_status = models.CharField(max_length=100, blank=True, null=True)
    run_left = models.CharField(max_length=100, blank=True, null=True)
    schedule_process = models.CharField(max_length=100, null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)
    run_time = models.CharField(max_length=100, null=True)


class flow_monitor_error_log(models.Model):
    id = models.AutoField(primary_key=True)
    table_name = models.CharField(max_length=255, null=True)
    transaction_id_data = models.CharField(max_length=255, null=True)
    error_dic = models.BinaryField(null=True)
    error_description = models.CharField(max_length=256, null=True)
    flow = models.CharField(max_length=256, null=True)
    element_id = models.CharField(max_length=255, null=True)
    subprocess = models.CharField(max_length=255, null=True)
    process = models.CharField(max_length=255, null=True)
    app_code = models.CharField(max_length=255, null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)


class computation_function_repository(models.Model):
    id = models.AutoField(primary_key=True)
    operation_name = models.CharField(max_length=255, null=True)
    input_order = models.CharField(max_length=255, null=True)
    input_name = models.CharField(max_length=255, null=True)
    input_label = models.CharField(max_length=255, null=True)
    dependency = models.CharField(max_length=10, null=True)
    dependency_condition = models.CharField(max_length=255, null=True)
    input_type = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.operation_name


class computation_scenario_repository(models.Model):
    id = models.AutoField(primary_key=True)
    model_name = models.CharField(max_length=255, null=True, verbose_name="Model name")
    scenario_id = models.CharField(max_length=255, null=True, verbose_name="Scenario id")
    scenario_name = models.CharField(max_length=255, null=True, verbose_name="Scenario name")
    scenario_config = models.BinaryField(null=True, verbose_name="Scenario config")
    run_with_base_model = models.BooleanField(null=False, verbose_name="Run with base model")
    configuration_date = models.DateTimeField(
        auto_now=True, editable=False, null=True, verbose_name="Configuration date"
    )
    created_by = models.CharField(max_length=100, verbose_name="Created by")
    created_date = models.DateTimeField(auto_now=True, editable=False, verbose_name="Created date")
    modified_by = models.CharField(max_length=100, null=True, verbose_name="Modified by")
    modified_date = models.DateTimeField(
        auto_now=True, editable=False, null=True, verbose_name="Modified date"
    )


class data_management_computed_fields_config(models.Model):
    id = models.AutoField(primary_key=True)
    model_name = models.CharField(max_length=255, null=True)
    element_id = models.CharField(max_length=255, null=True)
    element_name = models.CharField(max_length=255, null=True)
    element_config = models.BinaryField(null=True)

    def __str__(self):
        return self.element_id


class data_management_computed_fields_flow(models.Model):
    id = models.AutoField(primary_key=True)
    model_name = models.CharField(max_length=255, null=True, unique=True)
    flowchart_xml = models.BinaryField(null=True)
    flowchart_dict = models.BinaryField(null=True)
    flowchart_elements = models.BinaryField(null=True)

    def __str__(self):
        return self.model_name


class alerts(models.Model):
    id = models.AutoField(primary_key=True)
    usergroup = models.CharField(null=True, max_length=256)
    alert_instance = models.CharField(null=True, max_length=256)
    approval_status = models.CharField(null=True, max_length=256)
    approval_code = models.CharField(null=True, max_length=256)
    alert_type = models.CharField(null=True, max_length=256)
    alert_options = models.CharField(null=True, max_length=526)
    events = models.CharField(null=True, max_length=526)
    app_code = models.CharField(null=True, max_length=256)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=100, null=True)
    modified_date = models.DateTimeField(auto_now=True, editable=False, null=True)


class alertslog(models.Model):
    id = models.AutoField(primary_key=True)
    usergroup = models.CharField(null=True, max_length=256)
    alert_instance = models.CharField(null=True, max_length=256)
    alert_type = models.CharField(null=True, max_length=256)
    alert_options = models.CharField(null=True, max_length=256)
    events = models.CharField(null=True, max_length=256)
    alert_message = models.CharField(null=True, max_length=256)
    app_code = models.CharField(null=True, max_length=256)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True, editable=False)


class static_page_config(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True)
    app_code = models.CharField(max_length=255, null=True)
    app_mode = models.CharField(max_length=255, null=True)
    display_type = models.CharField(max_length=255, null=True)
    code = models.CharField(max_length=255, null=True)
    config = models.BinaryField(null=True)
    created_by = models.CharField(max_length=100, verbose_name="Created by")
    created_date = models.DateTimeField(auto_now=True, editable=False, verbose_name="Created date")
    modified_by = models.CharField(max_length=100, null=True, verbose_name="Modified by")
    modified_date = models.DateTimeField(max_length=100, null=True, verbose_name="Modified date")


class scheduler_event_status(models.Model):
    id = models.AutoField(primary_key=True)
    process_code = models.CharField(max_length=255, null=True)
    subprocess_code = models.CharField(max_length=255, null=True)
    block_element_id = models.CharField(max_length=255, null=True)
    execution_date = models.DateField(auto_now=False, editable=True)
    execution_time = models.CharField(max_length=100, null=True)
    status = models.CharField(max_length=255, null=True)
    execution_information = models.TextField(null=True, blank=True)
    executed_time = models.CharField(max_length=100, null=True, blank=True)


class process_flow_event_status(models.Model):
    id = models.AutoField(primary_key=True)
    process_code = models.CharField(max_length=255, null=True)
    subprocess_code = models.CharField(max_length=255, null=True)
    block_element_id = models.CharField(max_length=255, null=True)
    execution_date = models.DateField(auto_now=False, editable=True)
    execution_time = models.CharField(max_length=100, null=True)
    status = models.CharField(max_length=255, null=True)
    execution_information = models.TextField(null=True, blank=True)
    executed_time = models.CharField(max_length=100, null=True, blank=True)


class system_management_table(models.Model):
    id = models.AutoField(primary_key=True)
    screens = models.CharField(max_length=256, null=True)
    preference_config = models.BinaryField(null=True)


class application_theme(models.Model):
    id = models.AutoField(primary_key=True)
    app_code = models.CharField(max_length=255, null=True)
    theme_type = models.CharField(max_length=255, null=True)
    theme_name = models.CharField(max_length=255, null=True)
    theme_config = models.BinaryField(null=True)
    created_by = models.CharField(max_length=100, null=True, verbose_name="Created by")
    created_date = models.DateTimeField(auto_now=True, null=True, editable=False, verbose_name="Created date")
    modified_by = models.CharField(max_length=100, null=True, verbose_name="Modified by")
    modified_date = models.DateTimeField(
        auto_now=True, editable=False, null=True, verbose_name="Modified date"
    )


class template_theme(models.Model):
    id = models.AutoField(primary_key=True)
    template_name = models.CharField(max_length=255, null=True, unique=False)
    template_type = models.CharField(max_length=255, null=True, unique=False)
    template_config = models.CharField(max_length=255, null=True, unique=False)


class smtp_configuration(models.Model):
    id = models.AutoField(primary_key=True)
    app_code = models.CharField(max_length=255, null=True)
    element_id = models.BinaryField(null=True, blank=True)
    server_name = models.CharField(max_length=255, null=True)
    description = models.CharField(max_length=526, null=True, blank=True)
    group_assigned = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.element_id


class event_master(models.Model):
    id = models.AutoField(primary_key=True)
    element_id = models.CharField(null=True, max_length=255)
    event = models.CharField(max_length=255, null=True)
    performed_by = models.TextField(null=True, blank=True)
    approval_code = models.CharField(max_length=256, null=True, blank=True)
    action_config = models.BinaryField(null=True, blank=True)
    event_triggered_by = models.CharField(max_length=255, null=True)
    event_triggered_date = models.DateTimeField(auto_now=True, null=True, editable=False)
    status = models.CharField(max_length=100, null=True, blank=True)
    recipients_list = models.TextField(null=True, blank=True)


class system_application_master(models.Model):
    id = models.AutoField(primary_key=True)
    app_name = models.CharField(max_length=255, verbose_name="App Name", null=False)
    display_config = models.BinaryField(null=False)
    app_drawer_ui_config = models.BinaryField(null=True)
    app_theme = models.BinaryField(null=True)


sys_tables = [
    "Templates",
    "usergroup_approval",
    "CountryMaster",
    "CurrencyMaster",
    "Application",
    "Curve_Repository",
    "computation_model_configuration",
    "Profile",
    "Category_Subelement",
    "Hierarchy_table",
    "Curve_Data",
    "computation_model_flowchart",
    "jobs_scheduled",
    "group_config",
    "Draft_FormData",
    "Error_Master_Table",
    "Business_Models",
    "computation_model_run_history",
    "Users_urlMap",
    "Tasks_Planner",
    "Ocr_Template",
    "NavigationSideBar",
    "Holiday_Calendar_Repository",
    "Process_subprocess_flowchart",
    "UserPermission_Master",
    "Plan_Buckets",
    "permissionaccess",
    "TabScreens",
    "ApprovalTable",
    "Model_Repository",
    "Upload_Error_History",
    "summary_table",
    "DraftProcess",
    "user_approval",
    "configuration_parameter",
    "Tables",
    "allocated_licences",
    "Category_Subelement_Attributes",
    "UserConfig",
    "Plans",
    "computation_output_repository",
    "Hierarchy_levels",
    "data_mapping_error_report",
    "Hierarchy_groups",
    "userpermission_interim",
    "group_details",
    "ml_model_repository",
    "UserProfile",
    "ConfigTable",
    "Process_flow_model",
    "computation_function_repository",
    "computation_scenario_repository",
    "data_management_computed_fields_config",
    "data_management_computed_fields_flow",
    "application_theme",
    "template_theme",
    "flow_monitor_error_log",
    "alerts",
    "alertslog",
    "static_page_config",
    "audit_operation",
    "ProcessScheduler",
    "scheduler_event_status",
    "process_flow_event_status",
    "external_application_master",
    "system_management_table",
    "smtp_configuration",
    "event_master",
    "system_application_master",
]

admin_tables = [
    "user",
    "Profile",
    "auth_group",
    "user_groups",
    "configuration_parameter",
    "UserPermission_Master",
    "permissionaccess",
    "usergroup_approval",
    "user_approval",
    "allocated_licences",
    "user_model",
    "userpermission_interim",
    "group_details",
    "user_navbar",
    "failed_login_alerts",
    "dashboard_config",
    "login_trail",
    "audit_trail",
    "notification_management",
    "applicationAccess",
]

sys_tables = [i for i in sys_tables if i not in admin_tables]


def json_creator():
    app_config_struc_json = {}
    existing_model_structure = {}
    with open(f"{PLATFORM_DATA_PATH}app_config_tables.json") as currentfile:
        existing_model_structure = json.load(currentfile)
        currentfile.close()
    for i in sys_tables:
        model_class = eval(i + "()")
        if existing_model_structure.get(i):
            version = existing_model_structure[i]["version"]
        else:
            version = "1.0.0"
        model_config = {"version": version, "field_config": {}}
        primary_key = model_class._meta.pk.name
        for field in model_class._meta.concrete_fields:
            field_name = field.name
            field_config = {
                "internal_type": str(field.get_internal_type()),
                "verbose_name": str(field.verbose_name),
                "null": field.null,
                "unique": field.unique,
                "validators": [],
            }
            if field_name == primary_key:
                field_config["primary_key"] = True
            if field.get_internal_type() == "CharField":
                field_config["max_length"] = field.max_length
                if getattr(field, "choices"):
                    field_config["choices"] = field.choices
            elif field.get_internal_type() in ["DateTimeField", "DateField", "TimeField"]:
                field_config["auto_now"] = field.auto_now
                field_config["editable"] = field.editable
            elif field.get_internal_type() == "ConcatenationField":
                field_config["columns"] = field.columns
            elif field.get_internal_type() == "ForeignKey":
                field_config["parent"] = str(field.remote_field.model.__name__)
            else:
                pass
            if field.get_default():
                field_config["default"] = str(field.get_default())
            else:
                pass
            model_config["field_config"][field_name] = field_config
        app_config_struc_json[i] = model_config
    with open(f"{PLATFORM_DATA_PATH}app_config_tables.json", "w") as outfile:
        json.dump(app_config_struc_json, outfile, indent=4)
        outfile.close()
    return app_config_struc_json
