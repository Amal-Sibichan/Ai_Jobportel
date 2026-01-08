from django.db import models
from django.contrib.auth.models import User

from pgvector.django import VectorField

# Create your models here.
class seeker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pics',null=True,blank=True)
    phone=models.CharField(max_length=15,null=True)
    headline=models.CharField(max_length=15,null=True)
    discription=models.CharField(max_length=15,null=True)
    address=models.CharField(max_length=100,null=True)
    city=models.CharField(max_length=100,null=True)
    state=models.CharField(max_length=100,null=True)
    pincode=models.CharField(max_length=100,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

class resume(models.Model):
    seeker=models.OneToOneField(seeker,on_delete=models.CASCADE,related_name="resume")
    resume=models.FileField(upload_to='resume',null=True)
    resume_vector = VectorField(dimensions=384,null=True,blank=True)
    resume_text=models.TextField(null=True,blank=True)
    ats_score=models.FloatField(default=0.0)
    semantic_score=models.FloatField(default=0.0)
    skills=models.JSONField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.seeker.user.username

class Education(models.Model):
    seeker=models.ForeignKey(seeker,on_delete=models.CASCADE,related_name="education")
    level=models.CharField( max_length=50,)
    institution=models.CharField(max_length=100,null=True,blank=True)
    course=models.CharField(max_length=50,null=True,blank=True)
    start=models.DateField()
    end=models.DateField(null=True,blank=True)
    description=models.TextField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.level} - {self.institution}"

class Experience(models.Model):
    seeker=models.ForeignKey(seeker,on_delete=models.CASCADE,related_name="experiences")
    company=models.CharField(max_length=100,null=True,blank=True)
    title=models.CharField(max_length=100,null=True,blank=True)
    start=models.DateField()
    end=models.DateField(null=True,blank=True)
    description=models.TextField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.title} - {self.company}"

class skill(models.Model):
    seeker=models.ForeignKey(seeker,on_delete=models.CASCADE,related_name="skills")
    name=models.CharField(max_length=100,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name


