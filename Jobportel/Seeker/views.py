from django.shortcuts import render
import json
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from .models import Experience, seeker,skill,Education
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