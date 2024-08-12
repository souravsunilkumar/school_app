# Generated by Django 5.1 on 2024-08-12 08:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('roll_number', models.CharField(max_length=10)),
                ('class_assigned', models.CharField(max_length=20)),
                ('division_assigned', models.CharField(max_length=10)),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='my_app.teacher')),
            ],
        ),
    ]
