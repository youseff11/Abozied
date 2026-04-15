from django.urls import path
from .views import predict_artifact

urlpatterns = [
    path('predict/', predict_artifact, name='predict_artifact'),
    path('register/', views.register_user, name='register'),
]