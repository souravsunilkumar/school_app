from django.shortcuts import render,redirect,get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.template.loader import get_template
from .models import *
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import *
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from xhtml2pdf import pisa
from io import BytesIO
from django.core.paginator import Paginator
import logging


logger = logging.getLogger(__name__)
# Create your views here.

def BASE(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Redirect to the corresponding dashboard based on the user's group
        if request.user.groups.filter(name='administrator').exists():
            return redirect('admin_dashboard')
        elif request.user.groups.filter(name='teacher').exists():
            return redirect('teacher_dashboard')
        elif request.user.groups.filter(name='parent').exists():
            return redirect('parent_dashboard')
    else:
        # If not authenticated, redirect to the login page
        return redirect('login')

def Login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            return redirect('base')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

def Parent_Reg(req):
    return render(req,'parent_register.html')

def School_Admin_Reg(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        school_admin_first_name = request.POST['school_admin_first_name']
        school_admin_last_name = request.POST['school_admin_last_name']
        school_name = request.POST['school_name']
        address = request.POST['address']
        contact = request.POST['contact']

        if password == confirm_password:
            # Create the User
            user = User.objects.create(
                username=username,
                first_name=school_admin_first_name,
                last_name=school_admin_last_name,
                password=make_password(password)
            )
            # Add the user to the administrator group
            group = Group.objects.get(id=3)  # Assuming group id=3 corresponds to 'administrator'
            user.groups.add(group)

            # Create the School and save the username of the admin
            School.objects.create(
                school_name=school_name,
                address=address,
                contact=contact,
                school_admin_first_name=school_admin_first_name,
                school_admin_last_name=school_admin_last_name,
                school_admin_username=username  # Save the admin's username
            )

            return redirect('login')  # Redirect to login page after successful registration

        else:
            return render(request, 'school_admin_register.html', {'error': 'Passwords do not match'})

    return render(request, 'school_admin_register.html')



@login_required
def Admin_Dashboard(request):
    return render(request, 'administrator/admin_dashboard.html')

@login_required
def Employee_Reg(request):
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST, request=request)
        if form.is_valid():
            # Create User object
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['second_name'],
            )
            
            # Assign user to the appropriate group based on designation
            designation = form.cleaned_data['designation']
            group_id_mapping = {
                'Teacher': 1,
                'Warden': 5,
                'Peon': 6,
                'Security': 7,
                'Office Staff': 8,
            }
            group = Group.objects.get(id=group_id_mapping[designation])
            user.groups.add(group)

            # Create Employee object with the user linked
            employee = Employee.objects.create(
                school=form.cleaned_data['school'],
                user=user,  # Linking the user to the employee
                user_name=user.username,  # Save the username in the Employee model
                first_name=form.cleaned_data['first_name'],
                second_name=form.cleaned_data['second_name'],
                contact_number=form.cleaned_data['contact_number'],
                designation=form.cleaned_data['designation'],
            )

            # If the designation is Teacher, create an entry in the Teacher model
            if designation == 'Teacher':
                Teacher.objects.create(
                    school=form.cleaned_data['school'],
                    employee=employee,
                    user_name=user.username,  # Save the username in the Teacher model
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['second_name'],
                    contact_number=form.cleaned_data['contact_number'],
                )

            # If the designation is Warden, create an entry in the Warden model
            elif designation == 'Warden':
                Warden.objects.create(
                    school=form.cleaned_data['school'],
                    employee=employee,
                    user_name=user.username,  # Save the username in the Warden model
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['second_name'],
                    contact_number=form.cleaned_data['contact_number'],
                )

            # Add a success message
            messages.success(request, f"{designation} employee registered successfully!")

            return redirect('employee_registration')  # Redirect after successful registration
    else:
        form = EmployeeRegistrationForm(request=request)

    return render(request, 'administrator/employee_registration.html', {'form': form})


@login_required
def Assign_Class_Teacher(request):
    # Get the school of the logged-in school admin
    school = get_object_or_404(School, school_admin_username=request.user.username)

    if request.method == 'POST':
        form = AssignClassTeacherForm(request.POST, school=school)
        if form.is_valid():
            class_teacher = form.save(commit=False)
            class_teacher.school = school  # Set the school to the admin's school
            class_teacher.save()

            # Update the teacher's is_class_teacher field
            teacher = form.cleaned_data['Teacher']
            teacher.is_class_teacher = True
            teacher.save()

            # Add a success message and redirect
            messages.success(request, f"{teacher.first_name} {teacher.last_name} has been assigned as a Class Teacher.")
            return redirect('assign_class_teacher')  # Redirect after successful assignment
    else:
        form = AssignClassTeacherForm(school=school)

    return render(request, 'administrator/assign_class_teacher.html', {'form': form})


def Role(request):
    if request.method == "POST":
        role = request.POST.get("role")
        if role == "parent":
            return redirect('parent_register')  
        elif role == "teacher":
            return redirect('teacher_register')  
    return render(request, 'role.html')


@login_required
def Teacher_Dashboard(request):
    teacher = Teacher.objects.filter(employee__user=request.user).first()

    if teacher and teacher.is_class_teacher:
        assigned_class = Class_Teacher.objects.filter(Teacher=teacher).first()
        if assigned_class:
            return render(request, 'teacher/teacher_dashboard.html', {
                'first_name': teacher.first_name,
                'last_name': teacher.last_name,
                'is_class_teacher': True,
                'assigned_class': assigned_class
            })
    
    return render(request, 'teacher/teacher_dashboard.html', {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'is_class_teacher': False
    })

@login_required
def Manage_Students(request):
    # Retrieve the Employee linked to the logged-in User
    employee = get_object_or_404(Employee, user=request.user)
    
    # Retrieve the Teacher instance for this Employee
    teacher = get_object_or_404(Teacher, employee=employee)
    
    # Retrieve the Class_Teacher instance for this Teacher
    class_teacher = get_object_or_404(Class_Teacher, Teacher=teacher)
    
    # Filter students based on the class and division assigned to the class teacher
    students = Student.objects.filter(
        class_teacher=class_teacher,
        class_assigned=class_teacher.class_assigned,
        division_assigned=class_teacher.division_assigned
    )

    context = {
        'class_teacher': class_teacher,
        'students': students
    }
    return render(request, 'teacher/manage_students.html', context)

@login_required
def Add_Students(request):
    class_teacher = Class_Teacher.objects.filter(Teacher__user_name=request.user.username).first()

    if not class_teacher:
        messages.error(request, "You are not assigned as a class teacher to any class.")
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        form = AddStudentForm(request.POST, class_teacher=class_teacher, school=class_teacher.school)
        if form.is_valid():
            student = form.save(commit=False)
            student.school = class_teacher.school
            student.class_teacher = class_teacher
            student.class_assigned = class_teacher.class_assigned
            student.division_assigned = class_teacher.division_assigned
            student.save()
            messages.success(request, f"Student {student.first_name} {student.last_name} added successfully.")
            return redirect('add_students')
    else:
        form = AddStudentForm(class_teacher=class_teacher, school=class_teacher.school)

    return render(request, 'teacher/manage_students/add_students.html', {'form': form})


@login_required
def Mark_Student_Attendance(request):
    # Get the employee associated with the current user
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return render(request, 'teacher/manage_students/mark_student_attendance.html', {
            'error_message': 'No employee record found for the current user.'
        })
    
    # Get the class teacher associated with this employee
    try:
        class_teacher = Class_Teacher.objects.get(Teacher__employee=employee)
    except Class_Teacher.DoesNotExist:
        return render(request, 'teacher/manage_students/mark_student_attendance.html', {
            'error_message': 'No class teacher record found for the current employee.'
        })

    # Filter students based on the class teacher's assigned class, division, and school
    students = Student.objects.filter(
        school=class_teacher.school,  # Filter by the teacher's school
        class_assigned=class_teacher.class_assigned,
        division_assigned=class_teacher.division_assigned
    )
    
    if request.method == "POST":
        selected_date_str = request.POST.get('attendance_date', date.today().strftime('%Y-%m-%d'))
        
        try:
            selected_date = date.fromisoformat(selected_date_str)
        except ValueError:
            return render(request, 'teacher/manage_students/mark_student_attendance.html', {
                'students': students,
                'attendance_date': date.today(),
                'error_message': 'Invalid date format. Please use YYYY-MM-DD.'
            })
        
        # Process attendance
        for student in students:
            status = request.POST.get(f"status_{student.id}", None)
            if status == 'absent':
                Attendance.objects.update_or_create(
                    student=student,
                    date=selected_date,
                    defaults={'is_present': False}
                )
            else:
                Attendance.objects.filter(student=student, date=selected_date).delete()
        
        return redirect('manage_students')
    
    # Check which students are marked as absent
    selected_date_str = request.GET.get('attendance_date', date.today().strftime('%Y-%m-%d'))
    try:
        selected_date = date.fromisoformat(selected_date_str)
    except ValueError:
        selected_date = date.today()

    absent_students = Attendance.objects.filter(date=selected_date).values_list('student_id', flat=True)
    context = {
        'students': students,
        'attendance_date': selected_date_str,
        'absent_students': absent_students,
    }
    return render(request, 'teacher/manage_students/mark_student_attendance.html', context)


@login_required
def View_Attendance_Report(request):
    # Get the employee associated with the current user
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return render(request, 'teacher/manage_students/attendance_report.html', {
            'error_message': 'No employee record found for the current user.'
        })
    
    # Get the class teacher associated with this employee
    try:
        class_teacher = Class_Teacher.objects.get(Teacher__employee=employee)
    except Class_Teacher.DoesNotExist:
        return render(request, 'teacher/manage_students/attendance_report.html', {
            'error_message': 'No class teacher record found for the current employee.'
        })

    # Get the students assigned to the class teacher
    students = Student.objects.filter(
        class_assigned=class_teacher.class_assigned,
        division_assigned=class_teacher.division_assigned,
        school=class_teacher.school
    )
    
    # Get the date range from the request or default to today's date
    start_date_str = request.GET.get('start_date', date.today().strftime('%Y-%m-%d'))
    end_date_str = request.GET.get('end_date', date.today().strftime('%Y-%m-%d'))

    try:
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
    except ValueError:
        return render(request, 'teacher/manage_students/attendance_report.html', {
            'students': students,
            'error_message': 'Invalid date format. Please use YYYY-MM-DD.'
        })

    attendance_data = {}

    # Iterate over each student and gather their attendance data for the date range
    for student in students:
        student_attendance = []
        for n in range((end_date - start_date).days + 1):
            single_date = start_date + timedelta(n)
            formatted_date = single_date.strftime('%d/%m/%Y')  # Format the date as dd/mm/yyyy
            is_sunday = single_date.weekday() == 6  # Check if it's a Sunday
            
            # Skip Sundays in the attendance report
            if not is_sunday:
                attendance_record = Attendance.objects.filter(student=student, date=single_date).first()
                if attendance_record and not attendance_record.is_present:
                    status = 'Absent'
                else:
                    status = 'Present'
                student_attendance.append({'date': formatted_date, 'status': status, 'is_sunday': is_sunday})
        
        attendance_data[student] = student_attendance

    # Convert the dictionary to a list of tuples for template compatibility
    attendance_list = [(student, attendance) for student, attendance in attendance_data.items()]

    context = {
        'students': students,
        'attendance_list': attendance_list,
        'start_date': start_date_str,
        'end_date': end_date_str,
    }
    return render(request, 'teacher/manage_students/attendance_report.html', context)


@login_required
def Download_Attendance_Report_PDF(request):
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return render(request, 'teacher/manage_students/attendance_report.html', {
            'error_message': 'No employee record found for the current user.'
        })
    
    try:
        class_teacher = Class_Teacher.objects.get(Teacher__employee=employee)
    except Class_Teacher.DoesNotExist:
        return render(request, 'teacher/manage_students/attendance_report.html', {
            'error_message': 'No class teacher record found for the current employee.'
        })

    start_date_str = request.GET.get('start_date', date.today().strftime('%Y-%m-%d'))
    end_date_str = request.GET.get('end_date', date.today().strftime('%Y-%m-%d'))

    try:
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
    except ValueError:
        return render(request, 'teacher/manage_students/attendance_report.html', {
            'error_message': 'Invalid date format. Please use YYYY-MM-DD.'
        })

    dates = [start_date + timedelta(n) for n in range((end_date - start_date).days + 1)]

    students = Student.objects.filter(
        school=class_teacher.school,
        class_assigned=class_teacher.class_assigned,
        division_assigned=class_teacher.division_assigned
    )

    attendance_data = {}
    for student in students:
        student_attendance = []
        for single_date in dates:
            formatted_date = single_date.strftime('%Y-%m-%d')
            is_absent = Attendance.objects.filter(student=student, date=single_date).exists()
            student_attendance.append({
                'date': formatted_date,
                'status': 'Absent' if is_absent else 'Present'
            })
        attendance_data[student] = student_attendance

    # Debugging: Print the rendered HTML
    template_path = 'teacher/manage_students/attendance_report_pdf.html'
    context = {
        'class_teacher': class_teacher,
        'attendance_data': attendance_data,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'dates': dates,
    }
    html = get_template(template_path).render(context)
    print("Rendered HTML:")
    print(html)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="attendance_report_{start_date_str}_to_{end_date_str}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
