import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / '.env.production')

from .base import *

DEBUG = False
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
CORS_ALLOW_ALL_ORIGINS = False

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

CORS_ALLOWED_ORIGINS = [
	"http://s.rezteche.com",
	"http://65.108.243.73",
]
