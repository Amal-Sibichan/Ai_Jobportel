from django.shortcuts import render
from django.http import HttpResponse
from Seeker.models import seeker
from .forms import register,login


# Create your views here.
def login_user(request):
    if request.method == 'POST':
        form=login(request.POST)
        if form.is_valid():
            return render(request,'main/home.html')
    else:
        form = login()

    return render(request,'accounts/Login.html',{'form':form})

def register_user(request):
    if request.method == 'POST':
        form = register(request.POST)
        if form.is_valid():
            name =form.cleaned_data['name']
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']
            password= form.cleaned_data['password']
            if role == 'job_seeker':
                new=seeker(name=name,email=email,password=password)
                new.save()
            elif role == 'recruiter':
                return HttpResponse(f"Registered: {name} - {email}-{role}-{password}")
            return render(request, 'accounts/Login.html')
    else:
        form = register()
    return render(request, 'accounts/register.html', {'form': form})
