"""
Django settings for dtr5 project.

Generated by 'django-admin startproject' using Django 1.8.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

# Import "secret" settings.
from .settings_secrets import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

if DEBUG:
    CANONICAL_HOST = 'http://localhost:8000'
else:
    CANONICAL_HOST = 'http://www.redddate.com'

LOGIN_URL = CANONICAL_HOST + '/'

AUTHENTICATION_BACKENDS = (
    # 'django.contrib.auth.backends.ModelBackend',  # default
    # 'django.contrib.auth.backends.RemoteUserBackend',
    'simple_reddit_oauth.backends.RedditBackend',
)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'simple_reddit_oauth',
    'dtr5app',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'dtr5.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dtr5.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'


# Write all logging to the console, including logleves INFO and DEBUG,
# when DEBUG is True.
# See https://docs.djangoproject.com/en/1.8/topics/logging/
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

# Settings for user profile data.
SEX = (
    (0, 'other'),
    (1, 'woman who likes men'),
    (2, 'woman who likes women'),
    (3, 'woman who likes queer'),
    (4, 'man who likes women'),
    (5, 'man who likes men'),
    (6, 'man who likes queer'),
    (7, 'queer who likes women'),
    (8, 'queer who likes men'),
    (9, 'queer who likes queer'),
)
SEX_SYMBOL = (  # ♀♂⚥⚢⚣⚤⚪★☆⮕♥
    (0, '⚪'),
    (1, '♀♥♂'),
    (2, '♀♥♀'),
    (3, '♀♥⚥'),
    (4, '♂♥♀'),
    (5, '♂♥♂'),
    (6, '♂♥⚥'),
    (7, '⚥♥♀'),
    (8, '⚥♥♂'),
    (9, '⚥♥⚥'),
)
# Number of user IDs to load into session cache.
SEARCH_RESULTS_BUFFER_SIZE = 100
LINKS_IN_PROFILE_HEADER = 5
RESULTS_BUFFER_LEN = 20 if DEBUG else 1000
# Ignore subreddits too small or too large.
SR_MIN_SUBS = 100
SR_MAX_SUBS = 5000000
# How many subreddits to use at a time to find matches.
SR_LIMIT = 50
# How many favorite subreddits can a user select.
SR_FAVS_COUNT_MAX = 10

# Public settings for Reddit oAuth access.
OAUTH_REDDIT_REDIRECT_URI = CANONICAL_HOST + "/account/redditcallback/"
OAUTH_REDDIT_REDIRECT_AUTH_SUCCESS = CANONICAL_HOST + "/me/"
OAUTH_REDDIT_REDIRECT_AUTH_ERROR = LOGIN_URL
# Comma-separated list of API access scope with any of:
# identity edit flair history modconfig modflair modlog
# modposts modwiki mysubreddits privatemessages read report
# save submit subscribe vote wikiedit wikiread
OAUTH_REDDIT_SCOPE = "identity,mysubreddits"
OAUTH_REDDIT_DURATION = "permanent"  # or "temporary"
OAUTH_REDDIT_BASE_HEADERS = {
    "User-Agent": OAUTH_REDDIT_USER_AGENT, "raw_json": "1", }
