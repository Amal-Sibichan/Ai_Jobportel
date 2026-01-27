from django.urls import path

from .import views   
app_name='seeker'
urlpatterns = [
    path('seeker_profile',views.profile,name='profile'),
    path('add_skill',views.add_skill,name='add_skill'),
    path('delete_skill/<int:skill_id>/', views.delete_skill, name='delete_skill'),
    path('profileupdate',views.profileupdate,name='profileupdate'),
    path('Resume_upload',views.Resume_upload,name='Resume_upload'),
    path('seeker/dashboard', views.seeker_home, name='seeker_page'),
    path('seeker/application/<int:job_id>/', views.job_application, name='application'),
    


    
]