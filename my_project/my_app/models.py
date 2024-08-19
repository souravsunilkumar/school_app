from django.db import models
from django.contrib.auth.models import User
from datetime import date

# Create your models here.

class School(models.Model):
    id = models.AutoField(primary_key=True)  # Explicit id field
    school_name = models.CharField(max_length=255)
    address = models.TextField()
    contact = models.CharField(max_length=15)
    school_admin_first_name = models.CharField(max_length=255, null=True)
    school_admin_last_name = models.CharField(max_length=255, null=True)
    school_admin_username = models.CharField(max_length=255, null=True)  # New field

    def __str__(self):
        return self.school_name

class Employee(models.Model):
    TEACHER = 'Teacher'
    PEON = 'Peon'
    SECURITY = 'Security'
    WARDEN = 'Warden'
    OFFICE_STAFF = 'Office Staff'

    DESIGNATION_CHOICES = [
        (TEACHER, 'Teacher'),
        (PEON, 'Peon'),
        (SECURITY, 'Security'),
        (WARDEN, 'Warden'),
        (OFFICE_STAFF, 'Office Staff'),
    ]

    id = models.AutoField(primary_key=True)  # Explicit id field
    school = models.ForeignKey(School, on_delete=models.CASCADE)  # Foreign key to School model
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Foreign key to User model
    first_name = models.CharField(max_length=255)
    second_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    designation = models.CharField(
        max_length=20,
        choices=DESIGNATION_CHOICES,
        default=TEACHER,
    )

    def __str__(self):
        return f"{self.first_name} {self.second_name} - {self.designation} - {self.school}"
    

class Teacher(models.Model):
    id = models.AutoField(primary_key=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15, null=True)
    is_class_teacher = models.BooleanField(default=False)  # New field

    def __str__(self):
        return f"{self.first_name} {self.last_name} - Teacher - {self.school}"
    

class Class_Teacher(models.Model):
    id = models.AutoField(primary_key=True)
    Teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    class_assigned = models.CharField(max_length=20)
    division_assigned = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.class_assigned} {self.division_assigned} - {self.school}"
    
class Warden(models.Model):
    id = models.AutoField(primary_key=True)  # Explicit id field
    school = models.ForeignKey(School, on_delete=models.CASCADE)  # Link to School model
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)  # Link to Employee model
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15,null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - Warden - {self.school}"
    


class Student(models.Model):
    id = models.AutoField(primary_key=True)  # Explicit id field
    school = models.ForeignKey(School, on_delete=models.CASCADE)  # Link to School
    class_teacher = models.ForeignKey(Class_Teacher, on_delete=models.CASCADE,null=True)  # Link to Class_Teacher
    warden = models.ForeignKey(Warden, on_delete=models.SET_NULL, null=True, blank=True)  
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    admission_number = models.CharField(max_length=20, null=True)
    roll_number = models.IntegerField(null=True)
    parents_number = models.CharField(max_length=15,null=True)
    class_assigned = models.CharField(max_length=20)
    division_assigned = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.roll_number} {self.first_name} {self.last_name} - {self.class_assigned} {self.division_assigned}"
    

class Attendance(models.Model):
    id = models.AutoField(primary_key=True)  # Explicit id field
    student = models.ForeignKey(Student, on_delete=models.CASCADE,null=True)
    date = models.DateField(default=date.today)
    is_present = models.BooleanField(default=False)  

    def __str__(self):
        return f"{self.student} - {'Absent' if not self.is_present else 'Present'} on {self.date}"
    


class Hostel_Attendance(models.Model):
    id = models.AutoField(primary_key=True)  # Explicit id field
    student = models.ForeignKey(Student, on_delete=models.CASCADE,null=True)
    class_assigned = models.CharField(max_length=20)
    division_assigned = models.CharField(max_length=10)
    date = models.DateField(default=date.today)
    is_present = models.BooleanField(default=False)  

    def __str__(self):
        return f"{self.student} - {'Absent' if not self.is_present else 'Present'} on {self.date}"