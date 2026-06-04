from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-!z!c#ve8s-ijx29i=)qj(f@%^58o2zj@ffflfq&g$yf8@m4w(s'

DEBUG = True  # غيّره لـ False في البيئة الإنتاجية

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    # 'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',  # ✅ مهم جداً للـ Token Authentication
    'corsheaders',
    'api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',   # ✅ لازم يكون أول حاجة
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
        'DIRS': [BASE_DIR / 'templates'],
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

# ── REST Framework ──────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# ── CORS ────────────────────────────────────────────────────────
# السماح لكل الأصول (مناسب للتطوير والـ PythonAnywhere)
CORS_ALLOW_ALL_ORIGINS = True

# ── كلمة المرور ────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── التوطين ─────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Africa/Cairo'
USE_I18N      = True
USE_TZ        = True

# ── الملفات الثابتة والميديا ────────────────────────────────────
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Jazzmin Admin Theme ─────────────────────────────────────────
JAZZMIN_SETTINGS = {
    'site_title':          'Artifact AI Admin',
    'site_header':         'Egyptian Statues',
    'site_brand':          'Artifact AI',
    'welcome_sign':        'Welcome back, Yousef',
    'copyright':           'Yousef Osama - 2026',
    'search_model':        ['auth.User', 'api.Statue'],
    'show_sidebar':        True,
    'navigation_expanded': True,
    'topmenu_links': [
        {'name': 'Home', 'url': 'admin:index', 'permissions': ['auth.view_user']},
    ],
    'icons': {
        'auth':              'fas fa-users-cog',
        'auth.user':         'fas fa-user',
        'api.Statue':        'fas fa-monument',
        'api.SearchHistory': 'fas fa-history',
    },
}
