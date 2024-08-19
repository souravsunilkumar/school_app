from django.shortcuts import render,redirect,get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
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
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['second_name'],
                    contact_number=form.cleaned_data['contact_number'],
                )

            # If the designation is Warden, create an entry in the Warden model
            elif designation == 'Warden':
                Warden.objects.create(
                    school=form.cleaned_data['school'],
                    employee=employee,
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
            teacher = form.cleaned_data['Teacher']
            class_assigned = form.cleaned_data['class_assigned']
            division_assigned = form.cleaned_data['division_assigned']

            # Check if the teacher is already a class teacher
            if Class_Teacher.objects.filter(Teacher=teacher).exists() or teacher.is_class_teacher:
                form.add_error('Teacher', 'This teacher is already a class teacher.')
            else:
                # Check if another teacher is already assigned to this class and division in the same school
                if Class_Teacher.objects.filter(school=school, class_assigned=class_assigned, division_assigned=division_assigned).exists():
                    form.add_error(None, 'A teacher is already assigned to this class and division in this school.')
                else:
                    # Save the Class_Teacher object
                    class_teacher = form.save(commit=False)
                    class_teacher.school = school  # Set the school to the admin's school
                    class_teacher.user = request.user  # Set the user to the logged-in user
                    class_teacher.save()

                    # Update the teacher's is_class_teacher field
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
    first_name = request.user.first_name
    last_name = request.user.last_name
    return render(request, 'teacher/teacher_dashboard.html', {'first_name': first_name, 'last_name': last_name})

def Parent_Dashboard(request):
    return render(request,'parent/parent_dashboard.html')

@login_required
def Manage_Students(request):
    teacher = Class_Teacher.objects.get(user=request.user)
    students = Student.objects.filter(class_assigned=teacher.class_assigned, division_assigned=teacher.division_assigned)
    context={
        'teacher':teacher,
        'students':students
    }

    return render(request, 'teacher/manage_students.html', context)



@login_required
def Mark_Student_Attendance(request):
    teacher = Class_Teacher.objects.get(user=request.user)
    students = Student.objects.filter(class_assigned=teacher.class_assigned, division_assigned=teacher.division_assigned)
    
    selected_date_str = request.POST.get('attendance_date', date.today().strftime('%Y-%m-%d'))
    
    try:
        selected_date = date.fromisoformat(selected_date_str)
    except ValueError:
        return render(request, 'teacher/manage_students/mark_student_attendance.html', {
            'students': students,
            'attendance_date': date.today(),
            'error_message': 'Invalid date format. Please use YYYY-MM-DD.'
        })

    if request.method == "POST":
        for student in students:
            is_absent = request.POST.get(f"absent_{student.id}", False) == 'on'
            if is_absent:
                Attendance.objects.update_or_create(
                    student=student,
                    date=selected_date,
                    defaults={'is_present': False}
                )
            else:
                Attendance.objects.filter(student=student, date=selected_date).delete()
        return redirect('manage_students')
    
    # Check which students are marked as absent
    absent_students = Attendance.objects.filter(date=selected_date).values_list('student_id', flat=True)
    context = {
        'students': students,
        'attendance_date': selected_date_str,
        'absent_students': absent_students,
    }
    return render(request, 'teacher/manage_students/mark_student_attendance.html', context)


@login_required
def Attendance_Report(request):
    teacher = Class_Teacher.objects.get(user=request.user)
    students = Student.objects.filter(class_assigned=teacher.class_assigned, division_assigned=teacher.division_assigned)
    
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

    for student in students:
        student_attendance = []
        for n in range((end_date - start_date).days + 1):
            single_date = start_date + timedelta(n)
            formatted_date = single_date.strftime('%d/%m/%Y')  # Format the date as dd/mm/yyyy
            is_sunday = single_date.weekday() == 6  # Check if it's a Sunday
            
            # Skip Sundays in the attendance report
            if not is_sunday:
                attendance_record = Attendance.objects.filter(student=student, date=single_date).first()
                if attendance_record:
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
def Select_Date(request):
    if request.method == 'POST':
        selected_date = request.POST.get('attendance_date')
        if selected_date:
            return redirect(f'/teacher/manage-students/edit-attendance/?attendance_date={selected_date}')
    
    context = {
        'today': date.today(),
    }
    return render(request, 'teacher/manage_students/select_date.html', context)



@login_required
def Edit_Attendance(request):
    teacher = get_object_or_404(Class_Teacher, user=request.user)
    students = Student.objects.filter(class_assigned=teacher.class_assigned, division_assigned=teacher.division_assigned)
    
    selected_date_str = request.GET.get('attendance_date', date.today().strftime('%Y-%m-%d'))

    try:
        selected_date = date.fromisoformat(selected_date_str)
    except ValueError:
        return render(request, 'teacher/manage_students/edit_attendance.html', {
            'students': students,
            'attendance_date': date.today(),
            'error_message': 'Invalid date format. Please use YYYY-MM-DD.'
        })
    
    if request.method == "POST":
        for student in students:
            is_absent = request.POST.get(f"absent_{student.id}", False) == 'on'
            if is_absent:
                Attendance.objects.update_or_create(
                    student=student,
                    date=selected_date,
                    defaults={'is_present': False}
                )
            else:
                Attendance.objects.filter(student=student, date=selected_date).delete()
        return redirect('manage_students')
    
    # Pre-select absent students based on the selected date
    absent_students = Attendance.objects.filter(date=selected_date, is_present=False).values_list('student_id', flat=True)
    
    context = {
        'students': students,
        'attendance_date': selected_date_str,
        'absent_students': absent_students,
    }
    return render(request, 'teacher/manage_students/edit_attendance.html', context)


@login_required
def Download_Attendance_Report(request):
    teacher = Class_Teacher.objects.get(user=request.user)
    students = Student.objects.filter(class_assigned=teacher.class_assigned, division_assigned=teacher.division_assigned)
    
    start_date_str = request.GET.get('start_date', date.today().strftime('%Y-%m-%d'))
    end_date_str = request.GET.get('end_date', date.today().strftime('%Y-%m-%d'))

    try:
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
    except ValueError:
        return HttpResponse("Invalid date format. Please use YYYY-MM-DD.")
    
    attendance_data = {}

    for student in students:
        student_attendance = []
        for n in range((end_date - start_date).days + 1):
            single_date = start_date + timedelta(n)
            formatted_date = single_date.strftime('%d/%m/%Y')
            attendance_record = Attendance.objects.filter(student=student, date=single_date).first()
            if attendance_record:
                student_attendance.append({'date': formatted_date, 'status': 'Absent'})
            else:
                student_attendance.append({'date': formatted_date, 'status': 'Present'})
        
        attendance_data[student] = student_attendance

    # Convert the dictionary to a list of tuples for template compatibility
    attendance_list = [(student, attendance) for student, attendance in attendance_data.items()]

    # Paginate data
    paginator = Paginator(attendance_list, 10)  # 10 items per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'students': students,
        'attendance_list': page_obj,
        'start_date': start_date_str,
        'end_date': end_date_str,
    }
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.pdf"'
    
    # Render the HTML template
    html = render_to_string('teacher/manage_students/attendance_report_pdf.html', context)
    
    # Generate PDF
    pisa_status = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=response)
    
    if pisa_status.err:
        return HttpResponse('Error generating PDF')

    return response