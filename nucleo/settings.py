"""
Django settings for nucleo project.

Generated by 'django-admin startproject' using Django 1.11.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import boto3, os

from base64 import b64decode

from stellar_base import horizon, keypair


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

ENV_TYPE = os.environ.get('ENV_TYPE') # to distinguish between dev v.s. prod
ENV_NAME = os.environ.get('ENV_NAME') # to distinguish between web v.s. work(er)

# SECURITY WARNING: don't run with debug turned on in production!
if ENV_TYPE == 'prod':
    DEBUG = False
else:
    DEBUG = True


if ENV_TYPE == 'dev':
    # Defaults: see https://docs.djangoproject.com/en/2.0/ref/settings/#allowed-hosts
    ALLOWED_HOSTS = [ ]
elif ENV_NAME == 'work':
    # Localhost set for aws worker tier and HTTP needed
    ALLOWED_HOSTS = [ 'localhost' ]
else:
    # Otherwise, usual django settings with HTTPS
    ALLOWED_HOSTS = [ '.nucleo.fi' ]

    # PROD SECURITY
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_SSL_REDIRECT = True

    CSRF_COOKIE_HTTPONLY = True
    X_FRAME_OPTIONS = 'DENY'


# For debug available in template context
INTERNAL_IPS = [ '127.0.0.1' ]

# For error notifications when DEBUG = False
ADMINS = [('Admin', os.environ.get('ADMIN_EMAIL'))]

# Application definition

INSTALLED_APPS = [
    'nc.apps.NcConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sites',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djangobower',
    'webpack_loader',
    'rest_framework',
    'rest_framework.authtoken',
    'bootstrapform',
    'bootstrap3',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'betterforms',
    'algoliasearch_django',
    'stream_django',
    'timeseries',
    'django_celery_results',
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

ROOT_URLCONF = 'nucleo.urls'

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

WSGI_APPLICATION = 'nucleo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

if os.environ.get('RDS_DB_NAME', None): # for production
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('RDS_DB_NAME'),
            'USER': os.environ.get('RDS_USERNAME'),
            'PASSWORD': os.environ.get('RDS_PASSWORD'),
            'HOST': os.environ.get('RDS_HOSTNAME'),
            'PORT': os.environ.get('RDS_PORT'),
        }
    }
else: # for local dev
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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

# Auth
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/feed/activity/'
SIGNUP_REDIRECT_URL = '/accounts/signup/profile/update/'
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# All-auth
ACCOUNT_ADAPTER = 'nc.adapter.AccountAdapter'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = SIGNUP_REDIRECT_URL
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = SIGNUP_REDIRECT_URL
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_REDIRECT_URL = LOGIN_URL
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_SESSION_REMEMBER = False
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Admin
ADMIN_PATH = os.environ.get('DJANGO_ADMIN_PATH')


# Email
if ENV_TYPE == 'prod':
    EMAIL_HOST = os.environ.get('SES_HOSTNAME')
    EMAIL_HOST_USER = os.environ.get('SES_USERNAME')
    EMAIL_HOST_PASSWORD = os.environ.get('SES_PASSWORD')
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = 'Nucleo <notification@mail.nucleo.fi>'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder',
]
STATICFILES_DIRS = [
    # Webpack: We do this so that django's collectstatic copies over our bundles to
    # the STATIC_ROOT or syncs them to whatever storage we use.
    os.path.join(BASE_DIR, 'assets'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Storages settings
if ENV_TYPE == 'prod':
    MEDIAFILES_LOCATION = 'media'
    DEFAULT_FILE_STORAGE = 'custom_storages.MediaStorage'

    STATICFILES_LOCATION = 'static'
    STATICFILES_STORAGE = 'custom_storages.StaticStorage'

    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_QUERYSTRING_AUTH = False


# UPLOAD SIZE MAX (10 MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10*1024**2

# Sites Framework
SITE_ID = 1

# Bower
BOWER_COMPONENTS_ROOT = BASE_DIR + '/components/'
BOWER_INSTALLED_APPS = (
    'stellar-sdk',
    'js-cookie',
    'moment',
    'moment-timezone',
    'numeral',
    'ladda-bootstrap',
    'highcharts',
    'bignumber.js',
    'getstream',
    'lodash',
)

# Webpack
# NOTE: https://owais.lone.pw/blog/webpack-plus-reactjs-and-django/
# NOTE: Before deploy, execute cmds
# python manage.py bower install
# ./node_modules/.bin/webpack --config webpack.config.js

# Algolia
ALGOLIA = {
    'APPLICATION_ID': os.environ.get('ALGOLIA_APPLICATION_ID'),
    'API_KEY': os.environ.get('ALGOLIA_API_KEY'),
    'SEARCH_API_KEY': os.environ.get('ALGOLIA_SEARCH_API_KEY'),
    'INDEX_SUFFIX': ENV_TYPE,
}

# AWS
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION')

# Initialize a client for decrypting sensitive environment vars
# https://dzone.com/articles/aws-lambda-encrypted-environment-variables
kms_client = boto3.client(
    'kms',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

# Task queues
CELERY_RESULT_BACKEND = 'django-db'
if DEBUG:
    QUEUE_BACKEND = 'nc.queues.backends.celery.CeleryQueueBackend'
else:
    # AWS SQS Settings
    QUEUE_BACKEND = 'nc.queues.backends.sqsboto3.SQSBoto3QueueBackend'
    AWS_SQS_BROKER_URL = os.environ.get('AWS_SQS_BROKER_URL')
    AWS_SQS_REGION_NAME = os.environ.get('AWS_SQS_REGION_NAME')

# Stellar
STELLAR_ISSUING_KEY_PAIR = keypair.Keypair.from_seed(
    kms_client.decrypt(
        CiphertextBlob=b64decode(os.environ.get('STELLAR_ENCRYPTED_ISSUING_SECRET_SEED'))
    )['Plaintext']
)
STELLAR_BASE_KEY_PAIR = keypair.Keypair.from_seed(
    kms_client.decrypt(
        CiphertextBlob=b64decode(os.environ.get('STELLAR_ENCRYPTED_BASE_SECRET_SEED'))
    )['Plaintext']
)
STELLAR_DATA_VERIFICATION_KEY = 'nucleo_signed_user'
STELLAR_TOML_PATH = '/.well-known/stellar.toml'

# Nucleo covers 1 data entry + 1 trustline for user's first two account
# NOTE: https://www.stellar.org/developers/guides/concepts/fees.html
STELLAR_CREATE_ACCOUNT_QUOTA = 2
STELLAR_CREATE_ACCOUNT_MINIMUM_BALANCE = '3'
if DEBUG:
    STELLAR_HORIZON = horizon.HORIZON_TEST
    STELLAR_HORIZON_INITIALIZATION_METHOD = horizon.horizon_testnet
    STELLAR_NETWORK = 'TESTNET'
else:
    STELLAR_HORIZON = horizon.HORIZON_LIVE
    STELLAR_HORIZON_INITIALIZATION_METHOD = horizon.horizon_livenet
    STELLAR_NETWORK = 'PUBLIC'

# StellarExpert
if DEBUG:
    STELLAR_EXPERT_URL = 'https://stellar.expert/explorer/testnet'
else:
    STELLAR_EXPERT_URL = 'https://stellar.expert/explorer/public'
STELLAR_EXPERT_ACCOUNT_URL = STELLAR_EXPERT_URL + '/account/'
STELLAR_EXPERT_TRANSACTION_URL = STELLAR_EXPERT_URL + '/tx/'

# StellarNotifier
STELLAR_NOTIFIER_URL = os.environ.get('STELLAR_NOTIFIER_URL')
STELLAR_NOTIFIER_SUBSCRIPTION_URL = '{0}{1}'.format(STELLAR_NOTIFIER_URL, '/api/subscription/')
STELLAR_NOTIFIER_SIGNATURE_HEADER = 'X-Request-ED25519-Signature'
STELLAR_NOTIFIER_AUTHORIZATION_HEADER = 'Authorization'
STELLAR_NOTIFIER_AUTHORIZATION_FORMAT = 'Token {0}'

# StellarTerm
STELLARTERM_TICKER_URL = 'https://api.stellarterm.com/v1/ticker.json'

# Kraken
KRAKEN_TICKER_URL = 'https://api.kraken.com/0/public/OHLC'
KRAKEN_XLMUSD_PAIR_NAME = 'XXLMZUSD'
KRAKEN_XLMBTC_PAIR_NAME = 'XXLMXXBT'

# Papaya
PAPAYA_DOMAIN = 'apay.io'
PAPAYA_API_URL = 'https://apay.io/api'
PAPAYA_API_DEPOSIT_URL = PAPAYA_API_URL + '/deposit/'

# Stronghold
STRONGHOLD_ENV = os.environ.get('STRONGHOLD_ENV')
STRONGHOLD_SECRET_KEY = kms_client.decrypt(
    CiphertextBlob=b64decode(os.environ.get('STRONGHOLD_ENCRYPTED_SECRET_KEY'))
)['Plaintext']
STRONGHOLD_CREDENTIAL_ID = os.environ.get('STRONGHOLD_CREDENTIAL_ID')
STRONGHOLD_CREDENTIAL_PASSPHRASE = os.environ.get('STRONGHOLD_CREDENTIAL_PASSPHRASE')

# CryptoPanic
CRYPTOPANIC_API_KEY = os.environ.get('CRYPTOPANIC_API_KEY')
CRYPTOPANIC_STELLAR_POST_URL = 'https://cryptopanic.com/api/posts/'

# Stream
STREAM_API_KEY = os.environ.get('STREAM_API_KEY')
STREAM_API_SECRET = os.environ.get('STREAM_API_SECRET')
STREAM_USER_FEED = 'user'
STREAM_TIMELINE_FEED = 'timeline'

# reCAPTCHA
GOOGLE_RECAPTCHA_SITE_KEY = os.environ.get('GOOGLE_RECAPTCHA_SITE_KEY')
GOOGLE_RECAPTCHA_SECRET_KEY = os.environ.get('GOOGLE_RECAPTCHA_SECRET_KEY')
GOOGLE_RECAPTCHA_VERIFICATION_URL = 'https://www.google.com/recaptcha/api/siteverify'
