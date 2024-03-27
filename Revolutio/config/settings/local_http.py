import os

from config.settings.base import PLATFORM_FILE_PATH

from .base import *  # noqa
from .base import env

# from django.conf import settings   you dont need to do this
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
platform_domain = env("PLATFORM_DOMAIN_NAME", default="revolutio.digital")
if hosts == []:
    hosts = ["127.0.0.1", "localhost"]
hosts.append(f".{platform_domain}")
ALLOWED_HOSTS = hosts

# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_DJANGO_CACHE,
    }
    #            "MAX_ENTRIES": 20000
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

SESSION_COOKIE_AGE = int(env("DJANGO_SESSION_COOKIE_AGE", default="86400"))

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
