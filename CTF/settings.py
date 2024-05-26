import os
from pathlib import Path

from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = "django-insecure-gte39m!pnxhrdz4a3@xl5v(n-%t!q(u94+*zm-(r%lyk$$$99#"

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "ctf.local", "172.16.11.63"]

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "main.apps.MainConfig",
    "challenge.apps.ChallengeConfig",
    "chart.apps.ChartConfig",
    "admin_tools.apps.AdminToolsConfig",
    "bookstore.apps.BookstoreConfig",
    "rosetta",
    "parler",
]

ASGI_APPLICATION = "CTF.asgi.application"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "CTF.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

PARLER_LANGUAGES = {
    None: (
        {"code": "en"},
        {"code": "ru"},
        {"code": "tk"},
    ),
    "default": {
        "fallback": "en",
        "hide_untranslated": False,
    },
}

WSGI_APPLICATION = "CTF.wsgi.application"

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.mysql",
#         "OPTIONS": {
#             "sql_mode": "traditional",
#         },
#         "NAME": "ctf",
#         "USER": "afych",
#         "PASSWORD": "useradmin",
#         "HOST": "localhost",
#         "PORT": "3306",
#     }
# }


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

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
]


LANGUAGES = [
    ("en", _("English")),
    ("ru", _("Russian")),
    ("tk", _("Turkmen")),
]

LANGUAGE_CODE = "en"

TIME_ZONE = "Asia/Tashkent"

USE_I18N = True

USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

try:
    from django.contrib.messages import constants as messages

    MESSAGE_TAGS = {
        messages.DEBUG: "alert-info",
        messages.INFO: "alert-info",
        messages.SUCCESS: "alert-success",
        messages.WARNING: "alert-warning",
        messages.ERROR: "alert-danger",
    }
except Exception as e:
    pass


AUTH_USER_MODEL = "main.User"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"
