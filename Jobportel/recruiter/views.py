from django.shortcuts import redirect, render
from recruiter.models import Recruter,documents
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.http import require_POST, require_http_methods
from .forms import recruter_form,DocumentUploadForm
from django.http import HttpResponse
from django.contrib import messages

def is_recruter(user):
    return hasattr(user, 'recruter')

@login_required
@user_passes_test(is_recruter, login_url='/access-denied/')
def recruter_home(request):
    emp_obj=Recruter.objects.get(user=request.user)
    return render(request,'Recruter_temp/recruter_home.html',{'employer':emp_obj})

@login_required
@user_passes_test(is_recruter, login_url='/access-denied/')
def recruter_profile(request):
    user=request.user
    employer=getattr(user,"Recruter",None)
    return render(request,'Recruter_temp/recruter_profile.html',{"user":user,"employer":employer})

# def recruter_update(request):
#     user=request.user
#     employer=getattr(user,"Recruter",None)
#     return render(request,'Recruter_temp/profile_update.html',{"user":user,"employer":employer})
@login_required
@user_passes_test(is_recruter, login_url='/access-denied/')
def recruter_update(request):
    current_recruter=Recruter.objects.get(user=request.user)
    if request.method == 'POST':
        form=recruter_form(request.POST)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()

            current_recruter.company_name = form.cleaned_data['company_name']
            current_recruter.company_email = form.cleaned_data['company_email']
            current_recruter.website = form.cleaned_data['website']
            current_recruter.phone = form.cleaned_data['phone']
            current_recruter.address = form.cleaned_data['address']
            current_recruter.decription = form.cleaned_data['decription']
            current_recruter.industry = form.cleaned_data['industry']
            current_recruter.Organization_type = form.cleaned_data['Organization_type']
            current_recruter.save()
            messages.success(request, 'Login successful!')
            return redirect('recruiter:recruter_profile')


    else:
        form = recruter_form(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email':request.user.email,
            'company_name': current_recruter.company_name,
            'company_email': current_recruter.company_email,
            'website': current_recruter.website,
            'phone': current_recruter.phone,
            'address': current_recruter.address,
            'decription': current_recruter.decription,
            'industry': current_recruter.industry,
            'Organization_type': current_recruter.Organization_type,
            })
    return render(request,'Recruter_temp/profile_update.html',{'form':form,'employer':current_recruter})


@login_required
@user_passes_test(is_recruter, login_url='/access-denied/')
def upload_docs(request):
    recruter=Recruter.objects.get(user=request.user)
    docs, created = documents.objects.get_or_create(recruter=recruter)
    if request.method == 'POST':
        form=DocumentUploadForm(request.POST,request.FILES)
        if form.is_valid():
            gst=form.cleaned_data['gst_certificate']
            reg=form.cleaned_data['registration']
            pan=form.cleaned_data['pan_card']
            address=form.cleaned_data['address_proof']
            new_docs=documents.objects.create(recruter=recruter,gst_certificate=gst,registration=reg,pan_card=pan,address_proof=address)
            new_docs.save()
            return HttpResponse("Documents Uploaded")
    else:
        form=DocumentUploadForm()
    return render(request, 'recruter_temp/upload_docs.html',{'form':form,'docs':docs})
    
