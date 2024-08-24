from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth.models import User, Group
from .models import *

class Permission:
    
    @staticmethod
    def check_admin_permissions(user):
        
        if not user.groups.filter(name='main administrator').exists():
            raise PermissionDenied("You do not have permission to perform this action.")

    @staticmethod
    def check_sub_admin_permissions(user):
       
        if not user.groups.filter(name='main administrator').exists():
            raise PermissionDenied("You do not have permission to perform this action.")
    
    @staticmethod
    def validate_school_for_sub_admin(user, school_id):
        
        try:
            admin_school = School.objects.get(admin_user=user)
            selected_school = School.objects.get(id=school_id)
            if admin_school != selected_school:
                raise ValidationError("The selected school does not match the logged-in admin's school.")
        except School.DoesNotExist:
            raise ValidationError("School does not exist.")

    @staticmethod
    def add_sub_admin(username, password, confirm_password, first_name, last_name, school_id, contact_number):
        
        if password != confirm_password:
            raise ValidationError("Passwords do not match.")

        user = User.objects.get(username=username)
        Permission.check_sub_admin_permissions(user)

        Permission.validate_school_for_sub_admin(user, school_id)

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        sub_admin_group = Group.objects.get(id=9)  
        user.groups.add(sub_admin_group)

        
        Admin.objects.create(
            school=School.objects.get(id=school_id),
            first_name=first_name,
            second_name=last_name,
            user=user,
            username=username,
            contact_number=contact_number
        )

        return f"Sub admin {first_name} {last_name} registered successfully!"
