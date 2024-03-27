import random
import string
from typing import Any

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_email, user_field, user_username
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.utils import deserialize_instance, import_attribute, serialize_instance, valid_email_or_none
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django_multitenant.utils import get_current_tenant

User = get_user_model()


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest):
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest, sociallogin: Any):
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def populate_user(self, request, sociallogin, data):
        """
        Hook that can be used to further populate the user instance.

        For convenience, we populate several common fields.

        Note that the user instance being populated represents a
        suggested User instance that represents the social user that is
        in the process of being logged in.

        The User instance need not be completely valid and conflict
        free. For example, verifying whether or not the username
        already exists, is not a responsibility.
        """
        instance = get_current_tenant()
        tenant = instance.name
        username = data.get("username")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        name = data.get("name")

        if sociallogin.account.provider == "google":
            username1 = first_name + "." + last_name
            username2 = username1 + "@google"
            username2 = username2.lower()
            user = User.objects.filter(username=f"{username2}").first()
            if user and not sociallogin.is_existing:
                code = "".join(random.SystemRandom().choice(string.digits) for _ in range(6))
                username = username1 + code + "@google"
            else:
                username = username1 + "@google"
        elif sociallogin.account.provider == "facebook":
            username1 = first_name + "." + last_name
            username2 = username1 + "@facebook"
            username2 = username2.lower()
            user = User.objects.filter(username=f"{username2}").first()
            if user and not sociallogin.is_existing:
                code = "".join(random.SystemRandom().choice(string.digits) for _ in range(6))
                username = username1 + code + "@facebook"
            else:
                username = username1 + "@facebook"
        elif sociallogin.account.provider == "microsoft":
            username1 = first_name + "." + last_name
            username2 = username1 + "@microsoft"
            username2 = username2.lower()
            user = User.objects.filter(username=f"{username2}").first()
            if user and not sociallogin.is_existing:
                code = "".join(random.SystemRandom().choice(string.digits) for _ in range(6))
                username = username1 + code + "@microsoft"
            else:
                username = username1 + "@microsoft"
        user = sociallogin.user
        user_username(user, username or "")
        user_email(user, valid_email_or_none(email) or "")
        name_parts = (name or "").partition(" ")
        user_field(user, "first_name", first_name or name_parts[0])
        user_field(user, "last_name", last_name or name_parts[2])
        user_field(user, "tenant", tenant)
        return user
