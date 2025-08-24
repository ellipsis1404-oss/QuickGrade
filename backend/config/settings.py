# backend/config/settings.py

import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file (for local development)
load_dotenv(os.path.join(BASE_DIR, '.env'))


# --- CORE DJANGO SETTINGS ---

# SECRET_KEY is loaded from environment variables.
# The second argument is a FALLBACK for local development if .env is missing.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'a-default-insecure-key-for-local-development-only')

# DEBUG is True locally, but False in production on Render.
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS for local development. Render's hostname is added automatically.
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # For serving static files in development
    'django.contrib.staticfiles',
    # Third-party apps
    'rest_framework',
    'corsheaders',
    'django_filters',
    'storages',
    # Local apps
    'core',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Whitenoise middleware should be placed right after the security middleware.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# --- DATABASE CONFIGURATION ---
DATABASES = {
    'default': dj_database_url.config(
        # Fallback to local SQLite database if DATABASE_URL is not set
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600
    )
}

# --- PASSWORD VALIDATION ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- INTERNATIONALIZATION ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- STATIC & MEDIA FILES ---
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- DJANGO REST FRAMEWORK & CORS ---
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']
}
# This reads the trusted origins from your Render environment variables.
# The .split(',') allows you to add multiple domains later if needed.
CORS_ALLOWED_ORIGIN_REGEXES = [
    # This pattern matches http://localhost:any-port
    r"^http://localhost:\d+$",
    
    # This pattern will match your Cloudflare Pages URL
    # It handles both the default .pages.dev and any custom domains you might add.
    r"^https://.*\.pages\.dev$",
]

# --- STORAGE CONFIGURATION (Local vs. Production) ---
# Check if we are running on Render (production)
if os.environ.get('RENDER'):
    # Production settings: use Supabase for media files and Whitenoise for static files.
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
    # Supabase/S3 Storage Configuration from environment variables
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    SUPABASE_BUCKET = os.environ.get('SUPABASE_BUCKET')

    AWS_S3_ENDPOINT_URL = f"{SUPABASE_URL}/storage/v1"
    AWS_ACCESS_KEY_ID = SUPABASE_KEY
    AWS_SECRET_ACCESS_KEY = SUPABASE_KEY
    AWS_STORAGE_BUCKET_NAME = SUPABASE_BUCKET
    AWS_S3_FILE_OVERWRITE = False
# else: (For local development)
# Django's default FileSystemStorage will be used automatically for media files.
# Whitenoise's runserver_nostatic will handle static files.

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'