from django.db import models
from django.contrib.auth.models import User
import uuid
import random
import string

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Priority(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

# Create your models here.
class HELPForm(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    form_id = models.CharField(max_length=12, unique=True, editable=False, null=True, blank=True)
    date_submitted = models.DateTimeField(auto_now_add=True, null=True)
    location = models.CharField(max_length=255, choices=[
        ('HQ_Lekki', 'HQ Lekki'),
        ('CGS_Ikorodu', 'CGS Ikorodu'),
        ('LNG_PH', 'LNG PH'),
        ('LFZ_Ibeju', 'LFZ Ibeju'),
    ], blank=True, null=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)


    issue = models.CharField(max_length=255, choices=[
        ('IT', 'IT Support'),
    ], blank=True, null=True)

    priority = models.ForeignKey(Priority, on_delete=models.SET_NULL, blank=True, null=True)


    subject = models.CharField(max_length=255, null=True)
    complaint = models.TextField(null=True)
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)

    status = models.CharField(
        max_length=25,
        choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('resolved', 'Resolved'),
            ('closed', 'Closed'),
            ('closed_by_complainant', 'Closed By Complainant')

        ],
        default='pending',
    )

    admin_response = models.TextField(null=True, blank=True)
    response_timestamp = models.DateTimeField(null=True, blank=True)

    # New field for user rating of admin's response
    rating = models.PositiveIntegerField(
        choices=[(1, '1 - Poor'), (2, '2 - Fair'), (3, '3 - Good'), (4, '4 - Very Good'), (5, '5 - Excellent')],
        null=True, blank=True
    )

    def save(self, *args, **kwargs):
        if not self.form_id:
            self.form_id = self.generate_unique_form_id()
        super().save(*args, **kwargs)

    def generate_unique_form_id(self):
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            if not HELPForm.objects.filter(form_id=code).exists():
                return code

    def __str__(self):
        return self.form_id or f"HELPForm-{self.pk}"
