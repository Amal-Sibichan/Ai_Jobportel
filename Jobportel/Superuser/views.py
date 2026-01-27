from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.admin.views.decorators import staff_member_required
from Seeker.models import seeker
from recruiter.models import Recruter, documents
from django.contrib.auth.models import User
@staff_member_required
def admin_home(request):
    total_seekers = seeker.objects.count()
    total_recruters = Recruter.objects.count()
    pending_approvals = Recruter.objects.filter(approval_status="PENDING").count()
    
    # User Lists
    seekers = seeker.objects.all().order_by('-created_at')[:5] # Latest 5
    recruters = Recruter.objects.all().order_by('-created_at')
    
    context = {
        'total_seekers': total_seekers,
        'total_recruters': total_recruters,
        'pending_approvals': pending_approvals,
        'seekers': seekers,
        'recruters': recruters,
    }
    return render(request,'admin/home.html',context)

def verify(request,u_id):
    recruter_instance=Recruter.objects.get(id=u_id)
    docs, created = documents.objects.get_or_create(recruter=recruter_instance)
    return render(request,'admin/verify_docs.html',{'employer':recruter_instance,'docs':docs})

def update(request,r_id):
    recruter_instance=Recruter.objects.get(id=r_id)
    docs, created = documents.objects.get_or_create(recruter=recruter_instance)
    if request.method == 'POST':
        docs.registration_verified = 'registration_verified' in request.POST
        docs.pan_verified = 'pan_verified' in request.POST
        docs.address_proof_verified = 'address_proof_verified' in request.POST
        docs.gst_verified = 'gst_verified' in request.POST
        docs.save()

        if docs.is_documents_complete() and docs.all_documents_verified():
            recruter_instance.approval_status = "APPROVED"
            recruter_instance.save()
        else:
            recruter_instance.approval_status = "PENDING"
            recruter_instance.save()
    return HttpResponse("saved sucessfully")