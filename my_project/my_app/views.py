from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import *
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login
from .forms import *
# Create your views here.

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

def Teacher_Dashboard(req):
    return render(req,'teacher/teacher_dashboard.html')