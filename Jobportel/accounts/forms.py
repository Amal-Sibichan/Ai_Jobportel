from os import name
from typing import Required
from django.forms import ModelForm
from django import forms
from Seeker.models import seeker
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
import re

class register(forms.Form):
    name=forms.CharField(max_length=100,required=True)
    role=forms.CharField(max_length=100,required=True)
    email=forms.EmailField(required=True)
    password=forms.CharField(widget=forms.PasswordInput,required=True,min_length=8)
    confirm_password=forms.CharField(widget=forms.PasswordInput,required=True)

    def clean_name(self):
        name=self.cleaned_data.get('name')
        if not re.match("^[a-zA-Z ]+$", name):
            raise ValidationError("Name should only contain alphabets")
        return name
    def clean_email(self):
        email=self.cleaned_data.get('email')
        if not re.match("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            raise ValidationError("Invalid email format")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Password mismatch")
        if password:
            if not re.search(r'[A-Z]', password):
                raise ValidationError("Password must contain atleast 1 uppercase letter")
            if not re.search(r'[a-z]',password):
                raise ValidationError("Password must contain atleast 1 lowercase letter")
            if not re.search(r'[0-9]',password):
                raise ValidationError("Password must contain atleast 1 number")
            if not re.search(r'[@$!%*#?&]',password):
                raise ValidationError("Password must contain atleast 1 special character")

        return cleaned_data

class login_form(forms.Form):
    # role = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        # role = cleaned_data.get('role')

        if not email or not password :
            return cleaned_data

        # user = None

        # if role == 'job_seeker':
        user = authenticate(username=email, password=password)
        # elif role == 'recruiter':
        #     user = Recruter.objects.filter(email=email, password=password).first()
        # else:
        #     raise ValidationError("Invalid role selected")

        if user is None:
            raise ValidationError("Invalid email or password")

        cleaned_data["user"] = user
        return cleaned_data
        



