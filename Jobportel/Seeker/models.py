from django.db import models
from pgvector.django import VectorField

# Create your models here.
class seeker(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField()
    password=models.CharField(max_length=100)
    phone=models.CharField(max_length=15,null=True)
    address=models.CharField(max_length=100,null=True)
    resume=models.FileField(upload_to='resume',null=True)
    city=models.CharField(max_length=100,null=True)
    state=models.CharField(max_length=100,null=True)
    pincode=models.CharField(max_length=100,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    vector = VectorField(dimensions=384,null=True,blank=True)

    def __str__(self):
        return self.name


    
