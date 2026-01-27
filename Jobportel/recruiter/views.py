from django.shortcuts import redirect,render,get_object_or_404
from recruiter.models import Recruter,documents,job
from Seeker.models import seeker,resume,application
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.http import require_POST, require_http_methods
from Seeker.utils import extract,entity_score_spacy,atscore,pool_score,semantic_similarity,jaccard_skill_score,generate_vector
from .forms import recruter_form,DocumentUploadForm,job_form
from django.http import HttpResponse
from django.contrib import messages
import datetime

def is_recruter(user):
    return hasattr(user, 'recruter')

@login_required
@user_passes_test(is_recruter, login_url='/access-denied/')
def recruter_home(request):
    emp_obj=Recruter.objects.get(user=request.user)
    jobs=job.objects.filter(recruter=emp_obj).order_by('-created_at')[:5]
    today=datetime.date.today()
    return render(request,'Recruter_temp/recruter_home.html',{'employer':emp_obj,'jobs':jobs,'today':today})

@login_required
@user_passes_test(is_recruter, login_url='/access-denied/')
def recruter_profile(request):
    user=request.user
    employer=getattr(user,"recruter",None)
    return render(request,'Recruter_temp/recruter_profile.html',{"user":user,"recruter":employer})

# def recruter_update(request):
#     user=request.user
#     employer=getattr(user,"Recruter",None)
#     return render(request,'Recruter_temp/profile_update.html',{"user":user,"employer":employer})
@login_required
@user_passes_test(is_recruter, login_url='/access-denied/')
def recruter_update(request):
    current_recruter=Recruter.objects.get(user=request.user)
    docs, created = documents.objects.get_or_create(recruter=current_recruter)
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
            current_recruter.size = form.cleaned_data['size']
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
    return render(request,'Recruter_temp/profile_update.html',{'form':form,'employer':current_recruter,'docs':docs})


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
            docs.gst_certificate = gst
            docs.registration = reg
            docs.pan_card = pan
            docs.address_proof = address
            docs.gst_verified = False
            docs.registration_verified = False
            docs.pan_verified = False
            docs.address_proof_verified = False
            docs.save()
            return HttpResponse("Documents Uploaded")
    else:
        form=DocumentUploadForm()
    return render(request, 'recruter_temp/upload_docs.html',{'form':form,'docs':docs})
    
@login_required
@user_passes_test(is_recruter, login_url='/access-denied/')
def post_job(request):
    current_recruter=Recruter.objects.get(user=request.user)
    docs=documents.objects.get(recruter=current_recruter)
    if not current_recruter.is_profile_complete():
        messages.warning(request, "Please fill in all company details.")
        return redirect('recruiter:profile_update')
    if not docs.is_documents_complete():
        messages.warning(request, "Please upload all required documents.")
        return redirect('recruiter:upload_docs')
    
    if current_recruter.approval_status != "APPROVED":
        messages.warning(request, "Your profile is not approved yet.")
        return redirect('recruiter:profile_update')
    
    if request.method == 'POST':
        form = job_form(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            discription = form.cleaned_data['discription']
            education = form.cleaned_data['education']
            experience = form.cleaned_data['experience']
            salary = form.cleaned_data['salary']
            responsablity = form.cleaned_data['responsablity']
            due = form.cleaned_data['due']
            skills_list = [s.strip() for s in form.cleaned_data['skills'].split(',')]
            job_text = f"""
                        Job Title: {title}

                        Job Description:
                        {discription}

                        Required Skills:
                        {skills_list}

                        Education:
                        {education}

                        Experience:
                        {experience}

                        responsablity:
                        {responsablity}
                        """
            job_vector = generate_vector(job_text)
            new_job = job.objects.create(title=title, discription=discription, skills=skills_list, education=education, experience=experience, salary=salary, responsablity=responsablity,job_vector=job_vector, due=due, recruter=current_recruter)
            new_job.save()
            return HttpResponse("Job Posted")
    else:
        form = job_form()
    

    return render(request, 'recruter_temp/Post_job.html', {'form': form})

@login_required
@user_passes_test(is_recruter, login_url='/access-denied/')
def job_list(request):
    current_recruter=Recruter.objects.get(user=request.user)
    jobs = job.objects.filter(recruter=current_recruter)
    count=jobs.count()
    today=datetime.date.today()
    return render(request, 'recruter_temp/job_list.html', {'jobs': jobs,'count':count,'today':today})

@login_required
@user_passes_test(is_recruter, login_url='/access-denied/')
def candidate_pool(request,job_id):
    target_job = get_object_or_404(job, id=job_id)
    app_data=application.objects.filter(job_id=job_id).select_related('seeker__user','job')
    count={
        'excellent': app_data.filter(category='excellent').count(),
        'good': app_data.filter(category='good').count(),
        'low': app_data.filter(category='low').count(),
        'total': app_data.count()
    }
    
    return render(request,'recruter_temp/candidate_list.html',{'data':app_data,'count':count,'job':target_job})