import os

from config.settings.base import PLATFORM_FILE_PATH

from .base import *  # noqa
from .base import env

# from django.conf import settings you dont need to do this
# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="xdplApuM5LUZw3zSPYmGGgzTVrYAEjytjNZ86pdNCOttIyp0boWETOexptQ8FAUP",
)

# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
hosts = []
if os.path.exists(f"{PLATFORM_FILE_PATH}allowed_host.txt"):
    with open(f"{PLATFORM_FILE_PATH}allowed_host.txt") as txt_data:
        for line in txt_data.readlines():
            hosts += line.split(",")
        txt_data.close()
if hosts == []:
    hosts = ["revolutio.digital", "127.0.0.1"]
ALLOWED_HOSTS = hosts

# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    },
    "st_rate_limit": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "spirit_rl_cache",
        "TIMEOUT": None,
    },
}

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env("DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL regex.
ADMIN_URL = env("DJANGO_ADMIN_URL", default="admin/")

# WhiteNoise
# ------------------------------------------------------------------------------
# http://whitenoise.evans.io/en/latest/django.html#using-whitenoise-in-development
INSTALLED_APPS = ["whitenoise.runserver_nostatic"] + INSTALLED_APPS  # noqa F405


# django-debug-toolbar
# ------------------------------------------------------------------------------
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#prerequisites
INSTALLED_APPS += ["debug_toolbar"]  # noqa F405
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#middleware
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa F405
# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#debug-toolbar-config
DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
    "SHOW_TEMPLATE_CONTEXT": True,
}
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#internal-ips
INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]


# django-extensions
# ------------------------------------------------------------------------------
# https://django-extensions.readthedocs.io/en/latest/installation_instructions.html#configuration
INSTALLED_APPS += ["django_extensions"]  # noqa F405

# Your stuff...
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/3.0/topics/settings/
SESSION_COOKIE_AGE = 60 * 60 * 24

# STATIC
# ------------------------


COMPRESS_URL = "https://revolutiodatastore.blob.core.windows.net/%24web/static/"


STATICFILES_STORAGE = "kore_investment.custom_storage.custom_azure.PrivateAzureStorage"


COMPRESS_ENABLED = env.bool("COMPRESS_ENABLED", default=True)
# https://django-compressor.readthedocs.io/en/latest/settings/#django.conf.settings.COMPRESS_STORAGE


COMPRESS_STORAGE = "kore_investment.custom_storage.custom_azure.PrivateAzureStorage"
# https://django-compressor.readthedocs.io/en/latest/settings/#django.conf.settings.COMPRESS_URL
# COMPRESS_URL = STATIC_URL  # noqa F405
