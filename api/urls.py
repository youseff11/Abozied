from django.urls import path
from . import views 

urlpatterns = [
    path('predict/', views.predict_artifact, name='predict_artifact'),
    path('register/', views.register_user, name='register'),
]