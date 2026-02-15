from django.contrib.messages import success
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
    path('recruter/candidate_pool/<int:job_id>',views.candidate_pool,name='candidate_pool'),
    path('recruter/candidate_details/<int:candidate_id>/<int:job_id>',views.candidate_details,name='candidate_details'),
    path('chatbot/ask/', views.ask_bot, name='chatbot_ask'),
    path('recruter/shortlist/<int:app_id>/',views.shorlist,name='shortlist'),
    path('recruter/Reject/<int:app_id>/',views.Reject,name='Reject'),
    path('admin/add_plan/',views.add_plan,name='add_Plan'),
    path('recruter/plans',views.subscription,name='subscription'),
    path('recruter/create_payment/<int:plan_id>/',views.create_payment,name='create_payment'),
    path('payment_success',views.payment_success,name='payment_success'),
    path('subscription_detials',views.subscription_detials,name='subscription_detials'),
    path('recruter/list/<int:job_id>',views.list,name='list'),



]