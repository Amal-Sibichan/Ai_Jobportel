from django.shortcuts import redirect,render,get_object_or_404
from recruiter.models import *
from Seeker.models import *
from django.contrib.auth.models import *
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST, require_http_methods
from Seeker.utils import extract,entity_score_spacy,atscore,pool_score,semantic_similarity,jaccard_skill_score,generate_vector,send_shortlist_email
from Seeker.LLM import resume_bot
from .forms import *
from django.http import HttpResponse,JsonResponse
from django.contrib import messages
import datetime
from django.db.models import Q
import json
import razorpay
from django.conf import settings
from datetime import timedelta
from django.utils import timezone

def is_recruter(user):
    return hasattr(user, 'recruter')

@login_required
@user_passes_test(is_recruter, login_url='/access-denied/')
def recruter_home(request):
    emp_obj=Recruter.objects.get(user=request.user)
    jobs=job.objects.filter(recruter=emp_obj).order_by('-created_at')[:5]
    job_count=job.objects.filter(recruter=emp_obj).count()
    application_count=application.objects.filter(job__recruter=emp_obj).count()
    today=datetime.date.today()
    return render(request,'Recruter_temp/recruter_home.html',{'employer':emp_obj,'jobs':jobs,'today':today,'job_count':job_count,'application_count':application_count})

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
            if 'logo' in request.FILES:
                current_recruter.logo = request.FILES['logo']
            current_recruter.save()
            messages.success(request, 'Profile updated successfully!')
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
            messages.success(request,'Documents uploaded. Wait for admin approvel ')
            return redirect('recruiter:upload_docs')
    else:
        form=DocumentUploadForm()
    return render(request, 'recruter_temp/upload_docs.html',{'form':form,'docs':docs})
    
@login_required
@user_passes_test(is_recruter, login_url='/access-denied/')
def post_job(request):
    
    try:
        current_recruter = Recruter.objects.get(user=request.user)
    except Recruter.DoesNotExist:
        messages.warning(request, "Please complete your recruiter profile first.")
        
    try:
        docs=documents.objects.get(recruter=current_recruter)
    except documents.DoesNotExist:
        messages.warning(request, "Please upload all required documents.")
        return redirect('recruiter:upload_docs')


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
            banner = form.cleaned_data['banner']
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
            new_job = job.objects.create(title=title, discription=discription, skills=skills_list, education=education, experience=experience, salary=salary, responsablity=responsablity,job_vector=job_vector, due=due, recruter=current_recruter,banner=banner)
            new_job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('recruiter:recruter_page')
    else:
        form = job_form()
    

    return render(request, 'recruter_temp/Post_job.html', {'form': form})

def update_jobs(request,job_id):
    current_job=get_object_or_404(job,id=job_id)
    current_recruter = Recruter.objects.get(user=request.user)
    skill_string = ",".join(current_job.skills)
    if request.method == 'POST':
        form=job_form(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            discription = form.cleaned_data['discription']
            education = form.cleaned_data['education']
            experience = form.cleaned_data['experience']
            salary = form.cleaned_data['salary']
            responsablity = form.cleaned_data['responsablity']
            due = form.cleaned_data['due']
            banner = form.cleaned_data['banner']
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
            current_job.title=title
            current_job.discription = discription
            current_job.skills = skills_list
            current_job.education = education
            current_job.experience = experience
            current_job.salary = salary
            current_job.responsablity = responsablity
            current_job.job_vector = job_vector
            current_job.due = due
            if 'banner' in request.FILES:
                current_job.banner = request.FILES['banner']
            current_job.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('recruiter:recruter_home')
    else:
        form = job_form(initial={
            'title':current_job.title,
            'discription':current_job.discription,
            'education':current_job.education,
            'experience':current_job.experience,
            'salary':current_job.salary,
            'responsablity':current_job.responsablity,
            'due':current_job.due,
            'skills':skill_string,

        })

    return render(request,'recruter_temp/update_job.html',{'form':form,'job':current_job})

@login_required
@user_passes_test(is_recruter, login_url='/access-denied/')
def job_list(request):
    try:
        current_recruter=Recruter.objects.get(user=request.user)
        jobs = job.objects.filter(recruter=current_recruter)
        count=jobs.count()
        today=datetime.date.today()
        q = request.GET.get('q')
        if q:
            jobs = jobs.filter(
                Q(title__icontains=q)|
                Q(recruter__company_name__icontains=q)|
                Q(created_at__icontains=q)
            )
        return render(request, 'recruter_temp/job_list.html', {'jobs': jobs,'count':count,'today':today})
    except Exception as e:
        print(f"Error fetching job list: {e}")
        return HttpResponse(f"ERROR: {e}")
        messages.error(request, "An error occurred while fetching your job listings.")
        return render(request, 'recruter_temp/job_list.html', {'jobs': []})

@login_required
@user_passes_test(is_recruter, login_url='/access-denied/')
def candidate_pool(request,job_id):
    current_recruter=Recruter.objects.get(user=request.user)
    if not check_subscription(current_recruter):
        messages.error(request, "Your subscription has expired. Please renew.")
        return redirect("recruiter:subscription")
    if not current_recruter.plan.resume_pooling:
        return redirect('recruiter:list',job_id=job_id)

    target_job = get_object_or_404(job, id=job_id)
    app_data=application.objects.filter(job_id=job_id).select_related('seeker__user','job')
    count={
        'excellent': app_data.filter(category='excellent').count(),
        'good': app_data.filter(category='good').count(),
        'low': app_data.filter(category='low').count(),
        'total': app_data.count()
    }
    
    return render(request,'recruter_temp/candidate_list.html',{'data':app_data,'count':count,'job':target_job})
    
@login_required
@user_passes_test(is_recruter, login_url='/access-denied/')
def candidate_details(request,candidate_id,job_id):
    recruiter = Recruter.objects.get(user=request.user)
    candidate = get_object_or_404(seeker, id=candidate_id)
    jobs = get_object_or_404(job, id=job_id)
    app = get_object_or_404(application, seeker=candidate, job=jobs)
    experience=Experience.objects.filter(seeker=candidate).order_by("-id").first()
    education = Education.objects.filter(seeker=candidate).order_by("id").first()
    matched = app.matched_skills.split(", ") if app.matched_skills else []
    unmatched = app.unmatched_skills.split(", ") if app.unmatched_skills else []
    return render(request,'recruter_temp/candidate_details.html',{'candidate':candidate,'job':jobs,'app':app,'matched':matched,'unmatched':unmatched,'edu':education,'exp':experience,'recruter':recruiter})

def ask_bot(request):
    if request.method == "POST":
        try:
            # 1. Parse JSON from the frontend
            data = json.loads(request.body)
            user_question = data.get('message')
            app_id = data.get('user_id') # The ID you are passing from JS

            # 2. Fetch the "Triple Context" using select_related for speed
            # This pulls Application + Job + Seeker + User in ONE query
            app = application.objects.select_related('job', 'seeker', 'seeker__user').get(id=app_id)
            
            # 3. Build the Data Bundle for the LLM
            context_bundle = {
                "resume_text": app.seeker.resume.resume_text,
                "job_title": app.job.title,
                "job_requirements": app.job.discription, # Or app.job.skills
                "final_score": app.final_score,
                "matched": app.matched_skills,
                "unmatched": app.unmatched_skills,
                "ats_format_score": app.ats_score
            }

            # 4. Get the AI Answer
            ai_reply = resume_bot(context_bundle, user_question)
            
            return JsonResponse({'reply': ai_reply})

        except application.DoesNotExist:
            return JsonResponse({'reply': "Error: Could not find that application record."}, status=404)
        except Exception as e:
            # Check your terminal for this print if you get a 500 error!
            print(f"Chatbot Logic Error: {e}")
            return JsonResponse({'reply': f"I'm sorry, I encountered an error: {str(e)}"}, status=500)

    return JsonResponse({'reply': "Invalid Request"}, status=400)


def shorlist(request,app_id):
    app = application.objects.select_related('job', 'seeker', 'seeker__user').get(id=app_id)
    job_id = app.job_id
    user_id = app.seeker_id
    app.status = "SHORTLISTED"
    app.save()
    return redirect('recruiter:candidate_details', candidate_id=user_id,job_id=job_id)

@login_required
def shortlist_candidate(request, app_id):
    app = application.objects.get(id=app_id)

    

    # Get candidate details
    candidate = app.seeker.user
    recruiter = app.job.recruter
    # Send email
    send_shortlist_email(
        candidate_email=candidate.email,
        candidate_name=candidate.username,
        job_title=app.job.title,
        company=recruiter.company_name
    )
    # Update status
    app.status = "SHORTLISTED"
    app.save()

    messages.success(request, "Candidate shortlisted and email sent.")
    return redirect("recruiter:job_list")

def  Reject(request,app_id):
    app = application.objects.select_related('job', 'seeker', 'seeker__user').get(id=app_id)
    job_id = app.job_id
    user_id = app.seeker_id
    app.status = "REJECTED"
    app.save()
    return redirect('recruiter:candidate_details', candidate_id=user_id,job_id=job_id)



@staff_member_required
def add_plan(request):
    if request.method == "POST":
        form = PlanForm(request.POST)
        if form.is_valid():
            # Manually saving the data into the model
            Plan.objects.create(
                name=form.cleaned_data['name'],
                price=form.cleaned_data['price'],
                job_limit=form.cleaned_data['job_limit'],
                duration=form.cleaned_data['duration'],
                resume_pooling=form.cleaned_data['resume_pooling'],
                ai_chat=form.cleaned_data['ai_chat'],
                is_active=form.cleaned_data['is_active'],
            )
            messages.success(request,'Plan added')
            return redirect('recruiter:add_Plan')
    else:
        form = PlanForm()
    
    return render(request, 'admin/add_Plan.html', {'form': form})


def subscription(request):
    plans=Plan.objects.all()
    return render(request,'Recruter_temp/subscription.html',{'plans':plans})   




@login_required
@user_passes_test(is_recruter, login_url='/access-denied/')
def create_payment(request,plan_id):
    request.session["plan_id"] = plan_id
    plan = Plan.objects.get(id=plan_id)

    if plan.price == 0:
        # FREE plan
        recruiter = Recruter.objects.get(user=request.user)
        recruiter.sub_status = "ACTIVE"
        recruiter.sub_due = None
        recruiter.plan = plan
        recruiter.save()
        return redirect("recruiter:recruter_page")

    amount = plan.price * 100  # Razorpay uses paise

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": "1"
    })

    return render(request, "Recruter_temp/payment.html", {
        "order_id": order["id"],
        "amount": amount,
        "key": settings.RAZORPAY_KEY_ID
    })


@login_required
@user_passes_test(is_recruter, login_url='/access-denied/')
def payment_success(request):
    plan_id = request.session.get("plan_id")
    plan = Plan.objects.get(id=plan_id)

    recruiter = Recruter.objects.get(user=request.user)

    recruiter.sub_status = "ACTIVE"
    recruiter.sub_due = timezone.now().date() + timedelta(days=plan.duration)
    recruiter.plan = plan
    recruiter.save()

    del request.session["plan_id"]

    return render(request, "Recruter_temp/payment_success.html",{'plan':plan})



def check_subscription(recruiter):
    if recruiter.sub_status != "ACTIVE":
        return False

    if recruiter.sub_due and recruiter.sub_due < timezone.now().date():
        recruiter.sub_status = "FREE"
        recruiter.sub_due = None
        recruiter.save()
        return False
    
    

    return True


def subscription_detials(request):
    current_recruter=Recruter.objects.get(user=request.user)
    jobs_posted = job.objects.filter(recruter=current_recruter).count()
    
    # Calculate progress bar percentage
    if current_recruter.plan and current_recruter.plan.job_limit:
        usage_percent = (jobs_posted / current_recruter.plan.job_limit) * 100
    else:
        usage_percent = 0

    return render(request, 'Recruter_temp/subscription_detials.html', {
        'recruiter': current_recruter,
        'jobs_posted': jobs_posted,
        'usage_percent': usage_percent,
    })


def list(request,job_id):
    recruiter = get_object_or_404(Recruter, user=request.user)

    # Get the job (ensure it belongs to this recruiter)
    job_obj = get_object_or_404(job, id=job_id, recruter=recruiter)

    # Get all applications for this job
    applications = (
        application.objects
        .filter(job=job_obj)
        .select_related("seeker", "seeker__user")
    )

    context = {
        "job": job_obj,
        "applications": applications,
    }
    return render(request,'Recruter_temp/list.html',context)

