from django.urls import path
from .import views   

app_name = 'recruiter'
urlpatterns = [
    path('recruter/dashboard', views.recruter_home, name='recruter_page'),
    path('recruter/profile',views.recruter_profile,name='recruter_profile'),
    path('recruter/profile/update',views.recruter_update,name='profile_update'),
    path('recruter/upload_docs',views.upload_docs,name='upload_docs'),
    path('recruter/post_job',views.post_job,name='post_job'),
    path('recruter/job_list',views.job_list,name='job_list'),
    path('recruter/candidate_pool/<int:job_id>',views.candidate_pool,name='candidate_pool')

]