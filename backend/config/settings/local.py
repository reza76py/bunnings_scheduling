import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / '.env.local')

from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']
CORS_ALLOW_ALL_ORIGINS = True

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
