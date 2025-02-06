# Generated by Django 4.2.4 on 2025-01-18 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PTWForm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(max_length=255)),
                ('work_description', models.TextField()),
                ('equipment', models.TextField()),
                ('risk_assessment_done', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')])),
                ('start_date', models.DateTimeField()),
                ('duration', models.CharField(max_length=255)),
                ('days', models.PositiveIntegerField()),
                ('workers', models.PositiveIntegerField()),
                ('department', models.CharField(max_length=255)),
                ('contractor', models.CharField(max_length=255)),
                ('supervisor', models.CharField(max_length=255)),
                ('spade_or_blinds', models.BooleanField(default=False)),
                ('physical_separation', models.BooleanField(default=False)),
                ('closed_valves', models.BooleanField(default=False)),
                ('locked_out_tagged_out', models.BooleanField(default=False)),
                ('depressurizing', models.BooleanField(default=False)),
                ('draining_venting', models.BooleanField(default=False)),
                ('flushing_with_water', models.BooleanField(default=False)),
                ('purging_with_nitrogen', models.BooleanField(default=False)),
                ('wearing_safety_signs', models.BooleanField(default=False)),
                ('temporary_demarcations', models.BooleanField(default=False)),
                ('road_closure', models.BooleanField(default=False)),
                ('scaffolding', models.BooleanField(default=False)),
                ('additional_lighting', models.BooleanField(default=False)),
                ('safety_helmet', models.BooleanField(default=False)),
                ('safety_shoes', models.BooleanField(default=False)),
                ('safety_spectacles', models.BooleanField(default=False)),
                ('safety_goggles', models.BooleanField(default=False)),
                ('full_face_visor', models.BooleanField(default=False)),
                ('protective_apron', models.BooleanField(default=False)),
                ('dust_protection', models.BooleanField(default=False)),
                ('breathing_apparatus', models.BooleanField(default=False)),
                ('hearing_protection', models.BooleanField(default=False)),
                ('rubber_harness', models.BooleanField(default=False)),
                ('safety_harness', models.BooleanField(default=False)),
                ('work_vest', models.BooleanField(default=False)),
                ('additional_precautions', models.TextField(blank=True)),
                ('supervisor_name', models.CharField(max_length=255)),
                ('applicant_name', models.CharField(max_length=255)),
                ('applicant_date', models.DateField()),
                ('applicant_sign', models.CharField(max_length=255)),
                ('facility_manager_name', models.CharField(max_length=255)),
                ('facility_date', models.DateField()),
                ('facility_sign', models.CharField(max_length=255)),
                ('certificates_required', models.JSONField()),
                ('valid_from', models.DateField()),
                ('valid_to', models.DateField()),
                ('initials', models.CharField(max_length=255)),
                ('contractor_name', models.CharField(max_length=255)),
                ('contractor_date', models.DateField()),
                ('contractor_sign', models.CharField(max_length=255)),
                ('hseq_name', models.CharField(max_length=255)),
                ('hseq_date', models.DateField()),
                ('hseq_sign', models.CharField(max_length=255)),
            ],
        ),
    ]
