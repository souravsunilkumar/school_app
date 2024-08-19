from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import *

class EmployeeRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    school = forms.ModelChoiceField(queryset=School.objects.none())

    class Meta:
        model = Employee
        fields = ['username', 'password', 'confirm_password', 'school', 'first_name', 'second_name', 'contact_number', 'designation']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(EmployeeRegistrationForm, self).__init__(*args, **kwargs)
        
        # Prefill the school field based on the logged-in school admin
        if self.request and self.request.user.is_authenticated:
            admin_username = self.request.user.username
            try:
                school = School.objects.get(school_admin_username=admin_username)
                self.fields['school'].queryset = School.objects.filter(id=school.id)
                self.fields['school'].initial = school
            except School.DoesNotExist:
                self.fields['school'].queryset = School.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")

        return cleaned_data
    

    
class StudentForm(forms.ModelForm):
    school = forms.ModelChoiceField(
        queryset=School.objects.all(),
        disabled=True,  # Make it read-only
        widget=forms.Select
    )

    class Meta:
        model = Student
        fields = ['admission_number', 'first_name', 'last_name', 'roll_number', 'class_assigned', 'division_assigned', 'school']
        widgets = {
            'class_assigned': forms.TextInput(attrs={'readonly': 'readonly'}),
            'division_assigned': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        if teacher:
            self.fields['school'].initial = teacher.school


class AssignClassTeacherForm(forms.ModelForm):
    class Meta:
        model = Class_Teacher
        fields = ['Teacher', 'first_name', 'last_name', 'class_assigned', 'division_assigned']

    def __init__(self, *args, **kwargs):
        school = kwargs.pop('school', None)
        super(AssignClassTeacherForm, self).__init__(*args, **kwargs)
        if school:
            # Filter teachers by school
            self.fields['Teacher'].queryset = Teacher.objects.filter(school=school)
        
        # Disable first_name and last_name fields (they will be filled automatically)
        self.fields['first_name'].widget.attrs['readonly'] = True
        self.fields['last_name'].widget.attrs['readonly'] = True
        self.fields['Teacher'].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        teacher = cleaned_data.get('Teacher')
        class_assigned = cleaned_data.get('class_assigned')
        division_assigned = cleaned_data.get('division_assigned')
        school = self.instance.school

        if teacher:
            # Check if the teacher is already a class teacher
            if Class_Teacher.objects.filter(Teacher=teacher).exists() or teacher.is_class_teacher:
                self.add_error('Teacher', 'This teacher is already a class teacher.')

            # Check if another teacher is already assigned to this class and division in the same school
            if Class_Teacher.objects.filter(school=school, class_assigned=class_assigned, division_assigned=division_assigned).exists():
                self.add_error(None, 'A teacher is already assigned to this class and division in this school.')