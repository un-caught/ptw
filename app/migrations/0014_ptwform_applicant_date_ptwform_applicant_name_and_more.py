# Generated by Django 4.2.4 on 2025-01-22 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_remove_ptwform_applicant_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ptwform',
            name='applicant_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='ptwform',
            name='applicant_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='ptwform',
            name='applicant_sign',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='ptwform',
            name='supervisor_name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
