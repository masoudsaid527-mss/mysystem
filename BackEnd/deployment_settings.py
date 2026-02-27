import os
from .settings import *
import dj_database_url
from .settings import BASE_DIR

# Set debug to False in production
DEBUG = False
# Set ALLOWED_HOSTS to your domain
# Use Render-provided hostname or default to localhost
ALLOWED_HOSTS = [os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'localhost')]

# Recommended for CSRF protection (e.g. for forms)
CSRF_TRUSTED_ORIGINS = [
    'https://' + os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'localhost')
]

# Secret key must be set in environment variable
SECRET_KEY = os.environ.get('SECRET_KEY', 'unsafe-default')

# Middleware for production
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

# Static files config for WhiteNoise
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Parse DATABASE_URL from Render (PostgreSQL)
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        # ssl_require=True  # important for Render PostgreSQL
    )
}

# # CORS for React frontend (update to your actual frontend URL)
CORS_ALLOWED_ORIGINS = [
    "https://my-project-1-re1u.onrender.com",  # ✅ Replace with your frontend URL
    #"http://localhost:3000",  # optional for local dev
 ]


STORAGES = {
    "default": {
        "BACKEND" : "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage", 
    }
}