# Generated by Django 5.1 on 2024-08-19 05:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0034_remove_class_teacher_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='class_teacher',
            name='user_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='user_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='teacher',
            name='user_name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
