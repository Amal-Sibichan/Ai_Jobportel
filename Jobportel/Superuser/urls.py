from django.urls import path
from .import views   

app_name = 'Superuser'
urlpatterns = [
    path('superuser/',views.admin_home,name='admin_home'),
    path('superuser/vrerify/<int:u_id>/',views.verify,name='verify_docs'),
    path('verfication/<int:r_id>/',views.update,name='verification')

]