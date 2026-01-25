from django import forms
from django.forms.formsets import formset_factory
from .models import Recruter,documents
from django.core.exceptions import ValidationError
import re
from django.utils import timezone
import datetime

class recruter_form(forms.Form):
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(required=False)

    image = forms.ImageField(required=False)
    company_name=forms.CharField(max_length=20,required=True)
    company_email=forms.EmailField(required=False)
    website=forms.URLField(required=False)
    phone=forms.CharField( max_length=11, required=False)
    address=forms.CharField(widget=forms.Textarea, required=True)
    decription=forms.CharField(widget=forms.Textarea, required=False)
    industry=forms.CharField(required=True)
    SIZE_CHOICES = [("1-10","1-10 Employees"),("11-50","11-50 Employees"),("51-200","51-200 Employees"),("200+","200+ Employees")]
    size = forms.ChoiceField(choices=SIZE_CHOICES, required=False)
    ORG_CHOICES = [("STARTUP","Startup"),("PRIVATE","Private"),("MNC","MNC"),("CONSULTANCY","Consultancy"),("NGO","NGO")]
    Organization_type = forms.ChoiceField(choices=ORG_CHOICES, required=False)  
    def clean_first_name(self):
        fname=self.cleaned_data.get('first_name')
        if fname:
            if not re.match("^[a-zA-Z ]+$", fname):
                raise ValidationError("Name should only contain alphabets")
            return fname
    
    def clean_last_name(self):
        lname=self.cleaned_data.get('last_name')
        if lname:
            if not re.match("^[a-zA-Z ]+$", lname):
                raise ValidationError("Name should only contain alphabets")
            return lname
    
    def clean_email(self):
        email=self.cleaned_data.get('email')
        if email:
            if not re.match("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
                raise ValidationError("Invalid email format")
            return email
    
    def clean_company_email(self):
        email=self.cleaned_data.get('company_email')
        if email:
            if not re.match("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
                raise ValidationError("Invalid email format")
            return email

    def clean_phone(self):
        phone=self.cleaned_data.get('phone','').strip()
        if phone:
            if not phone.isdigit():
                raise forms.ValidationError('Enter a valid phone number')
            if len(phone) != 10:
                raise forms.ValidationError('Enter a valid phone number')
        return phone
    
    

    def clean(self):
        cleaned_data = super().clean()
        bio=cleaned_data.get("bio","")
        headline=cleaned_data.get("headlin","")
        if bio and len(bio)<10:
            self.add_error("bio","Bio must be atleast 10 characters Long")
        return cleaned_data


class DocumentUploadForm(forms.Form):
    gst_certificate = forms.FileField(required=True, label="GST Certificate")
    registration = forms.FileField(required=True, label="Company Registration")
    pan_card = forms.FileField(required=True, label="Company PAN Card")
    address_proof = forms.FileField(required=True, label="Address Proof")

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

class job_form(forms.Form):
    title = forms.CharField(max_length=50, required=True)
    discription = forms.CharField(widget=forms.Textarea, required=True)
    skills = forms.CharField(widget=forms.Textarea, required=True)
    education = forms.CharField(max_length=50, required=False)
    EXP_CHOICES = [("0-1","0-1 Years"),("1-3","1-3 Years"),("3-5","3-5 Years"),("5+","5+ Years")]
    experience = forms.ChoiceField(choices=EXP_CHOICES, required=True)
    salary = forms.CharField(required=True)
    responsablity = forms.CharField(widget=forms.Textarea, required=False)
    due = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)

    def clean_salary(self):
        salary=self.cleaned_data.get('salary','')
        if salary:
            if not salary.isdigit():
                raise forms.ValidationError('Enter a valid salary')
        return salary

    def clean_due(self):
        due=self.cleaned_data.get('due','')
        if due:
            if due < datetime.date.today():
                raise forms.ValidationError('Due date must be in the future')
        return due
    
    def clean_skills(self):
        skills=self.cleaned_data.get('skills','')
        if skills:
            if len(skills) < 10:
                raise forms.ValidationError('Skills must be atleast 10 characters long')
        return skills

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

