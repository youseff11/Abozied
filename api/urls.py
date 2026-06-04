from django.urls import path
from . import views

urlpatterns = [
    path('register/',  views.register_user,      name='register'),
    path('login/',     views.login_user,          name='login'),
    path('predict/',   views.predict_artifact,    name='predict'),
    path('history/',   views.get_search_history,  name='history'),   
    path('profile/',   views.get_profile,         name='profile'),
    path('landmarks/', views.get_landmarks, name='landmarks'),
    
]
