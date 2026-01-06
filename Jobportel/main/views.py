from django.shortcuts import render,redirect
from accounts.forms import login_form# Create your views here.
def home(request):  
    if request.user.is_authenticated:
        return render(request,'main/home.html')
    return redirect('accounts:login')