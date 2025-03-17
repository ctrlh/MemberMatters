"""
Django settings for membermatters project.

Generated by "django-admin startproject" using Django 2.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import sys
import os
import json
from datetime import timedelta
from multiprocessing import Process
import logging
from .constance_config import CONSTANCE_CONFIG_FIELDSETS, CONSTANCE_CONFIG

logger = logging.getLogger("settings.py")


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = os.environ.get(
    "MM_SECRET_KEY", "l)#t68rzepzp)0l#x=9mntciapun$whl+$j&=_@nl^zl1xm3j*"
)

# Default config is for dev environments and is overwritten in prod
DEBUG = True
ENVIRONMENT = "Development"
ALLOWED_HOSTS = ["*"]
SESSION_COOKIE_HTTPONLY = False
SESSION_COOKIE_SAMESITE = None
CSRF_COOKIE_SAMESITE = None
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

### mozilla-django-oidc config
# get these from your IDP
OIDC_RP_CLIENT_ID = os.environ.get("MM_OIDC_CLIENT_ID", None)
OIDC_RP_CLIENT_SECRET = os.environ.get("MM_OIDC_CLIENT_SECRET", None)
OIDC_OP_AUTHORIZATION_ENDPOINT = os.environ.get(
    "MM_OIDC_OP_AUTHORIZATION_ENDPOINT", None
)
OIDC_OP_TOKEN_ENDPOINT = os.environ.get("MM_OIDC_OP_TOKEN_ENDPOINT", None)
OIDC_OP_USER_ENDPOINT = os.environ.get("MM_OIDC_OP_USER_ENDPOINT", None)
# Set the following to False if you want your MM admin to create a user & profile (matches on email address) instead of creating from the Idp
OIDC_CREATE_USER = os.environ.get("MM_OIDC_CREATE_USER", True)
# Extend token validity window, default is 15 minutes
OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS = os.environ.get("MM_OIDC_TOKEN_EXPIRY", 3600)
# Want the user's profile scope to populate the Membermatters profile
OIDC_RP_SCOPES = "openid email profile"

# this allows the frontend dev server to talk to the dev server
CORS_ALLOW_ALL_ORIGINS = True

if os.environ.get("MM_ENV") == "Production":
    ENVIRONMENT = "Production"
    CORS_ALLOW_ALL_ORIGINS = False
    DEBUG = False

# Application definition
INSTALLED_APPS = [
    "constance",
    "constance.backends.database",
    "django_prometheus",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "oidc_provider",
    "channels",
    "profile",
    "access",
    "group",
    "memberbucks",
    "api_spacedirectory",
    "api_general",
    "api_access",
    "api_meeting",
    "api_admin_tools",
    "api_billing",
    "api_metrics",
    "corsheaders",
    "rest_framework",
    "rest_framework_api_key",
    "django_celery_results",
    "django_celery_beat",
    "import_export",
    "mozilla_django_oidc",
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "membermatters.oidc_client_settings.CustomOIDCAB",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "membermatters.middleware.Sentry",
    "membermatters.middleware.ForceCsrfCookieMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
    "mozilla_django_oidc.middleware.SessionRefresh",
]

ROOT_URLCONF = "membermatters.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "constance.context_processors.config",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ASGI_APPLICATION = "membermatters.asgi.application"

if ENVIRONMENT == "Production":
    if os.getenv("MM_REDIS_HOST"):
        logger.info("Using Redis for channels layer")
        CHANNEL_LAYERS = {
            "default": {
                # Via local Redis
                "BACKEND": "channels_redis.core.RedisChannelLayer",
                "CONFIG": {
                    "hosts": [os.getenv("MM_REDIS_HOST")],
                },
            },
        }
    else:
        logger.warning("No Redis host found, falling back to in-memory channels layer")
        CHANNEL_LAYERS = {
            "default": {
                # Via In-memory channel layer
                "BACKEND": "channels.layers.InMemoryChannelLayer"
            },
        }

else:
    CHANNEL_LAYERS = {
        "default": {
            # Via In-memory channel layer
            "BACKEND": "channels.layers.InMemoryChannelLayer"
        },
    }

if "MM_USE_POSTGRES" in os.environ:
    DATABASES = {
        "default": {
            "ENGINE": "django_prometheus.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "membermatters"),
            "USER": os.environ.get("POSTGRES_USER", "membermatters"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "membermatters"),
            "HOST": os.environ.get(
                "POSTGRES_HOST", "mm-postgres"
            ),  # default for docker-compose - change if needed
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }

elif "MM_USE_MYSQL" in os.environ:
    DATABASES = {
        "default": {
            "ENGINE": "django_prometheus.db.backends.mysql",
            "NAME": os.environ.get("MYSQL_DB", "membermatters"),
            "USER": os.environ.get("MYSQL_USER", "membermatters"),
            "PASSWORD": os.environ.get("MYSQL_PASSWORD", "membermatters"),
            "HOST": os.environ.get("MYSQL_HOST", "mm-mysql"),
            "PORT": os.environ.get("MYSQL_PORT", "3306"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django_prometheus.db.backends.sqlite3",
            "NAME": os.environ.get("MM_DB_LOCATION", "/usr/src/data/db.sqlite3"),
        }
    }

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    {
        "NAME": "pwned_passwords_django.validators.PwnedPasswordsValidator",
    },
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "console": {
            "format": "%(asctime)s %(name)s %(filename)s:%(lineno)s  %(levelname)-8s %(message)s"
        },
        "file": {
            "format": "%(asctime)s %(name)s %(filename)s:%(lineno)s  %(levelname)-8s %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "console",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.environ.get("MM_LOG_LOCATION", "/usr/src/logs/django.log"),
            "maxBytes": 10000000,
            "backupCount": 10,
            "formatter": "file",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "WARNING",
            "propagate": False,
        },
        "access": {
            "handlers": ["console", "file"],
            "level": os.environ.get("MM_LOG_LEVEL_ACCESS", "INFO"),
            "propagate": False,
        },
        "billing": {
            "handlers": ["console", "file"],
            "level": os.environ.get("MM_LOG_LEVEL_BILLING", "INFO"),
            "propagate": False,
        },
        "general": {
            "handlers": ["console", "file"],
            "level": os.environ.get("MM_LOG_LEVEL_GENERAL", "INFO"),
            "propagate": False,
        },
        "settings.py": {
            "handlers": ["console", "file"],
            "level": os.environ.get("MM_LOG_LEVEL_SETTINGS", "INFO"),
            "propagate": False,
        },
        "profile": {
            "handlers": ["console", "file"],
            "level": os.environ.get("MM_LOG_LEVEL_PROFILE", "INFO"),
            "propagate": False,
        },
        "discord": {
            "handlers": ["console", "file"],
            "level": os.environ.get("MM_LOG_LEVEL_DISCORD", "INFO"),
            "propagate": False,
        },
        "slack": {
            "handlers": ["console", "file"],
            "level": os.environ.get("MM_LOG_LEVEL_SLACK", "INFO"),
            "propagate": False,
        },
        "emails": {
            "handlers": ["console", "file"],
            "level": os.environ.get("MM_LOG_LEVEL_EMAILS", "INFO"),
            "propagate": False,
        },
        "sms": {
            "handlers": ["console", "file"],
            "level": os.environ.get("MM_LOG_LEVEL_SMS", "INFO"),
            "propagate": False,
        },
        "api_general:tasks": {
            "handlers": ["console", "file"],
            "level": os.environ.get("MM_LOG_LEVEL_GENERAL_TASKS", "INFO"),
            "propagate": False,
        },
        "api_access:tasks": {
            "handlers": ["console", "file"],
            "level": os.environ.get("MM_LOG_LEVEL_ACCESS_TASKS", "INFO"),
            "propagate": False,
        },
        "celery:api_metrics": {
            "handlers": ["console", "file"],
            "level": os.environ.get("MM_LOG_LEVEL_CELERY_METRICS", "INFO"),
            "propagate": False,
        },
        "api_member_bucks": {
            "handlers": ["console", "file"],
            "level": os.environ.get("MM_LOG_LEVEL_MEMBER_BUCKS", "INFO"),
            "propagate": False,
        },
        "api_spacedirectory": {
            "handlers": ["console", "file"],
            "level": os.environ.get("MM_LOG_LEVEL_SPACEDIRECTORY", "INFO"),
            "propagate": False,
        },
        "api_member_tools": {
            "handlers": ["console", "file"],
            "level": os.environ.get("MM_LOG_LEVEL_MEMBER_TOOLS", "INFO"),
            "propagate": False,
        },
        "metrics": {
            "handlers": ["console", "file"],
            "level": os.environ.get("MM_LOG_LEVEL_METRICS", "INFO"),
            "propagate": False,
        },
        "celery:celeryapp": {
            "handlers": ["console", "file"],
            "level": os.environ.get("MM_LOG_LEVEL_CELERY_APP", "INFO"),
            "propagate": False,
        },
        "oidc_provider": {
            "handlers": ["console", "file"],
            "level": os.environ.get("MM_LOG_LEVEL_OIDC_PROVIDER", "INFO"),
            "propagate": False,
        },
        "mozilla_django_oidc": {
            "handlers": ["console", "file"],
            "level": os.environ.get("MM_LOG_LEVEL_OIDC_CLIENT", "INFO"),
            "propagate": False,
        },
        "daphne": {"handlers": ["console", "file"], "level": "WARNING"},
    },
}

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "membermatters.custom_exception_handlers.fix_401",
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=365),
    "ROTATE_REFRESH_TOKENS": True,
    "UPDATE_LAST_LOGIN": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUTH_HEADER_TYPES": "Bearer",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
}

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = os.getenv("MM_LANGUAGE_CODE", "en-au")

TIME_ZONE = os.getenv("MM_TIME_ZONE", "Australia/Brisbane")
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.environ.get(
    "MM_STATIC_LOCATION", "/usr/src/app/memberportal/membermatters/static"
)
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/login"
MEDIA_URL = "/media/"
MEDIA_ROOT = os.environ.get("MM_MEDIA_LOCATION", "/usr/src/data/media/")

AUTH_USER_MODEL = "profile.User"

REQUEST_TIMEOUT = 0.05

# Celery configuration
CELERY_RESULT_BACKEND = "django-db"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_BROKER_URL = os.getenv("MM_REDIS_HOST")

# Django constance configuration
CONSTANCE_BACKEND = "membermatters.constance_backend.DatabaseBackend"
CONSTANCE_CONFIG = CONSTANCE_CONFIG
CONSTANCE_CONFIG_FIELDSETS = CONSTANCE_CONFIG_FIELDSETS

OIDC_USERINFO = "membermatters.oidc_provider_settings.userinfo"
OIDC_EXTRA_SCOPE_CLAIMS = "membermatters.oidc_provider_settings.CustomScopeClaims"

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Enable celery events for danihodovic/celery-exporter
CELERY_WORKER_SEND_TASK_EVENTS = True
CELERY_TASK_SEND_SENT_EVENT = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Needed for testing OIDC on local development environment with ngrok (oauth requires HTTPS)
# SITE_URL = "https://1bd0-122-148-148-138.ngrok-free.app"
