from django import forms
import re
from .models import Testfiles,Login


class Loginform(forms.Form):
    username = forms.CharField(max_length=10, label="username")
    password = forms.CharField(widget=forms.PasswordInput(), label="password")

    def clean_name(self):
        name = self.cleaned_data['name']
        pattern = r'^\d{2}(pw|pt|pd|pc)\d{2}$'  # Pattern check for username format
        if not re.match(pattern, name):
            raise forms.ValidationError("Invalid Username Format!")
        return name

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        password = cleaned_data.get("password")

        if name and password:
            # Check if the user exists in the database
            if not Login.objects.filter(name=name, password=password).exists():
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