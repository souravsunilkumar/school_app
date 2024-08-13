from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import *
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import *
# Create your views here.

def BASE(req):
    return render(req,'base.html')

def Login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Check if the authenticated user belongs to the group with group id=1 (Teacher)
            teacher_group = Group.objects.get(id=1)
            if teacher_group in user.groups.all():
                return redirect('teacher_dashboard')
            # Add other group-based redirections here if needed
            else:
                return redirect('login')  # Redirect to a default dashboard
        else:
            # Invalid login credentials
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

def Parent_Reg(req):
    return render(req,'parent_register.html')


def Teacher_Reg(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            # Save the user to the User model
            user = form.save()
            
            # Add the user to the 'teacher' group
            teacher_group = Group.objects.get(name='teacher')
            user.groups.add(teacher_group)

            # Create the Teacher_Model entry
            class_assigned = form.cleaned_data.get('class_assigned')
            division_assigned = form.cleaned_data.get('division_assigned')
            Teacher_Model.objects.create(
                user=user,
                class_assigned=class_assigned,
                division_assigned=division_assigned
            )

            return redirect('login')
    else:
        form = TeacherRegistrationForm()
    return render(request, 'teacher_register.html', {'form': form})


def Role(request):
    if request.method == "POST":
        role = request.POST.get("role")
        if role == "parent":
            return redirect('parent_register')  # Replace with the actual URL name for parent registration
        elif role == "teacher":
            return redirect('teacher_register')  # Replace with the actual URL name for teacher registration
    return render(request, 'role.html')

@login_required
def Teacher_Dashboard(request):
    # Access the logged-in user's first name and last name
    first_name = request.user.first_name
    last_name = request.user.last_name
    return render(request, 'teacher/teacher_dashboard.html', {'first_name': first_name, 'last_name': last_name})

@login_required
def Manage_Students(request):
    return render(request,'teacher/manage_students.html')

@login_required
def Add_student(request):
    teacher = Teacher_Model.objects.get(user=request.user)
    
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.teacher = teacher
            # These fields are already filled by the form as readonly fields
            student.save()
            return redirect('add_student')  # Replace with your success URL
    else:
        form = StudentForm(initial={
            'class_assigned': teacher.class_assigned,
            'division_assigned': teacher.division_assigned
        })

    return render(request, 'teacher/manage_students/add_student.html', {'form': form})
