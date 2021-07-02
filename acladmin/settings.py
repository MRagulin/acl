"""
Django settings for acladmin project.

Generated by 'django-admin startproject' using Django 3.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = '#8g9jc-u$r!z83lc1bi!e+wif&n^u+*0yy3otebb19lbu)2@dy'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

APPROVE = 'APPROVE_PERSON'

ALLOWED_HOSTS = ['*']
SESSION_SAVE_EVERY_REQUEST = True

# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'fontawesome-free',
    'ownerlist',
    'accesslist',
    'acladmin',
    'django_python3_ldap',
    'django.contrib.admin',
    'panel'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'acladmin.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ]
        ,
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

WSGI_APPLICATION = 'acladmin.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'aclproject',
        'USER':'postgres',
        'PASSWORD':'ABCabc123',
        'HOST': '127.0.0.1',
        'PORT':'5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
#STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

if os.name == 'nt':
    LOGPATH = os.path.join(BASE_DIR, 'log\\debug.log')
else:
    LOGPATH = os.path.join(BASE_DIR, 'log//debug.log')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters':
        {
            'file': {
                'format': '%(levelname)s|%(asctime)s|%(module)s|%(process)d|%(filename)s|%(lineno)d|%(message)s',
                'datefmt': '%d/%b/%Y %H:%M:%S'
                    }
         },

    'handlers': {
        'file': {
                'level': 'DEBUG', #WARNING
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': LOGPATH,
                'maxBytes': 1024*1024*5, # 5MB
                'backupCount': 0,
                'formatter': 'file',
        },
        "console": {
            "class": "logging.StreamHandler",
        },
    },

    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'DEBUG', #WARNING
            'propagate': True,
        },

        "django_python3_ldap": {
            "handlers": ["file"],
            "level": "WARNING",
        },
    },
}


LOGIN_REDIRECT_URL = '/acl/welcome/'

AUTHENTICATION_BACKENDS = (
    "accesslist.auth.MyAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
    "django_python3_ldap.auth.LDAPBackend",


)
LDAP_AUTH_URL = "ldap://dc8.vesta.ru:389"
LDAP_AUTH_USE_TLS = True
LDAP_AUTH_SEARCH_BASE = "ou=Back1,dc=vesta,dc=ru"

LDAP_AUTH_OBJECT_CLASS = "organizationalPerson"
#LDAP_AUTH_OBJECT_CLASS = "inetOrgPerson"

LDAP_AUTH_USER_FIELDS = {
    "username": "sAMAccountName",
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
    "phone": "homephone",
    "department": "departament",
    "full_name": "displayname",
    "mphone": "telephonenumber",
    "ad_groups": "group_dns",

}


LDAP_AUTH_USER_LOOKUP_FIELDS = ("username",)
LDAP_AUTH_CLEAN_USER_DATA = "django_python3_ldap.utils.clean_user_data"
LDAP_AUTH_SYNC_USER_RELATIONS = "django_python3_ldap.utils.sync_user_relations"
LDAP_AUTH_FORMAT_SEARCH_FILTERS = "django_python3_ldap.utils.format_search_filters"
LDAP_AUTH_FORMAT_USERNAME = "django_python3_ldap.utils.format_username_active_directory_principal"
LDAP_AUTH_ACTIVE_DIRECTORY_DOMAIN = "vesta.ru"
LDAP_AUTH_CONNECTION_USERNAME = 'aduser'
LDAP_AUTH_CONNECTION_PASSWORD = 'adpassword'



