from django.shortcuts import render,redirect,get_object_or_404
from django.template.loader import render_to_string
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

def BASE(req):
    return render(req,'base.html')

def Login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            teacher_group = Group.objects.get(id=1)
            if teacher_group in user.groups.all():
                return redirect('teacher_dashboard')
            else:
                return redirect('login')  # Redirect to a default dashboard
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

def Parent_Reg(req):
    return render(req,'parent_register.html')


def Teacher_Reg(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():

            user = form.save()
            

            teacher_group = Group.objects.get(name='teacher')
            user.groups.add(teacher_group)

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
            return redirect('parent_register')  
        elif role == "teacher":
            return redirect('teacher_register')  
    return render(request, 'role.html')

@login_required
def Teacher_Dashboard(request):

    first_name = request.user.first_name
    last_name = request.user.last_name
    return render(request, 'teacher/teacher_dashboard.html', {'first_name': first_name, 'last_name': last_name})

@login_required
def Manage_Students(request):
    teacher = Teacher_Model.objects.get(user=request.user)
    students = Student.objects.filter(class_assigned=teacher.class_assigned, division_assigned=teacher.division_assigned)
    context={
        'teacher':teacher,
        'students':students
    }

    return render(request, 'teacher/manage_students.html', context)


@login_required
def Add_student(request):
    teacher = Teacher_Model.objects.get(user=request.user)
    
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.teacher = teacher
            student.save()
            messages.success(request, 'Student added successfully!')
            return redirect('add_student')  
    else:
        form = StudentForm(initial={
            'class_assigned': teacher.class_assigned,
            'division_assigned': teacher.division_assigned
        })

    return render(request, 'teacher/manage_students/add_student.html', {'form': form})


@login_required
def Mark_Student_Attendance(request):
    teacher = Teacher_Model.objects.get(user=request.user)
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
    teacher = Teacher_Model.objects.get(user=request.user)
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
    teacher = get_object_or_404(Teacher_Model, user=request.user)
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
    teacher = Teacher_Model.objects.get(user=request.user)
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