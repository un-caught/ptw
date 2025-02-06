# Generated by Django 4.2.4 on 2025-01-22 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_ptwform_applicant_date_ptwform_applicant_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ptwform',
            name='certificates_required',
            field=models.CharField(blank=True, choices=[('CERTIFICATE_FOR_EXCAVATION_WORK', 'CERTIFICATE_FOR_EXCAVATION_WORK'), ('CERTIFICATE_FOR_HOT_WORK', 'CERTIFICATE_FOR_HOT_WORK'), ('CERTIFICATE_FOR_ELECTRICAL_WORK', 'CERTIFICATE_FOR_ELECTRICAL_WORK'), ('GAS_TEST_FORM', 'GAS_TEST_FORM'), ('CERTIFICATE_FOR_CONFINED_SPACES', 'CERTIFICATE_FOR_CONFINED_SPACES')], max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='ptwform',
            name='facility_manager_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='ptwform',
            name='facility_manager_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='ptwform',
            name='facility_manager_sign',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
