from random import choice, choices
from django.db import models
from django.db.models.fields import related
from huggingface_hub import Organization
from spacy import blank, registrations
from django.contrib.auth.models import User
from pgvector.django import VectorField

class Recruter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name=models.CharField(max_length=200)
    company_email=models.EmailField(null=True,blank=True)
    website=models.URLField(null=True,blank=True)
    phone=models.CharField(max_length=11,null=True,blank=True)
    address=models.TextField(null=True,blank=True)
    decription=models.CharField(max_length=500,null=True,blank=True)
    logo = models.ImageField(upload_to='company_logos', null=True, blank=True)
    size=models.CharField(max_length=20,choices=[("1-10","1-10 Employees"),("11-50","11-50 Employees"),("51-200","51-200 Employees"),("200+","200+ Employees")])
    industry=models.CharField(max_length=100,help_text="Example: IT,Finance,Helthcare etc..")
    Organization_type=models.CharField(max_length=20,choices=[("STARTUP","Startup"),("PRIVATE","Private"),("MNC","MNC"),("CONSULTANCY","Consultancy"),("NGO","NGO")])
    approval_status=models.CharField(max_length=20,choices=[("PENDING","Pending"),("APPROVED","Approved"),("REJECTED","Rejected")],default="PENDING")
    sub_status = models.CharField(max_length=20,choices=[("FREE","Free"),("PENDING_PAYMENT","Pending_payment"),("ACTIVE","Active"),("EXPIRED","Expired")],default="FREE")
    sub_due = models.DateField(null=True,blank=True)
    created_at = models.DateField(auto_now_add=True) 
    def is_profile_complete(self):
        required_fields = [
            self.company_name, 
            self.company_email, 
            self.website, 
            self.phone, 
            self.address, 
            self.industry,
            self.Organization_type,
            self.size,
            self.decription,
        ]
        return all(required_fields)

    def __str__(self):
        return self.company_name

class documents(models.Model):
    recruter=models.OneToOneField(Recruter,on_delete=models.CASCADE,related_name="documents")
    gst_certificate=models.FileField(upload_to='recruter_docs/gst',null=True,blank=True)
    registration=models.FileField(upload_to='recruter_docs/registration',null=True,blank=True)
    pan_card=models.FileField(upload_to='recruter_docs/pan',null=True,blank=True)
    address_proof=models.FileField(upload_to='recruter_docs/address_proof',null=True,blank=True)
    
    gst_verified = models.BooleanField(default=False)
    registration_verified = models.BooleanField(default=False)
    pan_verified = models.BooleanField(default=False)
    address_proof_verified = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_documents_complete(self):
        required_fields=[
            self.gst_certificate,
            self.registration,
            self.pan_card,
            self.address_proof,
        ]
        return all(required_fields)

    def all_documents_verified(self):
        return self.gst_verified and self.registration_verified and self.pan_verified and self.address_proof_verified

    def __str__(self):
        return self.recruter.company_name


    

    
class job(models.Model):
    recruter = models.ForeignKey(Recruter,on_delete=models.CASCADE,related_name='jobs')
    title = models.CharField(max_length=50,null=True,blank=True)
    discription = models.TextField(null=True,blank=True)
    skills = models.JSONField(null=True,blank=True)
    education = models.CharField(max_length=50,null=True,blank=True)
    experience = models.CharField(max_length=20,choices=[("0-1","0-1 Years"),("2-5","2-5 Years"),("5+","5+ Years")])
    salary = models.CharField(null=True,blank=True)
    responsablity = models.TextField(null=True,blank=True)
    job_vector = VectorField(dimensions=384,null=True,blank=True)
    due = models.DateField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.recruter.company_name
    



    

