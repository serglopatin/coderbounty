"""
Django settings for coderbounty project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import os
import dj_database_url
import sys
from django.http import Http404

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

TESTING = sys.argv[1:2] == ["test"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "ci7svvv6wp+5cyk3(ju6w*6v-xldo#an3e3zuvg&&7@v=4*2^c"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ADMINS = (
    ("AdminEmail", os.environ.get("ADMIN_EMAIL", "me@me.com")),
    ("AdminEmail", os.environ.get("ADMIN_EMAIL", "me@me.com")),
)

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))


ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.bitbucket",
    "actstream",
    "website",
    "rest_framework",
    "import_export",
)

SITE_ID = 1


MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "rollbar.contrib.django.middleware.RollbarNotifierMiddleware",
]


ROOT_URLCONF = "coderbounty.urls"

WSGI_APPLICATION = "coderbounty.wsgi.application"

AUTH_PROFILE_MODULE = "UserProfile"


AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "coderbounty",
        "USER": os.environ.get("PGUSER", "postgres"),
        "PASSWORD": os.environ.get("PGPASSWORD", "postgres"),
        "HOST": "127.0.0.1",
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#         'NAME': 'coderbounty.db',                       # Or path to database file if using sqlite3.
#         'USER': '',                       # Not used with sqlite3.
#         'PASSWORD': '',                   # Not used with sqlite3.
#         'HOST': '',                       # Set to empty string for localhost. Not used with sqlite3.
#         'PORT': '',                       # Set to empty string for default. Not used with sqlite3.
#     }
# }


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True


EMAIL_HOST = "localhost"
EMAIL_PORT = 1025
# python -m smtpd -n -c DebuggingServer localhost:1025

if "DATABASE_URL" in os.environ:
    DEBUG = False
    DATABASES["default"] = dj_database_url.config()
    DATABASES["default"]["ENGINE"] = "django.db.backends.postgresql_psycopg2"
    ROLLBAR = {
        "access_token": os.environ.get(
            "ROLLBAR_ACCESS_TOKEN", "f25f82658f7c493f8eeeb271a817345c"
        ),
        "environment": "development" if DEBUG else "production",
        "root": BASE_DIR,
        "exception_level_filters": [(Http404, "warning")],
    }
    import rollbar

    rollbar.init(**ROLLBAR)
    EMAIL_HOST = "smtp.sendgrid.net"
    EMAIL_HOST_USER = os.environ.get("SENDGRID_USERNAME", "blank")
    EMAIL_HOST_PASSWORD = os.environ.get("SENDGRID_PASSWORD", "blank")
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True


# local dev needs to set SMTP backend or fail at startup
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Allow all host headers
ALLOWED_HOSTS = ["*"]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "none"


SOCIALACCOUNT_PROVIDERS = {"github": {"SCOPE": ["user:email"]}}

# python -m smtpd -n -c DebuggingServer localhost:1025

# TODO: remove wepay
WEPAY_IN_PRODUCTION = os.environ.get("WEPAY_IN_PRODUCTION", not DEBUG)
WEPAY_ACCOUNT_ID = os.environ.get("WEPAY_ACCOUNT_ID", "941349")
WEPAY_ACCESS_TOKEN = os.environ.get(
    "WEPAY_ACCESS_TOKEN",
    "STAGE_9c8476245785f470fd87b6bb1fad6ccb5c6cae5522337c378b7b0984d909401d",
)


SLACK_API_TOKEN = os.environ.get("SLACK_API_TOKEN", "token-123")

CLIENT_ID = os.environ.get("CLIENT_ID", "PAYPAL_CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET", "PAYPAL_CLIENT_SECRET")
MODE = os.environ.get("MODE", "sandbox")

GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "coderbounty-cowboy")
GITHUB_PASSWORD = os.environ.get("GITHUB_PASSWORD", "removed")

GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID", "GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET", "GITHUB_CLIENT_SECRET")

PAYPAL_SANDBOX_EMAIL = os.environ.get("PAYPAL_SANDBOX_EMAIL", "PAYPAL_SANDBOX_EMAIL")
PAYPAL_SANDBOX_PASSWORD = os.environ.get(
    "PAYPAL_SANDBOX_PASSWORD", "PAYPAL_SANDBOX_PASSWORD"
)

STATIC_ROOT = "staticfiles"
STATIC_URL = "/static/"

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

# TEMPLATE_DIRS = (PROJECT_PATH + "/templates/",)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": DEBUG,
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.media",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_MAX_AGE = 432000

LOGIN_REDIRECT_URL = "/profile/"

ACTSTREAM_SETTINGS = {
    "USE_JSONFIELD": False,
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "mail_admins": {"level": "ERROR", "class": "django.utils.log.AdminEmailHandler"}
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}

ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda u: "/profile/%s/" % u.username,
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


def get_cache():
    import os

    try:
        os.environ["MEMCACHE_SERVERS"] = os.environ["MEMCACHIER_SERVERS"].replace(
            ",", ";"
        )
        os.environ["MEMCACHE_USERNAME"] = os.environ["MEMCACHIER_USERNAME"]
        os.environ["MEMCACHE_PASSWORD"] = os.environ["MEMCACHIER_PASSWORD"]
        return {
            "default": {
                "BACKEND": "django_pylibmc.memcached.PyLibMCCache",
                "TIMEOUT": 500,
                "BINARY": True,
                "OPTIONS": {"tcp_nodelay": True},
            }
        }
    except:
        return {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}


CACHES = get_cache()