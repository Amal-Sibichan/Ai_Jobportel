from django.shortcuts import render,redirect
from accounts.forms import login_form# Create your views here.
from recruiter.models import Recruter,documents,job

def home(request):  
    jobs=job.objects.select_related('recruter').all()
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('Superuser:admin_home')
        if hasattr(request.user, 'recruter'):
            return redirect('recruiter:recruter_page')
        if hasattr(request.user, 'seeker'):
            return redirect('seeker:seeker_page')
        return render(request,'main/home.html',{'jobs':jobs})
    return redirect('accounts:login')