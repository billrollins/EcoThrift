# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from datetime import timedelta
import os
from decouple import config
from unipath import Path
from google.oauth2 import service_account

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE_DIR = Path(__file__).parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_1122')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# load production server from .env
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'www.ecothrift.us', 'www.ecothriftlife.com']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.home'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'
LOGIN_REDIRECT_URL = "home"  # Route defined in home/urls.py
LOGOUT_REDIRECT_URL = "home"  # Route defined in home/urls.py
TEMPLATE_DIR = os.path.join(BASE_DIR, "apps/templates")  # ROOT dir for templates

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.settings_context',
            ],
        },
    },
]


WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {

        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'd9h60aj6kuj49u',
        'USER': 'uangbgnigmgeft',
        'PASSWORD': '7bdd71e77c803e5a8d0b88db00b7d452144a364ea9337dd1f9cbd8b466cd52ed',
        'HOST': 'ec2-52-86-56-90.compute-1.amazonaws.com',
        'PORT': '5432',
    }
}

#
# Google Cloud Storage (GCS) Settings
#
    
GS_BUCKET_NAME = "django_web"    
DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"    
MEDIA_URL = "https://storage.cloud.google.com/django_web/" 

# May be not needed.  Looks like model path is saved in file fields
EMPLOYEE_MEDIA_URL = os.path.join(MEDIA_URL, 'employee/')

GS_CREDENTIALS = service_account.Credentials.from_service_account_file(os.path.join(BASE_DIR, 'ecothrift-web-2d1aa76a62eb.json'))
GS_EXPIRATION = timedelta(minutes=5)    
GS_BLOB_CHUNK_SIZE = 1024 * 256 * 40 # Needed for uploading large streams, entirely optional otherwise


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

#############################################################
# SRC: https://devcenter.heroku.com/articles/django-assets

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/


# App static files, relative path; needs to end in /
STATIC_URL = 'static/'

# Global static files, absolute path; doesn't end in /
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'apps/static')]

# Save static files to one directory: locally
STATIC_ROOT = os.path.join(CORE_DIR, 'staticfiles')

# Save static files to one directory: remote
STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'

#############################################################
#############################################################

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'