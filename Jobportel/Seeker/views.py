from django.core.checks.messages import Info
from django.shortcuts import render
import json
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from numpy import info
from .models import Experience, seeker,skill,Education,resume
from .forms import profileupdateform,upload_resume
from .utils import extract,entity_score_spacy,atscore,pool_score,semantic_similarity,jaccard_skill_score,generate_vector
from .LLM import extract_skills_llm
# Create your views here.
def user_dash(request):
    return HttpResponse("user dash")
@login_required
def profile(request):
    user=request.user
    seeker=getattr(user,"seeker",None)
    resume=getattr(seeker,"resume",None)
    Experiences=seeker.experiences.all()
    Education=seeker.education.all()
    skills=seeker.skills.all()
    
    return render(request,'seeker/profile.html',{'user':user,'skills':skills})

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
            return HttpResponse("Profile Updated ")
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
            if user_res.resume.resume:
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
            new_res = resume.objects.create(resume=res,seeker=user_res,resume_vector=vector_Emp,resume_text=res_text,ats_score=ats_score,semantic_score=entity_score,skills=skill_list)
            new_res.save()
            return HttpResponse("Resume Uploaded")