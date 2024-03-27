import json
import logging
import os

from bootstrap_datepicker_plus.widgets import DatePickerInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Column, Layout, Row, Submit

# dynamic_forms
# dynamic_forms
from django import forms
from django.contrib.auth import get_user_model
import django.contrib.auth.forms as auth_form
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

##formset
from django.forms import BaseFormSet, CheckboxInput, HiddenInput, ModelForm, SelectMultiple, TextInput
from django.middleware.csrf import get_token

##formset
from django.utils.translation import gettext_lazy as _
from django_multitenant.utils import get_current_tenant
import pandas as pd

from config.settings.base import PLATFORM_FILE_PATH
from kore_investment.users.computations.db_centralised_function import (
    current_app_db_extractor,
    db_engine_extractor,
    read_data_func,
)
from kore_investment.users.models import Profile

from . import models
from .computations import html_generator

User = get_user_model()


class UserChangeForm(auth_form.UserChangeForm):
    class Meta(auth_form.UserChangeForm.Meta):
        model = User


class UserCreationForm(auth_form.UserCreationForm):

    error_message = auth_form.UserCreationForm.error_messages.update(
        {"duplicate_username": _("This username has already been taken.")}
    )

    class Meta(auth_form.UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data["username"]

        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username

        raise ValidationError(self.error_messages["duplicate_username"])


class UserGroupForm(ModelForm):
    class Meta:
        model = Group
        fields = "__all__"
        widgets = {
            "name": TextInput(
                attrs={
                    "placeholder": "Group name",
                    "class": "pl-0",
                    "help_text": "Group name can not contain special characters and should be unique.",
                }
            ),
        }

    def clean_name(self):
        name = self.cleaned_data["name"]
        if Group.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("User group with that name already exists.")
        return name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column("name", css_class="form-group col-md-3 mb-0 pl-0 grpname")),
        )
        self.helper.form_method = "post"
        self.helper.add_input(
            Submit(
                "submit",
                "Save",
                css_id="save_user_group_form_button",
                css_class="buttonstyling acies_btn acies_btn-primary button_standard_save",
            )
        )


class UserForm(ModelForm):
    class Meta:
        model = models.user_model
        fields = "__all__"
        widgets = {
            "username": TextInput(attrs={"placeholder": "Username", "class": "user_creation_fields"}),
            "password": TextInput(
                attrs={
                    "placeholder": "Password",
                    "readonly": "readonly",
                    "type": "password",
                    "class": "user_creation_fields",
                }
            ),
            "email": TextInput(attrs={"placeholder": "Email", "class": "user_creation_fields"}),
            "ldap_login": CheckboxInput(attrs={"class": "aciescustom-control-label"}),
            "application_login": CheckboxInput(attrs={"class": "aciescustom-control-label"}),
            "is_developer": CheckboxInput(attrs={"class": "aciescustom-control-label"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("username", css_class="form-group col-md-4"),
                Column("password", css_class="form-group col-md-4"),
                Column("email", css_class="form-group col-md-4"),
                css_class="form-row",
            ),
            Row(
                Column("ldap_login", css_class="form-group col-md-6", css_id="ldap"),
                Column("application_login", css_class="form-group col-md-6", css_id="application"),
                css_class="form-row",
            ),
            Row(
                Column("is_developer", css_class="form-group col-md-12", css_id="is_developer"),
            ),
        )
        self.helper.form_method = "post"
        self.helper.add_input(
            Button(
                "submit",
                "Save",
                css_id="save_user_form_button",
                css_class="buttonstyling acies_btn acies_btn-primary standard_button_click",
            )
        )


class UserForm1(ModelForm):
    class Meta:
        model = User
        fields = "__all__"
        widgets = {
            "username": TextInput(attrs={"placeholder": "Username"}),
            "email": TextInput(attrs={"placeholder": "Email"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("username", css_class="form-group col-md-3"),
                Column("email", css_class="form-group col-md-3"),
                css_class="form-row",
            ),
        )
        self.helper.form_method = "post"
        self.helper.add_input(
            Button(
                "submit",
                "Save",
                css_id="save_user_form_button",
                css_class="buttonstyling acies_btn acies_btn-primary",
            )
        )


class UserGroupTagForm(forms.Form):
    User_id = forms.MultipleChoiceField(
        label="User Id",
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-control select-multiple select2",
                "size": "10",
                "multiple": True,
                "required": True,
            }
        ),
    )
    Group_id = forms.ChoiceField(
        label="Group Id",
        widget=forms.Select(
            attrs={
                "class": "form-control select-multiple select2",
                "size": "10",
                "multiple": True,
                "required": True,
            }
        ),
    )

    def __init__(self, *args, request="", **kwargs):
        super().__init__(*args, **kwargs)
        instance = get_current_tenant()
        user_list = (
            read_data_func(
                request,
                config_dict={
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "User",
                        "Columns": ["id", "username"],
                    },
                    "condition": [
                        {
                            "column_name": "instance_id",
                            "condition": "Equal to",
                            "input_value": instance.id,
                            "and_or": "",
                        },
                    ],
                },
            )
            .set_index("id")["username"]
            .to_dict()
        )
        user_list = [(key, value) for key, value in user_list.items()]
        self.fields["User_id"].choices = user_list

        group_list = read_data_func(
            request,
            config_dict={
                "inputs": {"Data_source": "Database", "Table": "group_details", "Columns": ["name"]},
                "condition": [
                    {
                        "column_name": "instance_id",
                        "condition": "Equal to",
                        "input_value": instance.id,
                        "and_or": "",
                    },
                ],
            },
        ).name.tolist()
        self.fields["Group_id"].choices = [(i, i) for i in group_list]

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("User_id", css_class="form-group col-md-3 mb-3"),
                Column("Group_id", css_class="form-group col-md-3 mb-3"),
                css_class="form-row",
            ),
        )

        self.helper.form_method = "post"
        self.helper.add_input(
            Submit(
                "submit",
                "Save",
                css_class="buttonstyling acies_btn acies_btn-primary button_standard_save",
            )
        )


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = (
            "first_name",
            "last_name",
            "bio",
            "job_title",
            "location",
            "profile_pic",
            "date_joined",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "username",
        )


class BaseArticleFormSet(BaseFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields["id"] = forms.IntegerField(widget=HiddenInput(attrs={"required": False}))


#     class Meta:

#         self.helper.layout = Layout(
#             Row(


class UserPermission_MasterForm(ModelForm):

    level_1 = forms.MultipleChoiceField(
        label="Sub-Process Name",
        widget=SelectMultiple(attrs={"size": "10", "multiple": True, "class": "select2 form-control"}),
    )
    level_2 = forms.MultipleChoiceField(
        label="Sub-Process Tab Name",
        widget=SelectMultiple(attrs={"size": "10", "multiple": True, "class": "select2 form-control"}),
    )
    level_button_access = forms.MultipleChoiceField(
        label="Button Access Permission",
        widget=SelectMultiple(attrs={"size": "10", "multiple": True, "class": "select2 form-control"}),
    )

    class Meta:
        model = models.UserPermission_Master
        fields = "__all__"

        widgets = {"permission_name": SelectMultiple()}

    def __init__(self, *args, request="", **kwargs):
        super().__init__(*args, **kwargs)
        for key in self.fields:
            self.fields[key].required = False
        instance = get_current_tenant()
        self.fields["permission_type"].widget.attrs["class"] = "form-control select2"
        app_code, db_connection_name = current_app_db_extractor(request, tenant=None)
        app_choice = read_data_func(
            request,
            config_dict={
                "inputs": {
                    "Data_source": "Database",
                    "Table": "Application",
                    "Agg_Type": "DISTINCT",
                    "Columns": ["application_name", "application_code"],
                },
                "condition": [
                    {
                        "column_name": "application_code",
                        "condition": "Equal to",
                        "input_value": app_code,
                        "and_or": "",
                    },
                ],
            },
        )
        app_choice = app_choice[["application_name", "application_code"]].values.tolist()
        f_app_choice = []
        app_dict = {}
        for i in range(0, len(app_choice)):
            f_app_choice.append((app_choice[i][1], app_choice[i][0]))
            app_dict[app_choice[i][1]] = app_choice[i][0]
        self.fields["application"] = forms.ChoiceField(choices=f_app_choice)
        self.fields["application"].widget.attrs["data-app_name"] = app_dict
        self.fields["application"].widget.attrs["class"] = "form-control select2"
        valu1 = read_data_func(
            request,
            config_dict={
                "inputs": {"Data_source": "Database", "Table": "group_details", "Columns": ["name"]},
                "condition": [
                    {
                        "column_name": "instance_id",
                        "condition": "Equal to",
                        "input_value": instance.id,
                        "and_or": "",
                    },
                ],
            },
        )
        val01 = valu1.name.tolist()
        val02 = []
        val02.append(("", "-----------"))
        for i in range(0, len(val01)):
            val02.append((val01[i], val01[i]))
        self.fields["usergroup"] = forms.ChoiceField(choices=val02)

        self.fields["usergroup"].widget.attrs["class"] = "form-control select2"

        self.fields["permission_name"] = forms.MultipleChoiceField(label="Process Name", choices=[])
        self.fields["permission_name"].widget.attrs["class"] = "form-control select2"
        self.fields["permission_name"].widget.attrs["size"] = "10"
        self.fields["permission_name"].widget.attrs["multiple"] = True

        self.fields["permission_level"].widget.attrs["class"] = "form-control select2"
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("usergroup", css_class="form-group col-md-3", css_id="uname"),
                Column(
                    "application", css_class="form-group col-md-3", css_id="application", style="display:none"
                ),
                Column("permission_type", css_class="form-group col-md-3", css_id="permtype"),
                Column(
                    "permission_level",
                    style="display:none",
                    css_class="form-group col-md-3",
                    css_id="permlevel",
                ),
                css_class="form-row",
            ),
            Row(
                Column(
                    "permission_name",
                    css_class="form-group col-md-4",
                    style="display:none",
                    css_id="div_level_0",
                ),
                Column(
                    "level_1", css_class="form-group col-md-4", style="display:none", css_id="div_level_1"
                ),
                Column(
                    "level_2", css_class="form-group col-md-4", style="display:none", css_id="div_level_2"
                ),
                Column(
                    "level_button_access",
                    css_class="form-group col-md-4",
                    style="display:none",
                    css_id="div_level_button_access",
                ),
                css_class="form-row",
            ),
            Row(css_class="form-row", css_id="div_dev_mode"),
        )
        self.helper.form_method = "post"

        self.helper.add_input(
            Button(
                "submit",
                "Save",
                css_id="save_userpermission_master_form_button",
                css_class="buttonstyling acies_btn acies_btn-primary button_standard_save",
            )
        )


def create_test_form(
    model_name,
    create_view_tab_body_content,
    element_id,
    request,
    user_group,
    edit=False,
    parent_element_id="",
    linked_bool=True,
):
    curr_app_code, db_connection_name = current_app_db_extractor(request)
    user_db_engine, db_type = db_engine_extractor(db_connection_name)
    modal_name = "list_view_edit_modal_"
    pre_ele = "process"
    view = "list view"

    if create_view_tab_body_content["Category_attributes"]["Template"].get(
        "Template_type"
    ) == "Custom defined template" and parent_element_id.startswith("whiteSpacewrap"):
        related_item_code = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "TabScreens",
                    "Columns": ["related_item_code"],
                },
                "condition": [
                    {
                        "column_name": "element_id",
                        "condition": "Equal to",
                        "input_value": element_id,
                        "and_or": "",
                    },
                ],
            },
        ).to_dict("records")[0]
        item_group_code = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "NavigationSideBar",
                    "Columns": ["item_group_code"],
                },
                "condition": [
                    {
                        "column_name": "item_code",
                        "condition": "Equal to",
                        "input_value": related_item_code["related_item_code"],
                        "and_or": "",
                    },
                ],
            },
        ).to_dict("records")[0]
        if os.path.exists(
            f"kore_investment/templates/user_defined_template/public/{curr_app_code}/{item_group_code['item_group_code']}_{related_item_code['related_item_code']}_{parent_element_id}.html"
        ):
            with open(
                f"kore_investment/templates/user_defined_template/public/{curr_app_code}/{item_group_code['item_group_code']}_{related_item_code['related_item_code']}_{parent_element_id}.html"
            ) as f:
                html = f.read()
                html = html.replace("createview", "list_view_edit_modal_")
                html = html.replace(parent_element_id, element_id)
        else:
            pass
    else:
        html, script = html_generator.html_generator(
            model_name,
            create_view_tab_body_content,
            element_id,
            request,
            edit=True,
            user_group=user_group,
            linked_bool=linked_bool,
            view=view,
            list_view_flag=True,
        )
    js_script = html_generator.jsFieldsGenerator(
        name=modal_name, tab_type_list=["list_view"], pre_ele=pre_ele
    )
    csrf_token = get_token(request)
    csrf_token_html = f'<input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}" />'
    if html.find("{%csrf_token%}") != -1:
        html = html.replace("{%csrf_token%}", csrf_token_html)
    elif html.find("{% csrf_token %}") != -1:
        html = html.replace("{% csrf_token %}", csrf_token_html)
    codeList = {"html": html, "script": js_script}
    return codeList


class upload_screen_datepickerform(forms.Form):
    Date_of_Extraction = forms.DateField(
        widget=DatePickerInput(
            format="%d-%m-%Y",
            attrs={"placeholder": "DD-MM-YYYY", "css_class": "dateUS", "name": "dateOfExtraction"},
        )
    )
