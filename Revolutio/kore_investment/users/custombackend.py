import json
import os
import re

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django_auth_ldap.backend import LDAPBackend

from config.settings.base import PLATFORM_FILE_PATH

from .authentication_backend import session_breach_check

if os.path.exists(f"{PLATFORM_FILE_PATH}ldap_configuration.json"):
    with open(f"{PLATFORM_FILE_PATH}ldap_configuration.json") as json_file:
        ldap_data = json.load(json_file)
        variableCounter = 1
        for tenant in ldap_data:
            exec(
                f"""class CustomLDAPBackend{variableCounter}(LDAPBackend):
                settings_prefix = "AUTH_LDAP_{variableCounter}_"

                default_settings = {{
                    "LOGIN_COUNTER_KEY": "CUSTOM_LDAP_LOGIN_ATTEMPT_COUNT",
                    "LOGIN_ATTEMPT_LIMIT": 50,
                    "RESET_TIME": 30 * 60,
                    "USERNAME_REGEX": r"^.*$",
                }}

                def authenticate_ldap_user(self, ldap_user, password):
                    if self.exceeded_login_attempt_limit():
                        # Or you can raise a 403 if you do not want
                        # to continue checking other auth backends
                        return None
                    self.increment_login_attempt_count()
                    user = ldap_user.authenticate(password)
                    if user:
                        user.from_ldap = True
                        user.save()
                    session_breach_check(user, '{tenant}')
                    return user

                def _get_or_create_user(self, username, ldap_user):
                    kwargs = {{"username": username, "defaults": {{"from_ldap": True}} }}
                    user_model = get_user_model()
                    return user_model.objects.get_or_create(**kwargs)

                @property
                def login_attempt_count(self):
                    return cache.get_or_set(self.settings.LOGIN_COUNTER_KEY, 0, self.settings.RESET_TIME)

                def increment_login_attempt_count(self):
                    try:
                        cache.incr(self.settings.LOGIN_COUNTER_KEY)
                    except ValueError:
                        cache.set(self.settings.LOGIN_COUNTER_KEY, 1, self.settings.RESET_TIME)

                def exceeded_login_attempt_limit(self):
                    return self.login_attempt_count >= self.settings.LOGIN_ATTEMPT_LIMIT

                def username_matches_regex(self, username):
                    return re.match(self.settings.USERNAME_REGEX, username)

                def send_sms(self, username):
                    # Implement your SMS logic here
                    return

                """,
                globals(),
                globals(),
            )

            variableCounter += 1

        json_file.close()
