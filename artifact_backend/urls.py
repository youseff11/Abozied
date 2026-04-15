from django.contrib import admin
from django.urls import path, include # لازم تتأكد إن path و include موجودين هنا
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')), # تأكد إن عندك ملف urls.py جوه فولدر api
]

# السطور دي عشان السيرفر يقدر يعرض صور التماثيل اللي هترفعها
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)