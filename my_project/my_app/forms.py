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

        if self.request and self.request.user.is_authenticated:
            user = self.request.user

            if user.groups.filter(name='main administrator').exists():
                # Main administrator should see the school they manage
                try:
                    admin = Admin.objects.get(user=user)
                    self.fields['school'].queryset = School.objects.filter(id=admin.school.id)
                    self.fields['school'].initial = admin.school
                except Admin.DoesNotExist:
                    self.fields['school'].queryset = School.objects.none()
            
            elif user.groups.filter(name='sub_admins').exists():
                # Sub-admin should see the school they are associated with
                try:
                    admin = Admin.objects.get(user=user)
                    self.fields['school'].queryset = School.objects.filter(id=admin.school.id)
                    self.fields['school'].initial = admin.school
                except Admin.DoesNotExist:
                    self.fields['school'].queryset = School.objects.none()
            
            else:
                self.fields['school'].queryset = School.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")

        return cleaned_data
    
class SubAdminRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)
    sub_admin_first_name = forms.CharField(max_length=30, required=True)
    sub_admin_last_name = forms.CharField(max_length=30, required=True)
    sub_admin_school = forms.ModelChoiceField(queryset=School.objects.none(), required=True)
    contact_number = forms.CharField(max_length=15, required=True)

    class Meta:
        model = Admin
        fields = ['username', 'password', 'confirm_password', 'sub_admin_first_name', 'sub_admin_last_name', 'sub_admin_school', 'contact_number']

    def __init__(self, *args, **kwargs):
        school = kwargs.pop('school', None)
        super().__init__(*args, **kwargs)
        if school:
            self.fields['sub_admin_school'].queryset = School.objects.filter(id=school.id)
            self.fields['sub_admin_school'].initial = school

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")

        return cleaned_data

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

        # Store the school for use in the save method
        self.school = school

    def clean(self):
        cleaned_data = super().clean()
        teacher = cleaned_data.get('Teacher')
        class_assigned = cleaned_data.get('class_assigned')
        division_assigned = cleaned_data.get('division_assigned')
        
        if teacher:
            # Check if the teacher is already a class teacher
            if Class_Teacher.objects.filter(Teacher=teacher).exists() or teacher.is_class_teacher:
                self.add_error('Teacher', 'This teacher is already a class teacher.')

            # Check if another teacher is already assigned to this class and division in the same school
            if Class_Teacher.objects.filter(school=self.school, class_assigned=class_assigned, division_assigned=division_assigned).exists():
                self.add_error(None, 'A teacher is already assigned to this class and division in this school.')

    def save(self, commit=True):
        class_teacher = super().save(commit=False)
        teacher = self.cleaned_data.get('Teacher')
        
        # Set the school before saving the instance
        class_teacher.school = self.school
        
        # Save the username of the teacher
        class_teacher.user_name = teacher.user_name
        class_teacher.first_name = teacher.first_name
        class_teacher.last_name = teacher.last_name
        
        if commit:
            class_teacher.save()
        return class_teacher
    

class AddStudentForm(forms.ModelForm):
    warden = forms.ModelChoiceField(
        queryset=Warden.objects.none(),  # This will be updated in the view
        required=False,  # Allow this field to be empty
        empty_label="Not a hosteler"
    )
    
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'gender', 'admission_number', 'roll_number', 'parents_number', 'parents_email', 'class_assigned', 'division_assigned', 'warden']

    def __init__(self, *args, **kwargs):
        class_teacher = kwargs.pop('class_teacher', None)
        school = kwargs.pop('school', None)
        super(AddStudentForm, self).__init__(*args, **kwargs)

        if class_teacher:
            # Prefill the class_assigned and division_assigned fields
            self.fields['class_assigned'].initial = class_teacher.class_assigned
            self.fields['division_assigned'].initial = class_teacher.division_assigned
        if school:
            # Filter wardens by school
            self.fields['warden'].queryset = Warden.objects.filter(school=school)

        # Disable the fields to prevent changes
        self.fields['class_assigned'].widget.attrs['readonly'] = True
        self.fields['division_assigned'].widget.attrs['readonly'] = True

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['exam_name']

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['subject_name']