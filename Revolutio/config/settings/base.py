"""
Base settings to build other settings files upon.
"""

from configparser import ConfigParser
import datetime
import json
import os
import urllib

from django.contrib.messages import constants as messages
from django_auth_ldap.config import LDAPSearch, LDAPSearchUnion
import environ
import ldap
import oracledb
import psycopg2
from rq import Queue
from sqlalchemy import create_engine, text
from turbodbc import connect, make_options

import redis

from .db_credential_encrytion import (
    decrypt_db_credential,
    decrypt_existing_db_credentials,
    encrypt_db_credentials,
)

ROOT_DIR = environ.Path(__file__) - 3  # (kore_investment/config/settings/base.py - 3 = kore_investment/)
APPS_DIR = ROOT_DIR.path("kore_investment")
config_path = ROOT_DIR.path("revolutio.conf")

config = ConfigParser()
config.read(config_path)

env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(ROOT_DIR.path(".env")))

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", False)
# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = "Asia/Calcutta"
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "en-us"
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
# https://docs.djangoproject.com/en/dev/ref/settings/#locale-paths
LOCALE_PATHS = [ROOT_DIR.path("locale")]

ACCOUNT_SESSION_REMEMBER = None
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Additional configuration settings
SOCIALACCOUNT_QUERY_EMAIL = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_LOGIN_ON_GET = True
ACCOUNT_USERNAME_REQURIED = True
# Required information from provider
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    },
    "facebook": {
        "METHOD": "oauth2",
        "SCOPE": ["email", "public_profile"],
        "AUTH_PARAMS": {"auth_type": "reauthenticate"},
        "INIT_PARAMS": {"cookie": True},
        "FIELDS": [
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "name",
            "name_format",
            "picture",
            "short_name",
        ],
        "EXCHANGE_TOKEN": True,
        "VERIFIED_EMAIL": False,
        "VERSION": "v13.0",
    },
    "microsoft": {
        "TENANT": "organizations",
    },
}

current_dir = os.getcwd()
# ## Configuration to use VM spaces in order to improve I/O speeds using Parquet and Arrow
DISKSTORE_PATH = current_dir + "/Computation_Temp_Storage/"
PLATFORM_FILE_PATH = current_dir + "/Platform_Configs/"
PLATFORM_DATA_PATH = current_dir + "/Platform_Data/"
UPLOADED_APP_BACKUP_PATH = current_dir + "/Platform_Configs/Uploaded_Application_Backups/"

AUTH_LDAP_ALWAYS_UPDATE_USER = True
ACCOUNT_EMAIL_VERIFICATION = "none"

PASSCODE_KEY = env(
    "PASSCODE_KEY",
    default="SgUkXp2s5v8y/B?E(H+MbQeThWmYq3t6w9z$C&F)J@NcRfUjXn2r4u7x!A%D*G-K",
)

# DATABASES

# Use MSSQL/PostgreSQL for database_type and 1433/5432 as port.

server = os.environ.get("POSTGRES_HOST", "172.22.16.1")
database = os.environ.get("POSTGRES_DB", "Platform_DB")
username = os.environ.get("POSTGRES_USER", "postgres")
password = os.environ.get("POSTGRES_PASSWORD", "postgres")
port = os.environ.get("POSTGRES_PORT", "5433")
database_type = os.environ.get("DATABASE_TYPE", "PostgreSQL")

# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

OPERATION_TYPE = os.environ.get("OPERATION_TYPE", "collectstatic")

if OPERATION_TYPE == "collectstatic":

    database_type = "Sqlite3"

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
else:
    if database_type == "PostgreSQL":
        DATABASES = {
            "default": {
                "ENGINE": "django_multitenant.backends.postgresql",
                "HOST": server,
                "PORT": port,
                "NAME": database,
                "USER": username,
                "PASSWORD": password,
            }
        }
    elif database_type == "MSSQL":
        DATABASES = {
            "default": {
                "ENGINE": "sql_server.pyodbc",
                # "HOST":"LP-MUM-01-00067\MSSQLSERVER01", ## to be used in Windows OS
                "HOST": server,
                "PORT": port,
                "NAME": database,
                "USER": username,
                "PASSWORD": password,
                "OPTIONS": {
                    "driver": "ODBC Driver 18 for SQL Server",
                    "extra_params": "Encrypt=yes;TrustServerCertificate=yes;",
                },
            }
        }
    DATABASES["default"]["CONN_MAX_AGE"] = 0

database_engine_dict = {}
if os.path.exists(f"{PLATFORM_FILE_PATH}user_databases.json"):
    with open(f"{PLATFORM_FILE_PATH}user_databases.json") as json_file:
        db_data = json.load(json_file)
        json_file.close()
    for c_name, c_config in db_data.items():
        if "connection_code" in db_data[c_name]:
            decrypted_db_server, decrypted_port, decrypted_db_name, decrypted_username, decrypted_password = (
                decrypt_existing_db_credentials(
                    c_config["server"],
                    c_config["port"],
                    c_config["db_name"],
                    c_config["username"],
                    c_config["password"],
                    c_config["connection_code"],
                )
            )
            c_config["HOST"] = decrypted_db_server
            c_config["PORT"] = decrypted_port
            c_config["NAME"] = decrypted_db_name
            c_config["USER"] = decrypted_username
            c_config["PASSWORD"] = decrypted_password
        else:
            (
                encrypted_server,
                encrypted_port,
                encrypted_database,
                encrypted_username,
                encrypted_user_secret_key,
                connection_code,
            ) = encrypt_db_credentials(
                c_config["server"],
                c_config["port"],
                c_config["db_name"],
                c_config["username"],
                c_config["password"],
            )
            with open(f"{PLATFORM_FILE_PATH}user_databases.json") as json_file:
                content_encrypted = json.load(json_file)
                json_file.close()
            content_encrypted[c_name]["server"] = encrypted_server
            content_encrypted[c_name]["port"] = encrypted_port
            content_encrypted[c_name]["db_name"] = encrypted_database
            content_encrypted[c_name]["username"] = encrypted_username
            content_encrypted[c_name]["password"] = encrypted_user_secret_key
            content_encrypted[c_name]["connection_code"] = connection_code
            with open(f"{PLATFORM_FILE_PATH}user_databases.json", "w") as f:
                json.dump(content_encrypted, f, indent=4)
                f.close()
            c_config["HOST"] = c_config["server"]
            c_config["PORT"] = c_config["port"]
            c_config["NAME"] = c_config["db_name"]
            c_config["USER"] = c_config["username"]
            c_config["PASSWORD"] = c_config["password"]

        del c_config["server"]
        del c_config["port"]
        del c_config["db_name"]
        del c_config["username"]
        del c_config["password"]
        if c_config["db_type"] == "MSSQL":
            del c_config["db_type"]
            try:
                quoted_temp = urllib.parse.quote_plus(
                    "driver={ODBC Driver 18 for SQL Server};server="
                    + c_config["HOST"]
                    + ","
                    + c_config["PORT"]
                    + ";database="
                    + c_config["NAME"]
                    + ";Uid="
                    + c_config["USER"]
                    + ";Pwd="
                    + c_config["PASSWORD"]
                    + ";Encrypt=yes;TrustServerCertificate=yes;Connect Timeout=60;"
                )
                engine_temp = create_engine(
                    f"mssql+pyodbc:///?odbc_connect={quoted_temp}",
                    pool_pre_ping=True,
                    pool_size=30,
                    max_overflow=10,
                    pool_recycle=900,
                    fast_executemany=False,
                )
                turb_connection = connect(
                    driver="ODBC Driver 18 for SQL Server",
                    server=c_config["HOST"] + "," + c_config["PORT"],
                    database=c_config["NAME"],
                    uid=c_config["USER"],
                    pwd=c_config["PASSWORD"] + ";Encrypt=yes;TrustServerCertificate=yes;",
                    turbodbc_options=make_options(
                        prefer_unicode=True,
                        use_async_io=True,
                        varchar_max_character_limit=10000000,
                        autocommit=True,
                    ),
                )
                database_engine_dict[c_name] = [engine_temp, turb_connection], "MSSQL"
            except Exception:
                pass
        elif c_config["db_type"] == "PostgreSQL":
            del c_config["db_type"]
            try:
                engine_temp = {
                    "dbname": c_config["NAME"],
                    "user": c_config["USER"],
                    "password": c_config["PASSWORD"],
                    "host": c_config["HOST"],
                    "port": c_config["PORT"],
                    "schema": c_config["schema"],
                }
                database_engine_dict[c_name] = [engine_temp, None], "PostgreSQL"
            except Exception:
                pass
        elif c_config["db_type"] == "Oracle":
            if c_config.get("db_connection_mode") == "thick":
                oracledb.init_oracle_client()
                thick_mode = True
            else:
                thick_mode = False
            engine_temp = create_engine(
                "oracle+oracledb://:@",
                thick_mode=thick_mode,
                connect_args={
                    "user": c_config["USER"],
                    "password": c_config["PASSWORD"],
                    "host": c_config["HOST"],
                    "port": c_config["PORT"],
                    "service_name": c_config["service_name"],
                },
                pool_pre_ping=True,
                pool_size=30,
                max_overflow=10,
                pool_recycle=900,
            )
            database_engine_dict[c_name] = [engine_temp, None], "Oracle"
        else:
            pass

DATABASES["default"]["ATOMIC_REQUESTS"] = True
DATABASE_ROUTERS = [
    "config.AuthRouter.AuthRouter",
]
DATE_FORMAT = "%d-%m-%Y"
DATE_INPUT_FORMATS = ["%d-%m-%Y"]
USE_I18N = True
USE_L10N = False
USE_TZ = True


# Tenant Host Mapper
tenant_host_mapper = {}
if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_host_mapping.json"):
    with open(f"{PLATFORM_FILE_PATH}tenant_host_mapping.json") as json_file:
        tenant_host_mapper = json.load(json_file)
        json_file.close()
else:
    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
            tenant_data = json.load(json_file)
            for t_name, t_config in tenant_data.items():
                if t_config.get("urlhost"):
                    if isinstance(t_config["urlhost"], list):
                        for url in t_config["urlhost"]:
                            tenant_host_mapper[url] = t_name
                    else:
                        tenant_host_mapper[t_config["urlhost"]] = t_name
            json_file.close()
    with open(f"{PLATFORM_FILE_PATH}tenant_host_mapping.json", "w") as out_file:
        json.dump(tenant_host_mapper, out_file, indent=4)
        out_file.close()


##Connection string for windows OS

##Connection string for Linux OS

quoted = urllib.parse.quote_plus(
    "driver={ODBC Driver 18 for SQL Server};server="
    + server
    + ","
    + port
    + ";database="
    + database
    + ";Uid="
    + username
    + ";Pwd="
    + password
    + ";Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"
)

central_database_config = {
    "dbname": database,
    "user": username,
    "password": password,
    "host": server,
    "port": port,
}

if database_type == "PostgreSQL":
    aps_engine = create_engine(f"postgresql+psycopg2://{username}:{password}@{server}:{port}/{database}")
    engine = {
        "dbname": database,
        "user": username,
        "password": password,
        "host": server,
        "port": port,
    }
    turbodbc_connection = {}
elif database_type == "MSSQL":
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={quoted}")
    turbodbc_connection = connect(
        driver="ODBC Driver 18 for SQL Server",
        server=server + "," + port,
        database=database,
        uid=username,
        pwd=password + ";Encrypt=yes;TrustServerCertificate=yes;",
        turbodbc_options=make_options(
            prefer_unicode=True, use_async_io=True, varchar_max_character_limit=100000000, autocommit=True
        ),
    )
else:
    engine = {}
    turbodbc_connection = {}


def get_tenants_map():
    tenants_data = {}
    with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
        tenants_data = json.load(json_file)
        json_file.close()
    return tenants_data


sql_config = {
    "server": server + "," + port,
    "database": "[" + database + "]",
    "schema": "[dbo]",
    "username": username,
    "password": password,
}

DISABLE_SERVER_SIDE_CURSORS = True

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
ASGI_APPLICATION = "config.asgi.application"

# CACHE
REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "RevolutioRedis@2023")
REDIS_URL = os.environ.get("REDIS_URL", "redis://:redissecretpassword@redis:6379/0")
redis_instance = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, password=REDIS_PASSWORD)
REDIS_DJANGO_CACHE = os.environ.get("REDIS_CACHE_LOCATION", "redis://127.0.0.1:6379")
REDIS_DJANGO_CACHE_PASSWORD = os.environ.get("KEYDB_PASSWORD", "RevolutioRedisKDB@2023")
REDIS_HOST_SCHEDULER = os.environ.get("REDIS_HOST_SCHEDULER", "127.0.0.1")
REDIS_PORT_SCHEDULER = os.environ.get("REDIS_PORT_SCHEDULER", "6379")
REDIS_PASSWORD_SCHEDULER = os.environ.get("REDIS_PASSWORD_SCHEDULER", "RevolutioRedisSc@2023")
redis_instance_scheduler = redis.StrictRedis(
    host=REDIS_HOST_SCHEDULER, port=REDIS_PORT_SCHEDULER, db=0, password=REDIS_PASSWORD_SCHEDULER
)
trusted_orgins = []
if os.path.exists(f"{PLATFORM_FILE_PATH}allowed_domains.json"):
    with open(f"{PLATFORM_FILE_PATH}allowed_domains.json") as json_file:
        trusted_orgins = json.load(json_file)
        json_file.close()
if os.environ.get("PLATFORM_DOMAIN_NAME"):
    trusted_orgins.append(
        f'{os.environ.get("ACCOUNT_DEFAULT_HTTP_PROTOCOL", "https")}://*.{os.environ.get("PLATFORM_DOMAIN_NAME")}'
    )
else:
    pass
CSRF_TRUSTED_ORIGINS = trusted_orgins

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_URL)],
        },
    },
}

# Queue
redis_queue = Queue(connection=redis_instance)
alerts_queue = Queue("alerts_queue", connection=redis_instance)
scheduler_queue = Queue("scheduled_job_queue", connection=redis_instance_scheduler)
system_scheduler_queue = Queue("system_scheduled_job_queue", connection=redis_instance_scheduler)
# TODO: set to whatever value is adequate in your circumstances
# TODO: set to whatever value is adequate in your circumstances

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    # "collectfast",
    "django.contrib.staticfiles",
    # "django.contrib.humanize", # Handy template tags
    "django.contrib.admin",
    "widget_tweaks",
    "misaka",
    "channels",
    "compressor",
    "cssmin",
    "jsmin",
]
THIRD_PARTY_APPS = [
    "crispy_forms",
    "crispy_bootstrap4",
    "djangocodemirror",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",  # for Google OAuth 2.0
    "allauth.socialaccount.providers.facebook",
    "allauth.socialaccount.providers.microsoft",
    "allauth.socialaccount.providers.twitter",
    # 'allauth.socialaccount.providers.apple',
    "allauth.socialaccount.providers.amazon",
    "rest_framework",
    "rest_framework_simplejwt",
    "webpack_loader",
    "bootstrap_datepicker_plus",
    "rules.apps.AutodiscoverRulesConfig",
    "django_pivot",
    "haystack",
    "schedule",
    "django.contrib.humanize",
    "storages",
    "corsheaders",
]

LOCAL_APPS = [
    "kore_investment.users.apps.UsersConfig",
    "tenant_admin.apps.TenantAdminConfig",
    "platform_admin.apps.PlatformAdminConfig",
    "kore_investment",
    # Your stuff: custom apps go here
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIGRATIONS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules
MIGRATION_MODULES = {"sites": "kore_investment.contrib.sites.migrations"}

# AUTHENTICATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    "rules.permissions.ObjectPermissionBackend",
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTStatelessUserAuthentication",
    )
}

SIMPLE_JWT = {
    # how long the original token is valid for
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(days=100),
}

LDAP_ACTIVATED = os.environ.get("LDAP_ACTIVATED", "false")

# LDAPBackend

if os.path.exists(f"{PLATFORM_FILE_PATH}ldap_configuration.json"):
    with open(f"{PLATFORM_FILE_PATH}ldap_configuration.json") as json_file:
        ldap_data = json.load(json_file)
        variableCounter = 1
        for tenant in ldap_data:
            if ldap_data[tenant]["activate_ldap"] == "true":
                exec(
                    f"AUTH_LDAP_{variableCounter}_SERVER_URI= ldap_data['{tenant}']['ldap_server_uri']"
                )  # AUTH_LDAP_1_SERVER_URI
                exec(f"AUTH_LDAP_{variableCounter}_BIND_DN = ldap_data['{tenant}']['ldap_bind_dn']")
                exec(
                    f"AUTH_LDAP_{variableCounter}_BIND_PASSWORD = ldap_data['{tenant}']['ldap_bind_password']"
                )
                ldap_user_search_criteria = ldap_data[tenant]["ldap_user_search_criteria"]
                if isinstance(ldap_data[tenant]["ldap_user_search_domain"], list):
                    ldap_user_search_str = "LDAPSearchUnion( "
                    for lusd in ldap_data[tenant]["ldap_user_search_domain"]:
                        ldap_user_search_str += (
                            f"LDAPSearch('{lusd}',ldap.SCOPE_SUBTREE,'{ldap_user_search_criteria}'), "
                        )
                    ldap_user_search_str += ")"
                else:
                    ldap_user_search_str = f"LDAPSearch(ldap_data['{tenant}']['ldap_user_search_domain'],ldap.SCOPE_SUBTREE,'{ldap_user_search_criteria}')"
                exec(f"AUTH_LDAP_{variableCounter}_USER_SEARCH = {ldap_user_search_str}")
                exec(
                    f"AUTH_LDAP_{variableCounter}_USER_ATTR_MAP = ldap_data['{tenant}']['ldap_user_attribute_mapping']"
                )
                AUTHENTICATION_BACKENDS.insert(
                    0, f"kore_investment.users.custombackend.CustomLDAPBackend{str(variableCounter)}"
                )

            variableCounter += 1


# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = "users.User"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url
LOGIN_REDIRECT_URL = "/users/selectApplication/"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = "/accounts/login/"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "kore_investment.utils.middlewares.HealthCheckMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "kore_investment.middleware.sessionCheckMiddleware.sessionCheckMiddleware",
    "kore_investment.middleware.db_connection_check_middleware.db_connection_middleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "kore_investment.middleware.audit_trail_middleware.AuditMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

if database_type == "PostgreSQL":
    MIDDLEWARE.insert(0, "kore_investment.middleware.tenant_middleware.MultitenantMiddleware")

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR.path("static"))

COMPRESS_ENABLED = True
COMPRESS_ROOT = STATIC_ROOT  ##django compressor
COMPRESS_OFFLINE = True
if not COMPRESS_ENABLED:  ##django compressor
    COMPRESS_ENABLED = True
    COMPRESS_CSS_FILTERS = ["compressor.filters.cssmin.CSSMinFilter"]
    COMPRESS_JS_FILTERS = ["compressor.filters.jsmin.JSMinFilter"]  ##django compressor


# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(APPS_DIR.path("static"))]
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR("media"))
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"


# CORS Whitelisting
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8080",
    "http://localhost:8080",
    *trusted_orgins,
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://\w+\.revolutio\.digital$",
    os.environ.get("CORS_ALLOWED_ORIGIN_REGEXES", r"^https://\w+\.revolutio\.digital$"),
]

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        "DIRS": [str(APPS_DIR.path("templates"))],
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "kore_investment.utils.context_processors.settings_context",
                "kore_investment.users.global_functions.application_list",
                "kore_investment.users.global_functions.current_application",
                "kore_investment.users.global_functions.sideNavBarLoad",
                "kore_investment.users.global_functions.breadcrumbs",
                "django.template.context_processors.request",
            ],
        },
    },
    {
        "NAME": "light",
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        "DIRS": [str(APPS_DIR.path("templates"))],
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "kore_investment.utils.context_processors.settings_context",
                "django.template.context_processors.request",
            ],
        },
    },
]
# http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = "bootstrap4"
MESSAGE_TAGS = {
    messages.DEBUG: "alert-info",
    messages.INFO: "alert-success",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}
# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
FIXTURE_DIRS = (str(APPS_DIR.path("fixtures")),)

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True

# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env("DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
# https://docs.djangoproject.com/en/2.2/ref/settings/#email-timeout
EMAIL_TIMEOUT = 5

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = "admin/"
# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [("""Srijan Raychaudhuri""", "srijanraychaudhuri@acies.consulting")]
# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "%(levelname)s %(asctime)s %(module)s " "%(process)d %(thread)d %(message)s"}
    },
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "./logs/logfile.log",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"level": "INFO", "handlers": ["file", "console"]},
}

#  WEBPACK CONFIG

WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": DEBUG,
        "BUNDLE_DIR_NAME": "webpack_bundles1/",  # must end with slash
        "STATS_FILE": str(ROOT_DIR.path("relation_canvas/webpack-stats.json")),
        "POLL_INTERVAL": 0.1,
        "TIMEOUT": None,
        "IGNORE": [r".+\.hot-update.js", r".+\.map"],
    },
    "HIERARCHY": {
        "CACHE": DEBUG,
        "BUNDLE_DIR_NAME": "webpack_bundles2/",  # must end with slash
        "STATS_FILE": str(ROOT_DIR.path("hierarchy_canvas/webpack-stats.json")),
        "POLL_INTERVAL": 0.1,
        "TIMEOUT": None,
        "IGNORE": [r".+\.hot-update.js", r".+\.map"],
    },
    "PLANNER": {
        "CACHE": DEBUG,
        "BUNDLE_DIR_NAME": "webpack_bundles3/",  # must end with slash
        "STATS_FILE": str(ROOT_DIR.path("planner/webpack-stats.json")),
        "POLL_INTERVAL": 0.1,
        "TIMEOUT": None,
        "IGNORE": [r".+\.hot-update.js", r".+\.map"],
    },
}

# AP Scheduler
SCHEDULER_AUTOSTART = os.environ.get("SCHEDULER_AUTOSTART", False)

DATA_UPLOAD_MAX_MEMORY_SIZE = 1086373952

# HAYSTACK SOLR

HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "haystack.backends.solr_backend.SolrEngine",
        "URL": "http://13.68.17.158:8983/solr/Revolutio",
    },
}
# BOWER

BOWER_COMPONENTS_ROOT = ROOT_DIR.path("components")

BOWER_INSTALLED_APPS = ("jquery", "jquery-ui", "bootstrap")


# django-allauth
# ------------------------------------------------------------------------------
ACCOUNT_ALLOW_REGISTRATION = env.bool("DJANGO_ACCOUNT_ALLOW_REGISTRATION", True)
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_AUTHENTICATION_METHOD = "username"
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_EMAIL_REQUIRED = False
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_EMAIL_VERIFICATION = "none"
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_ADAPTER = "kore_investment.users.adapters.AccountAdapter"
# https://django-allauth.readthedocs.io/en/latest/configuration.html
SOCIALACCOUNT_ADAPTER = "kore_investment.users.adapters.SocialAccountAdapter"

# AZURE STORAGE DETAILS

AZURE_ACCOUNT_NAME = "revolutiodatastore"

AZURE_ACCOUNT_KEY = "sp=racwd&st=2022-02-23T11:26:08Z&se=2022-02-23T19:26:08Z&spr=https&sv=2020-08-04&sr=c&sig=AeOePCsFDrubih5HIXEI0M55FGAcVHSuANnLW0y1Ddo%3D"

AZURE_OVERWRITE_FILES = "True"

AZURE_CONTAINER = "$web"

AZURE_URL_EXPIRATION_SECS = "300"

AZURE_LOCATION = "/static/"

CDN_CUSTOM_DOMAIN = os.environ.get("CDN_CUSTOM_DOMAIN", "")
if CDN_CUSTOM_DOMAIN:
    CDN_CUSTOM_LOCATION = os.environ.get("CDN_CUSTOM_LOCATION", "/static/")
    STATIC_URL = f"{CDN_CUSTOM_DOMAIN}/{CDN_CUSTOM_LOCATION}/"
    CORS_ALLOWED_ORIGINS.append(CDN_CUSTOM_DOMAIN)
else:
    STATIC_URL = f"/static/"


# EASY_AUDIT
DJANGO_EASY_AUDIT_UNREGISTERED_URLS_EXTRA = [
    r"^ws/queued_login_output/",
    r"^ws/queued_navbar_update/",
]
# django-compressor
# ------------------------------------------------------------------------------
# https://django-compressor.readthedocs.io/en/latest/quickstart/#installation
# Your stuff...
# ------------------------------------------------------------------------------

# NGINX

#    "PORT_NUMBER"
# ]  # To be changed based on the application link on the server {ABK:".com", CG:"4040"}
#                    pass
#                pass
#    pass


ACCOUNT_DEFAULT_HTTP_PROTOCOL = os.environ.get("ACCOUNT_DEFAULT_HTTP_PROTOCOL", "https")
