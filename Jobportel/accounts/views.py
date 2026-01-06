from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from Seeker.models import seeker
from .forms import login_form, register
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth import logout
# Create your views here.
def login_user(request):
    if request.method == 'POST':
        form=login_form(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request,user)
            seeker_obj = seeker.objects.get(user=user)
            messages.success(request, 'Login successful!')
            return render(request,'main/home.html',{'seeker':seeker_obj})
    else:
        form = login_form()

    return render(request,'accounts/Login.html',{'form':form})

def logout_user(request):
    logout(request)
    messages.info(request, "Logged out successfully")
    return redirect('accounts:login')

def register_user(request):
    if request.method == 'POST':
        form = register(request.POST)
        if form.is_valid():
            name =form.cleaned_data['name']
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']
            password= form.cleaned_data['password']
            user = User.objects.create_user(
                username=email,     # username can be email
                email=email,
                password=password,
                first_name=name
            )
            if role == 'job_seeker':
                seeker.objects.create(user=user)
            elif role == 'recruiter':
                # Recruiter.objects.create(user=user)
                return HttpResponse(f"Registered: {name} - {email}-{role}-{password}")
            return redirect('accounts:login')
    else:
        form = register()
    return render(request, 'accounts/register.html', {'form': form})
