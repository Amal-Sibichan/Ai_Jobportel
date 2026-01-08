from django import forms
from .models import seeker
from django.core.exceptions import ValidationError
import re

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
        