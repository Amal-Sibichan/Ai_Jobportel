from django.urls import path
from .import views   
urlpatterns = [
    path('user_home', views.user_dash, name='Uhome'),
    
]