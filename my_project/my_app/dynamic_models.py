# from django.db import models

# def create_dynamic_model(table_name):
#     class Meta:
#         db_table = table_name
    
#     attrs = {
#         '__module__': __name__,
#         'Meta': Meta,
#         'id': models.AutoField(primary_key=True),
#         'school': models.ForeignKey('School', on_delete=models.CASCADE),
#         'name': models.CharField(max_length=100, blank=True),
#         'class_assigned': models.CharField(max_length=50, blank=True),
#         'division_assigned': models.CharField(max_length=50, blank=True),
#         'admission_number': models.CharField(max_length=50, blank=True),
#         'roll_number': models.IntegerField(blank=True, null=True),
#         'teacher': models.ForeignKey('Teacher', on_delete=models.CASCADE, blank=True, null=True),
#         'student': models.ForeignKey('Student', on_delete=models.CASCADE, blank=True, null=True),
#         'is_present': models.BooleanField(default=False),
#         'date': models.DateField(blank=True, null=True),
#         'first_name': models.CharField(max_length=100, blank=True),
#         'last_name': models.CharField(max_length=100, blank=True),
#         'created_at': models.DateTimeField(auto_now_add=True),
#     }
    
#     return type(table_name.capitalize(), (models.Model,), attrs)
