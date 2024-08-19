# Generated by Django 5.1 on 2024-08-16 09:45

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('my_app', '0018_remove_teacher_model_school_remove_student_school_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('school_name', models.CharField(max_length=255)),
                ('address', models.TextField()),
                ('contact', models.CharField(max_length=15)),
                ('school_admin_first_name', models.CharField(max_length=255, null=True)),
                ('school_admin_last_name', models.CharField(max_length=255, null=True)),
                ('school_admin_username', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('admission_number', models.CharField(max_length=20, null=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('roll_number', models.IntegerField(null=True)),
                ('class_assigned', models.CharField(max_length=20)),
                ('division_assigned', models.CharField(max_length=10)),
                ('school', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='my_app.school')),
            ],
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField(default=datetime.date.today)),
                ('is_present', models.BooleanField(default=False)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='my_app.student')),
            ],
        ),
        migrations.CreateModel(
            name='Teacher_Model',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('class_assigned', models.CharField(max_length=20)),
                ('division_assigned', models.CharField(max_length=10)),
                ('school', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='my_app.school')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='student',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='my_app.teacher_model'),
        ),
    ]
