"""
Django settings for pyano project.

Generated by 'django-admin startproject' using Django 1.10.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '5s2ijthclynlo&oqe!8z&b33%k!$9*7ti-y^zg8-hv@roorn-x'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SHOPLIFT_DOMAIN = 'shoplift.pyano2.tk'

ALLOWED_HOSTS = ['13.58.121.50', '127.0.0.1', SHOPLIFT_DOMAIN]

SITE_ID = 1

# Application definition

INSTALLED_APPS = [
    'pyano2.apps.Pyano2Config',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrapform',
	'survey',
    'analytical',
    'social_django',
    'sorl.thumbnail',
    'newsletter',
    'tinymce'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware'
]

ROOT_URLCONF = 'pyano.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'pyano2', 'templates'),
            os.path.join(BASE_DIR, 'examples', 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',  # <--
                'social_django.context_processors.login_redirect', # <--
            ],
        },
    },
]

WSGI_APPLICATION = 'pyano.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pyano2',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        # # 'PORT': 'your_port',
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]

# Analytical settings
GOOGLE_ANALYTICS_PROPERTY_ID = 'UA-129797554-1'
GOOGLE_ANALYTICS_ANONYMIZE_IP = True
GOOGLE_ANALYTICS_SAMPLE_RATE = 10
GOOGLE_ANALYTICS_SITE_SPEED_SAMPLE_RATE = 10
GOOGLE_ANALYTICS_SESSION_COOKIE_TIMEOUT = 3600000
GOOGLE_ANALYTICS_VISITOR_COOKIE_TIMEOUT = 3600000
ANALYTICAL_INTERNAL_IPS = []
ANALYTICAL_AUTO_IDENTIFY = True

# To send email through gmail
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = "annotator.department@gmail.com"
EMAIL_HOST_PASSWORD = "83iUXL7ETARYK6UGJ6T4Zj52EfFjaDpLGHV6HV5vtzfjtHSyhf73pBB9j7gAfUd8tePuRxgocF4UFNrKxDsnZEUPFX5RkVEX8yNt"

AUTHENTICATION_BACKENDS = (
    'social_core.backends.open_id.OpenIdAuth',  # for Google authentication
    'social_core.backends.google.GoogleOpenId',  # for Google authentication
    'social_core.backends.google.GoogleOAuth2',  # for Google authentication
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL = '/accounts/login'
LOGOUT_URL = '/accounts/logout'
LOGIN_REDIRECT_URL = '/'

SOCIAL_AUTH_GITHUB_KEY = ''
SOCIAL_AUTH_GITHUB_SECRET = ''
SOCIAL_AUTH_TWITTER_KEY = ''
SOCIAL_AUTH_TWITTER_SECRET = ''
SOCIAL_AUTH_FACEBOOK_KEY = ''
SOCIAL_AUTH_FACEBOOK_SECRET = ''
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ''
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''

NEWSLETTER_CONFIRM_EMAIL = False
NEWSLETTER_RICHTEXT_WIDGET = "tinymce.widgets.TinyMCE"
# Amount of seconds to wait between each email. Here 100ms is used.
NEWSLETTER_EMAIL_DELAY = 0.1

# Amount of seconds to wait between each batch. Here one minute is used.
NEWSLETTER_BATCH_DELAY = 60

# Number of emails in one batch
NEWSLETTER_BATCH_SIZE = 100

SOCIAL_AUTH_GITHUB_KEY = '05ee6fa7511a1c4ab25a'
SOCIAL_AUTH_GITHUB_SECRET = 'f31c9e8d95a6761e686718d814eca75b28e9bb40'
SOCIAL_AUTH_TWITTER_KEY = 'Cpwr7cYAsUybYhsBtpJg7Yytf'
SOCIAL_AUTH_TWITTER_SECRET = 'ZQTZbIC9n6ov9DegLG9BATzZkiJ4FHQLGGgrxGwQWCdZqsGBr1'
SOCIAL_AUTH_FACEBOOK_KEY = ''
SOCIAL_AUTH_FACEBOOK_SECRET = ''
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '893054302964-35k5jobjdgqkoq4qt9r4if5ehdrqh406.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '5TH_oMviMUFD8V9Bc2TEv5ge'
