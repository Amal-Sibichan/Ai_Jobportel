from django.urls import path
from .import views   
urlpatterns = [
    path('user_home', views.user_dash, name='Uhome'),
    path('seeker_profile',views.profile,name='seeker/profile'),
    path('add_skill',views.add_skill,name='add_skill'),
    path('delete_skill/<int:skill_id>/', views.delete_skill, name='delete_skill'),
    path('profileupdate',views.profileupdate,name='profileupdate'),
    path('Resume_upload',views.Resume_upload,name='Resume_upload'),
    
]