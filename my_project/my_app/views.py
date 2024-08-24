from django.shortcuts import render,redirect,get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from django.template.loader import get_template
from .models import *
from django.http import JsonResponse
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
from django.core.mail import send_mail


logger = logging.getLogger(__name__)
# Create your views here.

@login_required
def BASE(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Redirect to the corresponding dashboard based on the user's group
        if request.user.groups.filter(name='main administrator').exists():
            return redirect('admin_dashboard')
        elif request.user.groups.filter(name='sub_admins').exists():
            return redirect('sub_admin_dashboard')
        elif request.user.groups.filter(name='teacher').exists():
            return redirect('teacher_dashboard')
        elif request.user.groups.filter(name='parent').exists():
            return redirect('parent_dashboard')
        else:
            # If the user does not belong to any known group, return a 403 Forbidden response
            return HttpResponse('Access denied', status=403)
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

            # Create the School
            school = School.objects.create(
                school_name=school_name,
                address=address,
                contact=contact,
                school_admin_first_name=school_admin_first_name,
                school_admin_last_name=school_admin_last_name,
                school_admin_username=username  # Save the admin's username
            )

            # Create the Admin instance
            Admin.objects.create(
                school=school,
                first_name=school_admin_first_name,
                second_name=school_admin_last_name,
                user=user,
                username=username
            )

            return redirect('login')  # Redirect to login page after successful registration

        else:
            return render(request, 'school_admin_register.html', {'error': 'Passwords do not match'})

    return render(request, 'school_admin_register.html')



@login_required
def Admin_Dashboard(request):
    return render(request, 'administrator/admin_dashboard.html')

@login_required
def Sub_Admin_Reg(request):
    school = get_object_or_404(School, school_admin_username=request.user.username)

    if request.method == 'POST':
        form = SubAdminRegistrationForm(request.POST, school=school)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']

            if password == confirm_password:
                # Create the User
                user = User.objects.create(
                    username=username,
                    first_name=form.cleaned_data['sub_admin_first_name'],
                    last_name=form.cleaned_data['sub_admin_last_name'],
                    password=make_password(password)
                )
                
                # Add the user to the sub admin group
                group = Group.objects.get(id=9)  # Assuming group id=9 corresponds to 'sub admin'
                user.groups.add(group)
                
                # Create the Admin instance
                Admin.objects.create(
                    school=form.cleaned_data['sub_admin_school'],
                    first_name=form.cleaned_data['sub_admin_first_name'],
                    second_name=form.cleaned_data['sub_admin_last_name'],
                    user=user,
                    username=username,
                    contact_number=form.cleaned_data['contact_number']  # Save contact number
                )

                # Show success message
                messages.success(request, f"Sub Admin {user.get_full_name()} registered successfully!")
                return redirect('sub_admin_register')  # Redirect after successful registration

            else:
                return render(request, 'administrator/sub_admin_register.html', {'form': form, 'error': 'Passwords do not match'})
        else:
            return render(request, 'administrator/sub_admin_register.html', {'form': form})
    else:
        form = SubAdminRegistrationForm(school=school)
    
    return render(request, 'administrator/sub_admin_register.html', {'form': form})

def Sub_Admin_Dashboard(request):
    return render(request,'sub_admin/sub_admin_dashboard.html')


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
                    user=user,  # Link the user to the Teacher model
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
                    user=user,  # Link the user to the Warden model
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
def Employee_Reg_Sub_Admin(request):
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

            # Get the school associated with the logged-in sub-admin or main admin
            school = form.cleaned_data['school']

            # Create Employee object with the user linked
            employee = Employee.objects.create(
                school=school,
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
                    school=school,
                    employee=employee,
                    user=user,  # Link the user to the Teacher model
                    user_name=user.username,  # Save the username in the Teacher model
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['second_name'],
                    contact_number=form.cleaned_data['contact_number'],
                )

            # If the designation is Warden, create an entry in the Warden model
            elif designation == 'Warden':
                Warden.objects.create(
                    school=school,
                    employee=employee,
                    user=user,  # Link the user to the Warden model
                    user_name=user.username,  # Save the username in the Warden model
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['second_name'],
                    contact_number=form.cleaned_data['contact_number'],
                )

            # Add a success message
            messages.success(request, f"{designation} employee registered successfully!")

            return redirect('employee_registration_sub_admin')  # Redirect after successful registration
    else:
        form = EmployeeRegistrationForm(request=request)

    return render(request, 'sub_admin/employee_registration.html', {'form': form})


@login_required
def Assign_Class_Teacher(request):
    # Get the school of the logged-in user (admin or sub-admin)
    if request.user.groups.filter(name='main administrator').exists():
        # Main admin
        school = get_object_or_404(School, school_admin_username=request.user.username)
    elif request.user.groups.filter(name='sub_admins').exists():
        # Sub-admin
        admin = get_object_or_404(Admin, user=request.user)
        school = admin.school
    else:
        # Handle case where user is neither admin nor sub-admin
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')  # Redirect to a home page or other appropriate page

    if request.method == 'POST':
        form = AssignClassTeacherForm(request.POST, school=school)
        if form.is_valid():
            class_teacher = form.save(commit=False)
            class_teacher.school = school  # Set the school to the admin's school

            # Get the teacher instance and assign its user to class_teacher
            teacher = form.cleaned_data['Teacher']
            class_teacher.user = teacher.user  # Correctly set the User instance

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

@login_required
def view_all_sub_admins(request):
    if request.user.groups.filter(name='main administrator').exists():
        # Get the school of the logged-in main administrator
        school = get_object_or_404(School, school_admin_username=request.user.username)
        sub_admins = Admin.objects.filter(school=school, user__groups__name='sub_admins')
    else:
        # Handle unauthorized access
        messages.error(request, "You do not have permission to view this page.")
        return redirect('admin_dashboard')  

    return render(request, 'administrator/admin_dashboard/view_all_sub_admins.html', {'sub_admins': sub_admins})

@login_required
def delete_sub_admin(request, id):
    if request.user.groups.filter(name='main administrator').exists():
        sub_admin = get_object_or_404(Admin, id=id)

        admin_school = get_object_or_404(School, school_admin_username=request.user.username)
        if sub_admin.school == admin_school:
            sub_admin.user.delete() 
            messages.success(request, f"Sub-admin {sub_admin.username} has been deleted.")
        else:
            messages.error(request, "You do not have permission to delete this sub-admin.")
    else:
        messages.error(request, "You do not have permission to perform this action.")

    
    return redirect('view_all_sub_admins')

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
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return render(request, 'teacher/manage_students/mark_student_attendance.html', {
            'error_message': 'No employee record found for the current user.'
        })
    
    try:
        class_teacher = Class_Teacher.objects.get(Teacher__employee=employee)
    except Class_Teacher.DoesNotExist:
        return render(request, 'teacher/manage_students/mark_student_attendance.html', {
            'error_message': 'No class teacher record found for the current employee.'
        })

    students = Student.objects.filter(
        school=class_teacher.school,
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

        for student in students:
            status = request.POST.get(f"status_{student.id}", None)
            if status == 'absent':
                Attendance.objects.update_or_create(
                    student=student,
                    date=selected_date,
                    defaults={'is_present': False}
                )
                # Send email to parents if the student is marked absent
                if student.parents_email:
                    send_mail(
                        subject='Student Attendance Alert',
                        message=f'Dear Parent,\n\nYour student {student.first_name} {student.last_name} is marked absent today ({selected_date}).\n\nRegards,\nSchool Management',
                        from_email='souravsunilkumar5@gmail.com',
                        recipient_list=[student.parents_email],
                        fail_silently=False,
                    )
            else:
                Attendance.objects.filter(student=student, date=selected_date).delete()
        
        return redirect('manage_students')
    
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

    # Grouping data by month
    monthly_attendance_data = {}
    for student in students:
        student_attendance = []
        for single_date in dates:
            formatted_date = single_date.strftime('%Y-%m-%d')
            is_absent = Attendance.objects.filter(student=student, date=single_date).exists()
            student_attendance.append({
                'date': formatted_date,
                'status': 'Absent' if is_absent else 'Present'
            })
        
        # Group attendance by month
        for record in student_attendance:
            month_year = single_date.strftime('%B %Y')
            if month_year not in monthly_attendance_data:
                monthly_attendance_data[month_year] = {}
            if student not in monthly_attendance_data[month_year]:
                monthly_attendance_data[month_year][student] = []
            monthly_attendance_data[month_year][student].append(record)

    template_path = 'teacher/manage_students/attendance_report_pdf.html'
    context = {
        'class_teacher': class_teacher,
        'monthly_attendance_data': monthly_attendance_data,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'dates': dates,
    }
    html = get_template(template_path).render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="attendance_report_{start_date_str}_to_{end_date_str}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')

    return response


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
    # Use request.user.username to get the Class_Teacher instance
    teacher = get_object_or_404(Class_Teacher, user_name=request.user.username)
    
    # Filter students by the teacher's assigned class, division, and school
    students = Student.objects.filter(
        school=teacher.school,  # Ensure the students are from the teacher's school
        class_assigned=teacher.class_assigned,
        division_assigned=teacher.division_assigned
    )
    
    selected_date_str = request.GET.get('attendance_date', date.today().strftime('%Y-%m-%d'))

    try:
        selected_date = date.fromisoformat(selected_date_str)
    except ValueError:
        return render(request, 'teacher/manage_students/edit_attendance.html', {
            'students': students,
            'attendance_date': date.today(),
            'error_message': 'Invalid date format. Please use YYYY-MM-DD.'
        })
    
    is_today = (selected_date == date.today())
    
    if request.method == "POST":
        for student in students:
            is_absent = request.POST.get(f"absent_{student.id}", False) == 'on'
            existing_attendance = Attendance.objects.filter(student=student, date=selected_date).first()
            
            if is_absent:
                if not existing_attendance or existing_attendance.is_present:  # Was previously present
                    Attendance.objects.update_or_create(
                        student=student,
                        date=selected_date,
                        defaults={'is_present': False}
                    )
                    # Send email if the student is marked absent
                    message = (
                        f'Dear Parent,\n\nYour student {student.first_name} {student.last_name} is marked absent today ({selected_date}).\n\nRegards,\nSchool Management'
                        if is_today else
                        f'Dear Parent,\n\nYour student {student.first_name} {student.last_name} was marked absent on {selected_date}.\n\nRegards,\nSchool Management'
                    )
                    send_mail(
                        subject='Student Attendance Alert',
                        message=message,
                        from_email='souravsunilkumar5@gmail.com',
                        recipient_list=[student.parents_email],
                        fail_silently=False,
                    )
            else:
                if existing_attendance and not existing_attendance.is_present:  # Was previously absent
                    # Send email if the absent student is now marked present (late)
                    message = (
                        f'Dear Parent,\n\nYour student {student.first_name} {student.last_name} was marked present today ({selected_date}).\n\nRegards,\nSchool Management'
                        if is_today else
                        f'Dear Parent,\n\nYour student {student.first_name} {student.last_name} was marked present on {selected_date}.\n\nRegards,\nSchool Management'
                    )
                    send_mail(
                        subject='Student Attendance Alert',
                        message=message,
                        from_email='souravsunilkumar5@gmail.com',
                        recipient_list=[student.parents_email],
                        fail_silently=False,
                    )
                    existing_attendance.delete()
        
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
def add_update_marks(request):
    teacher = get_object_or_404(Teacher, user_name=request.user.username)
    if request.method == 'POST':
        if 'create_exam' in request.POST:
            return redirect('create_exam')
        elif 'use_existing_exam' in request.POST:
            return redirect('select_existing_exam')
    return render(request, 'teacher/manage_students/add_update_marks.html')

@login_required
def create_exam(request):
    if request.method == 'POST':
        exam_form = ExamForm(request.POST)
        if exam_form.is_valid():
            exam = exam_form.save(commit=False)
            teacher = Teacher.objects.get(employee__user=request.user)
            class_teacher = Class_Teacher.objects.filter(Teacher=teacher).first()

            if class_teacher:
                exam.teacher = teacher
                exam.school = teacher.school
                exam.class_assigned = class_teacher.class_assigned
                exam.division_assigned = class_teacher.division_assigned
                exam.user_name = request.user.username  # Save the logged-in teacher's username
                exam.save()
                return redirect('add_subjects', exam_id=exam.id)
            else:
                # Handle case where class_teacher is not found
                return redirect('error_page')  # Replace with your actual error handling
    else:
        exam_form = ExamForm()

    return render(request, 'teacher/manage_students/create_exam.html', {'exam_form': exam_form})




@login_required
def add_subjects(request, exam_id):
    exam = Exam.objects.get(id=exam_id)
    from_edit_marks = request.GET.get('from_edit_marks', 'false').lower() == 'true'

    if request.method == 'POST':
        subject_form = SubjectForm(request.POST)
        if subject_form.is_valid():
            subject = subject_form.save(commit=False)
            teacher = Teacher.objects.get(employee__user=request.user)
            class_teacher = Class_Teacher.objects.filter(Teacher=teacher).first()

            if class_teacher:
                subject.exam = exam
                subject.teacher = teacher
                subject.school = exam.school
                subject.class_assigned = class_teacher.class_assigned
                subject.division_assigned = class_teacher.division_assigned
                subject.user_name = request.user.username
                subject.save()

                messages.success(request, f"Subject '{subject.subject_name}' added successfully.")
                if from_edit_marks:
                    return redirect('edit_marks', exam_id=exam.id)
                else:
                    return redirect('add_subjects', exam_id=exam.id)
    else:
        subject_form = SubjectForm()

    return render(request, 'teacher/manage_students/add_subjects.html', {
        'subject_form': subject_form,
        'exam': exam,
        'from_edit_marks': from_edit_marks,
    })

@login_required
def enter_marks(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    teacher = exam.teacher
    students = Student.objects.filter(
        class_assigned=exam.class_assigned,
        division_assigned=exam.division_assigned,
        school=teacher.school
    )
    subjects = Subject.objects.filter(exam=exam)
    
    # Prepare a list to store marks information
    marks_info = []
    marks = Marks.objects.filter(exam=exam)
    for student in students:
        student_marks = {}
        for subject in subjects:
            mark = marks.filter(student=student, subject=subject).first()
            student_marks[subject.id] = mark
        marks_info.append({
            'student': student,
            'marks': student_marks
        })
    
    if request.method == 'POST':
        # Handle "out of" marks update for each subject
        for subject in subjects:
            out_of = request.POST.get(f"set_out_of_{subject.id}", "")
            if out_of:
                # Update the "out of" marks for all students for this subject
                Marks.objects.filter(
                    exam=exam,
                    subject=subject
                ).update(out_of=out_of)
        
        # Handle individual student marks
        for student in students:
            for subject in subjects:
                marks_obtained = request.POST.get(f"marks_obtained_{student.id}_{subject.id}", "")
                out_of = request.POST.get(f"out_of_{student.id}_{subject.id}", "")
                Marks.objects.update_or_create(
                    school=teacher.school,
                    teacher=teacher,
                    class_assigned=exam.class_assigned,
                    division_assigned=exam.division_assigned,
                    exam=exam,
                    student=student,
                    subject=subject,
                    defaults={
                        'marks_obtained': marks_obtained if marks_obtained else '',
                        'out_of': out_of if out_of else None,
                    }
                )
        messages.success(request, 'Marks of students added successfully.')
        return redirect('enter_marks', exam_id=exam.id)

    return render(request, 'teacher/manage_students/enter_marks.html', {
        'exam': exam,
        'students': students,
        'subjects': subjects,
        'marks_info': marks_info,
    })

@login_required
def select_existing_exam(request):
    # Get the User associated with the request
    user = request.user

    # Retrieve the Employee linked to this user
    employee = get_object_or_404(Employee, user=user)

    # Retrieve the Teacher linked to this Employee
    teacher = get_object_or_404(Teacher, employee=employee)
    
    # Retrieve the Class_Teacher associated with this Teacher
    class_teacher = get_object_or_404(Class_Teacher, Teacher=teacher)
    
    # Filter exams based on the Teacher's associated School, Class, and Division
    exams = Exam.objects.filter(
        school=teacher.school, 
        class_assigned=class_teacher.class_assigned, 
        division_assigned=class_teacher.division_assigned
    )
    
    if request.method == 'POST':
        exam_id = request.POST.get('exam')
        return redirect('edit_marks', exam_id=exam_id)
    
    return render(request, 'teacher/manage_students/select_existing_exam.html', {
        'exams': exams
    })


@login_required
def edit_marks(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    teacher = exam.teacher
    students = Student.objects.filter(
        class_assigned=exam.class_assigned,
        division_assigned=exam.division_assigned,
        school=teacher.school
    )
    subjects = Subject.objects.filter(exam=exam)
    
    if request.method == 'POST':
        # Handle "out of" marks update for each subject
        for subject in subjects:
            out_of = request.POST.get(f"set_out_of_{subject.id}", "")
            if out_of:
                # Update the "out of" marks for all students for this subject
                Marks.objects.filter(
                    exam=exam,
                    subject=subject
                ).update(out_of=out_of)
        
        # Handle individual student marks
        for student in students:
            for subject in subjects:
                marks_obtained = request.POST.get(f"marks_obtained_{student.id}_{subject.id}", "")
                out_of = request.POST.get(f"out_of_{student.id}_{subject.id}", "")
                Marks.objects.update_or_create(
                    school=teacher.school,
                    teacher=teacher,
                    class_assigned=exam.class_assigned,
                    division_assigned=exam.division_assigned,
                    exam=exam,
                    student=student,
                    subject=subject,
                    defaults={
                        'marks_obtained': marks_obtained if marks_obtained else '',
                        'out_of': out_of if out_of else None,
                    }
                )
        messages.success(request, 'Marks updated successfully.')
        return redirect('edit_marks', exam_id=exam.id)

    marks_dict = {}
    marks = Marks.objects.filter(exam=exam)
    for mark in marks:
        if mark.student.id not in marks_dict:
            marks_dict[mark.student.id] = {}
        marks_dict[mark.student.id][mark.subject.id] = mark

    return render(request, 'teacher/manage_students/edit_marks.html', {
        'exam': exam,
        'students': students,
        'subjects': subjects,
        'marks_dict': marks_dict,
    })

@login_required
def view_student_marks(request):
    # Retrieve the logged-in user's Employee instance
    employee = get_object_or_404(Employee, user=request.user)
    
    # Retrieve the Teacher instance linked to the Employee
    teacher = get_object_or_404(Teacher, employee=employee)
    
    # Retrieve the Class_Teacher instance linked to the Teacher
    class_teacher = get_object_or_404(Class_Teacher, Teacher=teacher)
    
    # Get exams related to the class and school of the teacher
    exams = Exam.objects.filter(
        class_assigned=class_teacher.class_assigned,
        division_assigned=class_teacher.division_assigned,
        school=class_teacher.school
    )
    
    if request.method == 'POST':
        exam_id = request.POST.get('exam_id')
        selected_exam = get_object_or_404(Exam, id=exam_id)
        
        # Fetch students related to the selected exam
        students = Student.objects.filter(
            class_assigned=selected_exam.class_assigned,
            division_assigned=selected_exam.division_assigned,
            school=class_teacher.school
        )
        
        # Fetch subjects related to the selected exam
        subjects = Subject.objects.filter(exam=selected_exam)
        
        # Fetch marks for the selected exam
        marks_dict = {}
        marks = Marks.objects.filter(exam=selected_exam)
        for mark in marks:
            if mark.student.id not in marks_dict:
                marks_dict[mark.student.id] = {}
            marks_dict[mark.student.id][mark.subject.id] = mark
        
        return render(request, 'teacher/manage_students/view_marks_list.html', {
            'exam': selected_exam,
            'students': students,
            'subjects': subjects,
            'marks_dict': marks_dict,
        })
    
    return render(request, 'teacher/manage_students/select_exam_for_marks.html', {
        'exams': exams,
    })