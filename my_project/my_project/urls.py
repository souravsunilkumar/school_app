"""
URL configuration for my_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import path, include
from my_app import views


urlpatterns = [
    path("base/", views.BASE, name="base"),
    path('admin/', admin.site.urls),
    path('', views.Login, name='login'),
    path('role', views.Role, name='role'),

    path('admin-register/', views.School_Admin_Reg, name='admin_register'),
    path('parent/register/', views.Parent_Reg, name='parent_register'),
    path('admin-dashboard/', views.Admin_Dashboard, name='admin_dashboard'),
    path('employee-registration/', views.Employee_Reg, name='employee_registration'),
    path('assign-class_teacher/', views.Assign_Class_Teacher, name='assign_class_teacher'),
    path('teacher/dashboard/', views.Teacher_Dashboard, name='teacher_dashboard'),
    path('teacher/manage-students/', views.Manage_Students, name='manage_students'),
    path('teacher/add-students/', views.Add_Students, name='add_students'),
    path('teacher/mark-students-attendance/', views.Mark_Student_Attendance, name='mark_attendance'),
    path('teacher/view-attedance-report/', views.View_Attendance_Report, name='view_attendance'),
    path('download_attendance_report_pdf/', views.Download_Attendance_Report_PDF, name='download_attendance_report_pdf'),

    path('select-date/', views.Select_Date, name='select_date'),
    path('teacher/manage-students/edit-attendance/', views.Edit_Attendance, name='edit_attendance'),

    path('add_update_marks/', views.add_update_marks, name='add_update_marks'),
    path('create_exam/', views.create_exam, name='create_exam'),
    path('add_subjects/<int:exam_id>/', views.add_subjects, name='add_subjects'),
    path('enter_marks/<int:exam_id>/', views.enter_marks, name='enter_marks'),

    path('select_existing_exam/', views.select_existing_exam, name='select_existing_exam'),
    path('edit_marks/<int:exam_id>/', views.edit_marks, name='edit_marks'),

    path('view_student_marks/', views.view_student_marks, name='view_student_marks'),

    
]
