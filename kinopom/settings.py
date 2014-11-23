import os
gettext = lambda s: s
"""
Django settings for kinopom project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'rnk!ui!yq=*-o#w(yqkd*=*-udfr!2#m62^#o7+h#ozg%2gl24'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition





ROOT_URLCONF = 'kinopom.urls'

WSGI_APPLICATION = 'kinopom.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases



# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'kinopom', 'static'),
)
SITE_ID = 1

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.i18n',
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.csrf',
    'django.core.context_processors.tz',
    'sekizai.context_processors.sekizai',
    'django.core.context_processors.static',
    'cms.context_processors.cms_settings'
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'kinopom', 'templates'),
    os.path.join(BASE_DIR, 'app_accounts', 'templates'),
    os.path.join(BASE_DIR, 'app_video', 'templates'),
    os.path.join(BASE_DIR, 'app_comments', 'templates'),
    os.path.join(BASE_DIR, 'app_menu', 'templates'),
)

INSTALLED_APPS = (
    'djangocms_admin_style',
    'djangocms_text_ckeditor',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'django.contrib.messages',

    'cms',
    'mptt',
    'menus',
    'south',
    'sekizai',
    'djangocms_style',
    'djangocms_column',
    'djangocms_file',
    'djangocms_flash',
    'djangocms_googlemap',
    'djangocms_inherit',
    'djangocms_link',
    'djangocms_picture',
    'djangocms_teaser',
    'djangocms_video',
    'reversion',
    'django_summernote',

    'kinopom',
    'app_accounts',
    'app_video',
    'app_comments',
    'app_menu',
)

LANGUAGES = (
    ## Customize this
    ('ru', gettext('ru')),
)

CMS_LANGUAGES = {
    ## Customize this
    'default': {
        'public': True,
        'hide_untranslated': False,
        'redirect_on_fallback': True,
    },
    1: [
        {
            'public': True,
            'code': 'ru',
            'hide_untranslated': False,
            'name': gettext('ru'),
            'redirect_on_fallback': True,
        },
    ],
}

CMS_TEMPLATES = (
    ## Customize this
    ('about.html', 'About project'),
    ('page_tags.html', 'Tags'),
    ('page_statistic.html', 'Statistic'),
    ('sidebar_right.html', 'Sidebar Right'),
    ('page_privacy_policy.html', 'Privacy policy'),
)

CMS_PERMISSION = True

CMS_PLACEHOLDER_CONF = {}

DATABASES = {
    'default':
        {
            'ENGINE': 'django.db.backends.sqlite3', 
            'NAME': 'project.db', 
            'HOST': 'localhost', 
            'USER': '', 
            'PASSWORD': '', 
            'PORT': ''
        }
}

# DATABASES = {
#     'default' : {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'kinopom',
#         'USER': 'kinopom',
#         'PASSWORD': 'qazwsxasdzxc',
#         'HOST': '/var/run/mysql',
#         'PORT': '3306',
#     }
# }
#


ALLOWED_HOSTS = ['127.0.0.1:8000']
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}


# CKEDITOR_SETTINGS = {
#     'language': '{{ language }}',
#     'toolbar_HTMLField': [
#         ['Undo', 'Redo'],
#         ['ShowBlocks'],
#         ['Format', 'Styles'],
#     ],
#     'skin': 'moono',
# }