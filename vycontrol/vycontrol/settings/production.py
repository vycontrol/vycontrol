from .base import *

DEBUG = False

ALLOWED_HOSTS = ['vycontrol.domain.com', ]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'user'
EMAIL_HOST_PASSWORD = 'password'
EMAIL_USE_TLS = True


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*wv2=o(o5$i2qim7yxras_7jf%n!*1rrzehv3o2f-ebsr@ba%4'

