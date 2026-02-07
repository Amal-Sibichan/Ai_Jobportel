from django import forms
from .models import seeker
from django.core.exceptions import ValidationError
import re
import datetime
from datetime import date
from django.utils import timezone


class profileupdateform(forms.Form):
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(required=False)
    
    # Seeker model fields
    image = forms.ImageField(required=False)
    headline=forms.CharField(max_length=100, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    phone = forms.CharField(max_length=10, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    city = forms.CharField(max_length=100, required=False)
    state = forms.CharField(max_length=100, required=False)
    pincode = forms.CharField(max_length=100, required=False)

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
    def clean_phone(self):
        phone=self.cleaned_data.get('phone','').strip()
        if phone:
            if not phone.isdigit():
                raise forms.ValidationError('Enter a valid phone number')
            if len(phone) != 10:
                raise forms.ValidationError('Enter a valid phone number')
        return phone
    
    def clean_pincode(self):
        pincode=self.cleaned_data.get('pincode','').strip()
        if pincode:
            if not pincode.isdigit():
                raise forms.ValidationError('Enter a valid pincode')
            if len(pincode) != 6:
                raise forms.ValidationError('Enter a valid pincode')
        return pincode
    
    def clean_city(self):
        city=self.cleaned_data.get('city','').strip()
        if city:
            if not city.isalpha():
                raise forms.ValidationError('Enter a valid city')
            if len(city) <2:
                raise forms.ValidationError('Enter a valid city')
        return city
    
    def clean_state(self):
        state=self.cleaned_data.get('state','').strip()
        if state:
            if not state.isalpha():
                raise forms.ValidationError('Enter a valid State')
            if len(state) < 2:
                raise forms.ValidationError('Enter a Valid state')
        return state


    

    def clean(self):
        cleaned_data = super().clean()
        bio=cleaned_data.get("bio","")
        headline=cleaned_data.get("headlin","")
        if bio and len(bio)<10:
            self.add_error("bio","Bio must be atleast 10 characters Long")
        return cleaned_data


class upload_resume(forms.Form):
    resume=forms.FileField()

    def clean(self):
        return super().clean()

class education_form(forms.Form):
    LEVEL_CHOICES = [("Degree","Degree"),("Diploma","Diploma"),("PG","PG"),("SSLC","SSLC"),("HSC","HSC")]
    level = forms.ChoiceField(choices=LEVEL_CHOICES, required=False)
    institution = forms.CharField(max_length=100)
    course = forms.CharField(max_length=50)
    start = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)

    def clean_institution(self):
        inst=self.cleaned_data.get('institution')
        if inst:
            if len(inst) < 3:
                self.add_error("institution", "Enter a valid institution")
        return inst

    def clean_course(self):
        course=self.cleaned_data.get('course')
        if course and len(course) < 2:
            self.add_error("course", "Enter a valid course")
        return course
    def clean_description(self):
        des=self.cleaned_data.get('description')
        if des and len(des) < 10:
            self.add_error("description","Description must be atleast 10 characters Long")
        return des

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start")
        end = cleaned_data.get("end")

        if start and start > datetime.date.today():
            self.add_error("start", "Enter a valid date")

        if start and end and end < start:
            self.add_error("end", "Enter a valid date")
        return cleaned_data

class experience_form(forms.Form):
    company = forms.CharField( max_length=30, required=True)
    title = forms.CharField(max_length=50,required=True)
    description = forms.CharField(widget=forms.Textarea,required=False)
    start = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}),required=True)
    end = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}),required=False)

    def clean_company(self):
        company=self.cleaned_data.get('company')
        if company and len(company) < 2:
            self.add_error("company", "Enter a valid company")
        return company

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title and len(title) < 2:
            self.add_error("title", "Enter a valid title")
        return title 

    def clean_description(self):
        des=self.cleaned_data.get('description')
        if des and len(des) < 10:
            self.add_error("description","Description must be atleast 10 characters Long")
        return des


    def clean(self):
        print("CLEAN() IS RUNNING")
        cleaned_data = super().clean()
        start = cleaned_data.get("start")
        end = cleaned_data.get("end")

        if start and start > date.today():
            self.add_error("start", "Enter a valid date")

        if start and end and end < start:
            self.add_error("end", "Enter a valid date")
        return cleaned_data