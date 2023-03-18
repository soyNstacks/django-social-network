from django import forms
from django.forms import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


from datetime import datetime
import pytz 
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _

from .models import * 

MAX_UPLOAD_SIZE = "5242880" # 5MB file size limit
   
class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=255, label='First Name', 
                                 required=True, 
                                 widget=forms.TextInput(attrs={
        'class': 'form-control', 'autocomplete': 'off',
        'placeholder': 'First Name'}))
    
    last_name = forms.CharField(max_length=255, label='Last Name', 
                                required=True, 
                                widget=forms.TextInput(attrs={
        'class': 'form-control', 'autocomplete': 'off',
        'placeholder': 'Last Name'}))
    
    email = forms.EmailField(max_length=255, 
                            label='Email', 
                            required=True, 
                            widget=forms.TextInput(attrs={
        'placeholder': 'Enter your email address'}))
    
    password1 = forms.CharField(label='Password', required=True, 
                                widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'autocomplete': 'off'}))
    
    password2 = forms.CharField(label='Confirm Password', required=True, 
                                widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'autocomplete': 'off', "minlength": 8}))

    class Meta: 
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2', )
        
    
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        # source: https://stackoverflow.com/questions/66292877/i-want-email-has-to-be-unique
        email_to_find = User.objects.exclude(username=self.instance.username)\
                        .filter(email=email)
        
        if email_to_find.exists():
            raise ValidationError('A user with this email address already exists.')
        return email

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False) 
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        
        if commit:
            user.save()
        return user


class UserExtraFieldsForm(forms.ModelForm):
    date_of_birth = forms.DateField(label='Date of Birth', widget=forms.DateInput(
        format=('%Y-%m-%d'), attrs={'type': 'date', 'class': 'form-control'}))
    
    profile_picture = forms.ImageField(label='Upload Profile Picture', 
                                       required=False, error_messages = {
        'invalid': "Only image file formats like jpg"}, 
        widget=forms.FileInput)

    class Meta:
        model = UserProfile
        fields = ('date_of_birth', 'profile_picture')

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get("date_of_birth")
        # source: https://stackoverflow.com/questions/65126644/how-to-only-accept-date-inputs-of-more-than-18-years-ago-in-django
        current_date = datetime.now(pytz.utc).date()
        age = (current_date - date_of_birth).days / 365
        if age < 0:
            raise ValidationError("Invalid date of birth entered: exceeds current year.")
        elif age < 13.0 and age >= 0:
            raise ValidationError("You must be at least 13 years old to sign up.")
        elif age > 116:
            raise ValidationError("Invalid date of birth entered: year.") 
        return date_of_birth
        
    def save(self, commit=True):
        add_fields = super(UserExtraFieldsForm, self).save(commit=False)
        add_fields.date_of_birth = self.cleaned_data["date_of_birth"]

        if commit:
            add_fields.save() 
        return add_fields
        

class EditUserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Email / Username')

    
class PostForm(forms.ModelForm):
    body_text = forms.CharField(label='Text', widget=forms.Textarea(attrs={
        'class': 'form-control', 'rows': 1, 'placeholder': "What's up?"}))
    media = forms.FileField(label='Upload Media', required=False, error_messages = {
        'invalid': "Only image file formats like jpg, or video formats like mp4 allowed."}, widget=forms.FileInput)

    class Meta:
        model = Post
        fields = ('body_text', 'media')

    def clean_media(self):
        media_content = self.cleaned_data["media"]
        content_type = self.instance.media_type
        if content_type == 'video' and media_content._size > int(MAX_UPLOAD_SIZE):
            raise forms.ValidationError(_(f"File limit exceeded. Maximum file size: 5MB"))
        return media_content

    def save(self, commit=True):
        fields = super(PostForm, self).save(commit=False)
        fields.media = self.cleaned_data["media"]

        if commit:
            fields.save()
        return fields
