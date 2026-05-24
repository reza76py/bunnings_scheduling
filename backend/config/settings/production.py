import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

from .base import *

SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-env')
DEBUG = False
ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', '').split(',') if host.strip()]
CSRF_TRUSTED_ORIGINS = ['https://s.rezteche.com']
CORS_ALLOWED_ORIGINS = ['https://s.rezteche.com']
CORS_ALLOW_ALL_ORIGINS = False
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.mysql',
		'NAME': os.getenv('DB_NAME', ''),
		'USER': os.getenv('DB_USER', ''),
		'PASSWORD': os.getenv('DB_PASSWORD', ''),
		'HOST': os.getenv('DB_HOST', 'localhost'),
		'PORT': os.getenv('DB_PORT', '3306'),
		'OPTIONS': {'charset': 'utf8mb4'},
	}
}

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'backend', 'staticfiles')

REST_FRAMEWORK = {
	'DEFAULT_AUTHENTICATION_CLASSES': [],
	'DEFAULT_PERMISSION_CLASSES': [
		'rest_framework.permissions.AllowAny',
	],
}
