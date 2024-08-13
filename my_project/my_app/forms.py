from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import *

class TeacherRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    class_assigned = forms.CharField(max_length=20)
    division_assigned = forms.CharField(max_length=10)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
    
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['admission_number', 'first_name', 'last_name', 'roll_number', 'class_assigned', 'division_assigned']
        widgets = {
            'class_assigned': forms.TextInput(attrs={'readonly': 'readonly'}),
            'division_assigned': forms.TextInput(attrs={'readonly': 'readonly'}),
        }