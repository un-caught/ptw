# Generated by Django 4.2.4 on 2025-05-04 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helpdesk', '0004_helpform_admin_response_helpform_rating_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='helpform',
            name='form_id',
            field=models.CharField(blank=True, editable=False, max_length=12, null=True, unique=True),
        ),
    ]
