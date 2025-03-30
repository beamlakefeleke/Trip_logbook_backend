import os
import pymysql
pymysql.install_as_MySQLdb()

# Define the base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Use environment variable for security
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "JH0eOqYGIyTLai20lY5yxl5-pizWneciUZFoXx0ZmKY6C99UUpZqakVowd6xoMi9Q2w")

# Enable Django Channels
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'rest_framework',
    'channels',  # Django Channels
    'corsheaders',
    'api',  # Your application
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # ✅ Ensure JWT is used
    ),
}

# Define ASGI application for Django Channels
ASGI_APPLICATION = "trip_logger.asgi.application"

# WebSockets with Redis
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],  # Ensure Redis is running
        },
    },
}

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv("MYSQL_DATABASE", "trip_logbook"),  # Database name
        'USER': os.getenv("MYSQL_USER", "root"),  # Change if using another user
        'PASSWORD': os.getenv("MYSQL_PASSWORD", "root"),  # Change to your MySQL password
        'HOST': os.getenv("MYSQL_HOST", "127.0.0.1"),  # Default to localhost
        'PORT': os.getenv("MYSQL_PORT", "3306"),  # Default MySQL port
        'OPTIONS': {
            'charset': 'utf8mb4',  # Support Unicode emojis, special chars
        },
    }
}


# ✅ CORS Configuration (Allow frontend)
CORS_ALLOW_ALL_ORIGINS = False  # ❌ Not recommended for production
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # ✅ Allow frontend
]
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS = ["content-type", "authorization", "x-requested-with"]

# Security Settings
DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"  # Set True for local dev

# Enable Django to serve static files in development
if DEBUG:
    import mimetypes
    mimetypes.add_type("text/javascript", ".js", True)

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

# Static & Media Files
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # Correct path

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # Correct path

# Authentication
AUTH_USER_MODEL = "api.User"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ROOT_URLCONF = "trip_logger.urls"  
