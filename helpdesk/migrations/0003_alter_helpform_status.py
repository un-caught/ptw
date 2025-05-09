# Generated by Django 4.2.4 on 2025-05-01 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helpdesk', '0002_priority_alter_helpform_priority'),
    ]

    operations = [
        migrations.AlterField(
            model_name='helpform',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('resolved', 'Resolved'), ('closed', 'Closed'), ('closed_by_complainant', 'Closed By Complainant')], default='pending', max_length=25),
        ),
    ]
