# Generated by Django 5.1 on 2024-08-23 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0002_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='admin',
            name='contact_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
