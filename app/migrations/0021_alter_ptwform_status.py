# Generated by Django 4.2.4 on 2025-01-30 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_nhisform_date_submitted_ptwform_date_submitted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ptwform',
            name='status',
            field=models.CharField(choices=[('awaiting_supervisor', 'Awaiting Supervisor Approval'), ('awaiting_manager', 'Awaiting Manager Approval'), ('approved', 'Approved'), ('disapproved', 'Disapproved')], default='awaiting_supervisor', max_length=20),
        ),
    ]
