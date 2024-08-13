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
    path('parent/register/', views.Parent_Reg, name='parent_register'),
    path('teacher/register/', views.Teacher_Reg, name='teacher_register'),
    path('teacher/dashboard/', views.Teacher_Dashboard, name='teacher_dashboard'),
    path('teacher/manage-students/', views.Manage_Students, name='manage_students'),
    path('teacher/manage-students/add-student', views.Add_student, name='add_student'),
    path('teacher/manage-students/mark-attendance', views.Mark_Student_Attendance, name='mark_attendance'),
    path('teacher/manage-students/attendance-report', views.Attendance_Report, name='attendance_report'),
    path('teacher/manage-students/select-date', views.Select_Date, name='select_date'),
    path('teacher/manage-students/edit-attendance/', views.Edit_Attendance, name='edit_attendance'),
    path('teacher/manage-students/download-attendance-report/', views.Download_Attendance_Report, name='download_attendance_report'),


]
