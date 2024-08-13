from django.db import models
from django.contrib.auth.models import User
from datetime import date

# Create your models here.

class Teacher_Model(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    class_assigned = models.CharField(max_length=20)
    division_assigned = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.class_assigned} {self.division_assigned}"
    

class Student(models.Model):
    teacher = models.ForeignKey(Teacher_Model, on_delete=models.CASCADE)
    admission_number =models.CharField(max_length=20, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    roll_number = models.IntegerField(null=True)
    class_assigned = models.CharField(max_length=20)
    division_assigned = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.roll_number} {self.first_name} {self.last_name} - {self.class_assigned} {self.division_assigned}"
    

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    is_present = models.BooleanField(default=False)  

    def __str__(self):
        return f"{self.student} - {'Absent' if not self.is_present else 'Present'} on {self.date}"