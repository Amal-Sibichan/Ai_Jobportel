from django.urls import path
from .import views   

app_name = 'recruiter'
urlpatterns = [
    path('recruter/dashboard', views.recruter_home, name='recruter_page'),
    path('recruter/profile',views.recruter_profile,name='recruter_profile'),
    path('recruter/profile/update',views.recruter_update,name='profile_update'),
    path('recruter/upload_docs',views.upload_docs,name='upload_docs'),

]