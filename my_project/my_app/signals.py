# from django.db import connection
# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver
# from django.contrib import admin
# from django.apps import apps
# from .models import School
# from .dynamic_models import create_dynamic_model

# def create_school_tables(school_name):
#     # Replacing spaces and dashes in table names
#     school_name = school_name.replace(" ", "_").replace("-", "_")
    
#     with connection.cursor() as cursor:
#         cursor.execute(f"""
#             CREATE TABLE IF NOT EXISTS `{school_name}_Teacher` (
#                 id INT AUTO_INCREMENT PRIMARY KEY,
#                 school_id INT NOT NULL,
#                 name VARCHAR(100) NOT NULL,
#                 class_assigned VARCHAR(50),
#                 division_assigned VARCHAR(50),
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                 FOREIGN KEY (school_id) REFERENCES school(id)
#             );
#         """)
#         cursor.execute(f"""
#             CREATE TABLE IF NOT EXISTS `{school_name}_Student` (
#                 id INT AUTO_INCREMENT PRIMARY KEY,
#                 school_id INT NOT NULL,
#                 admission_number VARCHAR(50) NOT NULL,
#                 teacher_id INT NOT NULL,
#                 class_assigned VARCHAR(50),
#                 division_assigned VARCHAR(50),
#                 roll_number INT NOT NULL,
#                 first_name VARCHAR(100) NOT NULL,
#                 last_name VARCHAR(100) NOT NULL,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                 FOREIGN KEY (school_id) REFERENCES school(id),
#                 FOREIGN KEY (teacher_id) REFERENCES `{school_name}_Teacher`(id)
#             );
#         """)
#         cursor.execute(f"""
#             CREATE TABLE IF NOT EXISTS `{school_name}_Parent` (
#                 id INT AUTO_INCREMENT PRIMARY KEY,
#                 school_id INT NOT NULL,
#                 class_assigned VARCHAR(50),
#                 division_assigned VARCHAR(50),
#                 admission_number VARCHAR(50),
#                 roll_number INT,
#                 student_name VARCHAR(200),
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                 FOREIGN KEY (school_id) REFERENCES school(id),
#                 FOREIGN KEY (student_name) REFERENCES `{school_name}_Student`(id)
#             );
#         """)
#         cursor.execute(f"""
#             CREATE TABLE IF NOT EXISTS `{school_name}_Attendance` (
#                 id INT AUTO_INCREMENT PRIMARY KEY,
#                 school_id INT NOT NULL,
#                 student_id INT NOT NULL,
#                 class_assigned VARCHAR(50),
#                 division_assigned VARCHAR(50),
#                 date DATE NOT NULL,
#                 is_present BOOLEAN DEFAULT FALSE,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                 FOREIGN KEY (school_id) REFERENCES school(id),
#                 FOREIGN KEY (student_id) REFERENCES `{school_name}_Student`(id)
#             );
#         """)

# def drop_school_tables(school_name):
#     school_name = school_name.replace(" ", "_").replace("-", "_")
    
#     with connection.cursor() as cursor:
#         cursor.execute(f"DROP TABLE IF EXISTS `{school_name}_Teacher`;")
#         cursor.execute(f"DROP TABLE IF EXISTS `{school_name}_Parent`;")
#         cursor.execute(f"DROP TABLE IF EXISTS `{school_name}_Student`;")
#         cursor.execute(f"DROP TABLE IF EXISTS `{school_name}_Attendance`;")

# @receiver(post_save, sender=School)
# def create_and_register_school_models(sender, instance, created, **kwargs):
#     if created:
#         school_name = instance.school_name
#         create_school_tables(school_name)
        
#         for model_name in ['Teacher', 'Parent', 'Student', 'Attendance']:
#             table_name = f"{school_name.replace(' ', '_').replace('-', '_')}_{model_name}"
#             model_class = create_dynamic_model(table_name)
            
#             if model_class.__name__.lower() not in [model._meta.model_name for model in admin.site._registry.keys()]:
#                 admin.site.register(model_class, type(f'{model_class.__name__}Admin', (admin.ModelAdmin,), {}))

# @receiver(post_delete, sender=School)
# def delete_school_models(sender, instance, **kwargs):
#     school_name = instance.school_name.replace(" ", "_").replace("-", "_")
#     drop_school_tables(school_name)

#     # Unregister models from admin panel
#     for model_name in ['Teacher', 'Parent', 'Student', 'Attendance']:
#         table_name = f"{school_name}_{model_name}"
#         model_class = create_dynamic_model(table_name)
        
#         if model_class in admin.site._registry:
#             admin.site.unregister(model_class)
