from django.core.checks.messages import Info
from django.shortcuts import redirect, render
import json
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST, require_http_methods
from numpy import info
from .models import *
from .forms import profileupdateform,upload_resume,education_form,experience_form
from .utils import extract,entity_score_spacy,atscore,pool_score,semantic_similarity,jaccard_skill_score,generate_vector
from .LLM import extract_skills_llm
from recruiter.models import *
from django.db.models import Q
# Create your views here.
@login_required
def seeker_home(request):
    seeker_obj = seeker.objects.get(user=request.user)
    

    jobs = job.objects.select_related('recruter').all()
    return render(request,'main/home.html',{'seeker':seeker_obj,'jobs':jobs})
@login_required
def profile(request):
    user=request.user
    seeker=getattr(user,"seeker",None)
    resume=getattr(seeker,"resume",None)
    Experiences=seeker.experiences.all()
    Education=seeker.education.all()
    skills=seeker.skills.all()
    edu_form = education_form()
    exp_form = experience_form()
    
    return render(request,'seeker/profile.html',{'user':user,'skills':skills,'form':edu_form,'e_form':exp_form,'education':Education,'experiences':Experiences})

@login_required
@require_POST
def add_skill(request):
    try:
        # Load the JSON data from the fetch request
        data = json.loads(request.body)
        skill_name = data.get('name', '').strip()
        
        if not skill_name:
            return JsonResponse({'status': 'error', 'message': 'Skill name cannot be empty'}, status=400)

        # 1. Get the seeker profile associated with the logged-in user
        # (Assuming your Seeker model has a OneToOne relationship with User)
        user_seeker = seeker.objects.get(user=request.user) 

        # 2. Create the skill using 'seeker' as the field name
        new_skill = skill.objects.create(
            seeker=user_seeker, 
            name=skill_name
        )
        
        return JsonResponse({
            'status': 'success', 
            'id': new_skill.id, 
            'name': new_skill.name
        })

    except seeker.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Seeker profile not found'}, status=404)
    except Exception as e:
        # Return the exact error to help us debug the 500 error
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@login_required
@require_http_methods(["DELETE"])
def delete_skill(request, skill_id):
    try:
        # Ensure the user owns the skill they are trying to delete
        skill_instance = skill.objects.get(id=skill_id,seeker=request.user.seeker)
        skill_instance.delete()
        return JsonResponse({'status': 'success'})
    except skill.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Skill not found'}, status=404)

@login_required
def profileupdate(request):
    current_seeker = seeker.objects.get(user=request.user)
    if request.method == 'POST':
        form = profileupdateform(request.POST)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()

            current_seeker.headline = form.cleaned_data['headline']
            current_seeker.discription = form.cleaned_data['bio']
            current_seeker.phone = form.cleaned_data['phone']
            current_seeker.address = form.cleaned_data['address']
            current_seeker.city = form.cleaned_data['city']
            current_seeker.state = form.cleaned_data['state']
            current_seeker.pincode = form.cleaned_data['pincode']

            if 'image' in request.FILES:
                current_seeker.image = request.FILES['image']
            
            current_seeker.save()
            messages.success(request, '  Profile Updated !')

            return redirect('seeker:profile')
    else:
        form = profileupdateform(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email':request.user.email,
            'headline':current_seeker.headline,
            'bio': current_seeker.discription,
            'phone': current_seeker.phone,
            'address': current_seeker.address,
            'city': current_seeker.city,
            'state': current_seeker.state,
            'pincode': current_seeker.pincode,
        })
    return render(request,'seeker/profileupdate.html',{'form':form,'seeker':current_seeker})



@login_required
def Resume_upload(request):
    user_res=seeker.objects.get(user=request.user)
    if request.method == 'POST':
        form=upload_resume(request.POST,request.FILES)
        if form.is_valid():
            res=form.cleaned_data['resume']
           # Use hasattr to check if the one-to-one relation 'resume' exists
            if hasattr(user_res, 'resume'):
                # Optional: Delete the physical file from storage if it exists
                if user_res.resume.resume:
                    user_res.resume.resume.delete(save=False)
                # Delete the database record
                user_res.resume.delete()
            
            res_text=extract(res)
            vector_Emp=generate_vector(res_text)
            Info=extract_skills_llm(res_text)
            try:
                resume_info = json.loads(Info)
            except json.JSONDecodeError:
                print("Invalid JSON format.")
                return HttpResponse("Invalid JSON format")
            ats_score=atscore(resume_info)
            entity_score=entity_score_spacy(res_text) 
            skill_list=resume_info.get('skills', [])  
            
            new_res = resume.objects.create(resume=res,seeker=user_res,resume_vector=vector_Emp,resume_text=res_text,ats_score=ats_score,entity_score=entity_score,skills=skill_list)
            new_res.save()
            messages.success(request, 'Resume uploaded  successfully!')
        return redirect('seeker:profile')

@login_required
def job_application(request,job_id):
    user_res=seeker.objects.get(user=request.user)
    if not hasattr(user_res, 'resume'):
        messages.error(request, 'Please upload a resume first.')
        return redirect('seeker:seeker_page')
    user_resume=resume.objects.get(seeker=user_res)
    jobs=job.objects.get(id=job_id)
    Skill_dict=jaccard_skill_score(user_resume.skills,jobs.skills)
    semantic_score=semantic_similarity(user_resume.resume_vector,jobs.job_vector)
    ats=user_resume.ats_score
    entity=user_resume.entity_score
    skill_score=Skill_dict['score']
    matched = Skill_dict['matched']
    unmatched = Skill_dict['unmatched']
    final_score= round((0.4 * skill_score + 0.15 * ats + 0.10 * entity + 0.35 * semantic_score),2)
    new_app = application.objects.create(seeker=user_res,job=jobs,matched_skills=matched,unmatched_skills=unmatched,final_score=final_score,skill_score=skill_score,semantic_score=semantic_score,entity_score=entity,ats_score=ats)
    new_app.save()
    messages.success(request, 'Application submitted successfully !')
    return redirect('seeker:seeker_page')


@login_required
def add_education(request):
    user_instance=seeker.objects.get(user=request.user)
    if request.method == "POST":
        form=education_form(request.POST)
        if form.is_valid():
            Education.objects.create(
                seeker=user_instance,
                institution=form.cleaned_data["institution"],
                level=form.cleaned_data["level"],
                course=form.cleaned_data["course"],
                start=form.cleaned_data["start"],
                end=form.cleaned_data["end"],
                description=form.cleaned_data["description"],
            )
            return JsonResponse(
                {
                    "success": True,
                    "message": "Education added successfully"
                },
                status=201
            )
        else:
            return JsonResponse(
                {
                    "success": False,
                    "errors": form.errors
                },
                status=400
            )
    else:
        form=education_form()
        return render(request,'seeker/profile.html',{'form':form})


@login_required
@require_POST
def add_experience(request):
    user_instance=seeker.objects.get(user=request.user)
    form=experience_form(request.POST)
    if form.is_valid():
            Experience.objects.create(
                seeker=user_instance,
                company=form.cleaned_data["company"],
                title=form.cleaned_data["title"],
                start=form.cleaned_data["start"],
                end=form.cleaned_data["end"],
                description=form.cleaned_data["description"],
            )
            return JsonResponse(
                {
                    "success": True,
                    "message": "Experience added successfully"
                },
                status=201
            )
            
    return JsonResponse(
                {
                    "success": False,
                    "errors": form.errors
                },
                status=400
            )

from django.shortcuts import render
from django.db.models import Q
from .models import job

@login_required
def jobs(request):
    # Start with all jobs
    job_list = job.objects.all().order_by('-created_at')

    # Get search parameters from the URL (GET request)
    exp_filter = request.GET.get('experience', '').strip()

    # Apply text search if query exists
    search_query = request.GET.get('q', '')
    if search_query:
        job_list = job_list.filter(
            Q(title__icontains=search_query) | 
            Q(recruter__company_name__icontains=search_query)
        )

    # Apply experience filter if selected
    if exp_filter and exp_filter != "":
        job_list = job_list.filter(experience=exp_filter)

    context = {
        'jobs': job_list,
        'search_query': search_query,
        'exp_filter': exp_filter,
    }
    return render(request, 'seeker/jobs.html', context)


def job_detials(request,jobid):
    has_applied=False
    user=seeker.objects.get(user=request.user)
    job_instance = job.objects.get(id=jobid)
    if application.objects.filter(seeker=user,job=job_instance).exists():
        has_applied=True
    
    context = {
        'job': job_instance,
        'has_applied':has_applied
    }
    return render(request, 'seeker/jobdetails.html', context)


