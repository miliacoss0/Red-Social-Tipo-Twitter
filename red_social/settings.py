"""
Django settings for red_social project.
"""

import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']  

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-q27k@v@$u@)#jl)#ci0v=0vq_m)cdrag(6s4-$v!x^)^ao0165'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'posts',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    'usuarios',
    'tweets',
    'follows',
    'mensajes',
]
#cloudinary
INSTALLED_APPS += [
    'cloudinary_storage',
    'cloudinary',
    'channels',
]

import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary_storage.storage import MediaCloudinaryStorage

# Configuración de Cloudinary
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': env('CLOUDINARY_API_KEY'),
    'API_SECRET': env('CLOUDINARY_API_SECRET'),
    'EXIF_DISPLAY': True,
}

cloudinary.config(
    cloud_name=env('CLOUDINARY_CLOUD_NAME'),
    api_key=env('CLOUDINARY_API_KEY'),
    api_secret=env('CLOUDINARY_API_SECRET'),
    secure=True
)

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

STORAGES = {
    'default': {
        'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

print(f" Cloudinary configurado con cloud_name: {CLOUDINARY_STORAGE['CLOUD_NAME']}")

# configuración de sitio
SITE_ID = 1

# backend de autorización
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# confi de github
SOCIALACCOUNT_PROVIDERS = {
    'github': {
        'SCOPE': ['user:email', 'read:user'],
        'APP': {
            'client_id': 'Ov23liUwVnQLW5qIr3nU',
            'secret': '0c13ba8e9ff76cd292d8fab79e5b1ba483e02984',
        },
        'VERIFIED_EMAIL': True,
    }
}

# confi de cuentas
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_EMAIL_VERIFICATION = 'optional'

# REDIRECCIONES
LOGIN_REDIRECT_URL = '/feed/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'red_social.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'red_social.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'red_social_db',
        'USER': 'postgres',
        'PASSWORD': '1',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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

# cache con redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{env("REDIS_HOST", default="localhost")}:{env("REDIS_PORT", default="6379")}/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'timeout': 20,
            },
        },
        'KEY_PREFIX': 'redsocial',
    }
}

# session engine con cache
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# django channels
ASGI_APPLICATION = 'red_social.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(env('REDIS_HOST', default='localhost'), int(env('REDIS_PORT', default='6379')))],
        },
    },
}

# Internationalization
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Asuncion'
USE_I18N = True
USE_TZ = True

SOCIALACCOUNT_ADAPTER = 'usuarios.adapter.CustomSocialAccountAdapter'

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'templates/tweets/static'),
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')