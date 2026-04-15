from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-!z!c#ve8s-ijx29i=)qj(f@%^58o2zj@ffflfq&g$yf8@m4w(s'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    # Jazmin لازم تكون قبل الـ admin عشان تغير شكلها
    'jazzmin',
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # المكتبات المطلوبة للربط
    'rest_framework',
    'rest_framework.authtoken', # ضفتلك دي عشان نظام الـ Login
    'corsheaders',
    
    # الـ App الخاص بمشروعك
    'api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'artifact_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'System' / 'templates'],
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

WSGI_APPLICATION = 'artifact_backend.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# إعدادات الـ Rest Framework لنظام الـ Token
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# --- ضبط الوقت ليكون بتوقيت القاهرة/أفريقيا ---
LANGUAGE_CODE = 'ar' # خليته عربي عشان Jazmin تظهر بالعربي لو حبيت
TIME_ZONE = 'Africa/Cairo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'artifact_backend' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# --- إعدادات الميديا (الصور اللي هترفعها للتماثيل) ---

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- إعدادات Jazmin (Dashboard) ---
JAZMIN_SETTINGS = {
    "site_title": "لوحة تحكم مشروع التماثيل",
    "site_header": "Egyptian Statues",
    "site_brand": "Artifact AI",
    "welcome_sign": "مرحباً بك يا يوسف في لوحة التحكم",
    "copyright": "Yousef Osama - 2026",
    "search_model": ["auth.User", "api.Statue"],
    "show_sidebar": True,
    "navigation_expanded": True,
    "topmenu_links": [
        {"name": "الرئيسية", "url": "admin:index", "permissions": ["auth.view_user"]},
    ],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "api.Statue": "fas fa-monument",
        "api.SearchHistory": "fas fa-history",
    },
}