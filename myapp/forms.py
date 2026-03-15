from django import forms
import re
from .models import Testfiles, Login
from django.contrib.auth.hashers import make_password, check_password


class Loginform(forms.Form):
    username = forms.CharField(max_length=10, label="username")
    password = forms.CharField(widget=forms.PasswordInput(), label="password")

    def clean_name(self):
        name = self.cleaned_data['name']
        pattern = r'^\d{2}(pw|pt|pd|pc)\d{2}$'
        if not re.match(pattern, name):
            raise forms.ValidationError("Invalid Username Format!")
        return name

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        password = cleaned_data.get("password")

        if name and password:
            user = Login.objects.filter(name=name).first()
            if not user or not check_password(password, user.password):
                raise forms.ValidationError("Invalid username or password!")

        return cleaned_data


# Student Registration Form
class StudentRegistrationForm(forms.Form):
    username = forms.CharField(max_length=10, label="Username", 
        help_text="Format: 23pw001 (YYcourseIDnumber)")
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")

    def clean_username(self):
        username = self.cleaned_data['username']
        pattern = r'^\d{2}(pw|pt|pd|pc)\d{2}$'
        if not re.match(pattern, username):
            raise forms.ValidationError("Invalid Username Format! Use format: 23pw001")
        if Login.objects.filter(name=username).exists():
            raise forms.ValidationError("Username already exists!")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match!")
            if len(password) < 6:
                raise forms.ValidationError("Password must be at least 6 characters")

        return cleaned_data


# Teacher Registration Form
class TeacherRegistrationForm(forms.Form):
    username = forms.CharField(max_length=50, label="Username")
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")

    def clean_username(self):
        username = self.cleaned_data['username']
        from .models import TeacherLogin
        if TeacherLogin.objects.filter(name=username).exists():
            raise forms.ValidationError("Username already exists!")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match!")
            if len(password) < 6:
                raise forms.ValidationError("Password must be at least 6 characters")

        return cleaned_data


# Separate Login Forms for Student and Teacher
class StudentLoginForm(forms.Form):
    username = forms.CharField(max_length=10, label="Username")
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            user = Login.objects.filter(name=username).first()
            if not user or not check_password(password, user.password):
                raise forms.ValidationError("Invalid username or password!")

        return cleaned_data


class TeacherLoginForm(forms.Form):
    username = forms.CharField(max_length=50, label="Username")
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            from .models import TeacherLogin
            user = TeacherLogin.objects.filter(name=username).first()
            if not user or not check_password(password, user.password):
                raise forms.ValidationError("Invalid username or password!")

        return cleaned_data


class FileUploadForm(forms.ModelForm):
    startTime = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "step": 1}), 
        required=True
    )
    endTime = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "step": 1}), 
        required=True
    )

    class Meta:
        model = Testfiles
        fields = ['name', 'Qfiles', 'Afiles', 'startTime', 'endTime', 'courseCode']
