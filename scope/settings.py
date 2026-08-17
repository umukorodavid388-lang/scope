"""
Django settings for scope project.
"""

from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


# --- Security -----------------------------------------------------------
# SECRET_KEY and DEBUG now come from environment variables, not hardcoded.
# Locally: set these in your .env file.
# On Render: set these in the Web Service's Environment tab.
SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS", "localhost,127.0.0.1"
).split(",")
# On Render, set ALLOWED_HOSTS=yourapp.onrender.com in the dashboard.


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "accounts",
    "videophotography",
    "dashboard",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # moved up, right after security — required order
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'scope.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "dashboard.context_processors.notifications",
            ],
        },
    },
]

WSGI_APPLICATION = 'scope.wsgi.application'
AUTH_USER_MODEL = "accounts.User"


# --- Database -------------------------------------------------------------
# Locally: falls back to your local Postgres if DATABASE_URL isn't set.
# On Render: DATABASE_URL is provided automatically once you link the
# Postgres database to this Web Service — no other change needed here.
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get(
            "DATABASE_URL",
            "postgres://postgres:PASSWORD@localhost:5432/videographyer_db",
        )
    )
}
# ^ For local dev, put your real local DB credentials in .env as
#   DATABASE_URL=postgres://postgres:yourpassword@localhost:5432/videographyer_db
#   instead of hardcoding them here.


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# --- Static & media files ---------------------------------------------
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
# ^ whitenoise setting so collectstatic output is compressed & cache-busted
#   in production. Safe to leave in for local dev too.

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
# Reminder: on Render this folder is wiped on every redeploy — see the
# about_video_url field on SiteContent for the workaround already built in.

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- Email ----------------------------------------------------------------
# No hardcoded fallback values here anymore — every real credential comes
# only from .env locally, or Render's Environment tab in production.
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)
CONTACT_INBOX_EMAIL = os.environ.get("CONTACT_INBOX_EMAIL", DEFAULT_FROM_EMAIL)