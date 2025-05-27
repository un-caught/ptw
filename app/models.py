from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

# Create your models here.
class Member(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def customer(self):
        return self.name
    

class SafetyPrecaution(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.name}"

class WorkLocationIsolation(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class PersonalSafety(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class Hazards(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name
    

class PTWForm(models.Model):
    # Section 1: Work Details
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    date_submitted = models.DateTimeField(auto_now_add=True, null=True)
    location = models.CharField(max_length=255, choices=[
        ('HQ_Lekki', 'HQ_Lekki'),
        ('CGS_Ikorodu', 'CGS_Ikorodu'),
        ('LNG_PH', 'LNG_PH'),
        ('LFZ_Ibeju', 'LFZ_Ibeju'),
    ], blank=True, null=True)
    work_description = models.TextField(null=True)
    equipment_tools_materials = models.TextField(null=True)
    risk_assessment_done = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], null=True)
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)
    project_attachment = models.FileField(upload_to='attachments/', null=True, blank=True)


    # Section 2: Work Duration and Personnel
    start_datetime = models.DateTimeField(null=True)
    duration = models.CharField(max_length=255, null=True)
    days = models.IntegerField(null=True)
    workers_count = models.IntegerField(null=True)
    department = models.CharField(max_length=255, null=True)
    contractor = models.CharField(max_length=255, null=True)
    contractor_supervisor = models.CharField(max_length=255, null=True)

    # Section 3: Safety Precautions
    work_place = models.ManyToManyField(SafetyPrecaution, blank=True)
    work_location_isolation = models.ManyToManyField(WorkLocationIsolation, blank=True)
    personal_safety = models.ManyToManyField(PersonalSafety, blank=True)
    additional_precautions = models.TextField(blank=True)

     # Section 4: Permit Applicant
    supervisor_name = models.CharField(max_length=255, null=True)
    applicant_name = models.CharField(max_length=255, null=True)
    applicant_date = models.DateField(null=True)
    applicant_sign = models.CharField(max_length=255, null=True)

     # Section 5: Facility Manager
    facility_manager_name = models.CharField(max_length=255, null=True)
    facility_manager_date = models.DateField(null=True)
    facility_manager_sign = models.CharField(max_length=255, null=True)
    certificates_required = models.CharField(max_length=255, choices=[
        ('CERTIFICATE_FOR_EXCAVATION_WORK', 'CERTIFICATE_FOR_EXCAVATION_WORK'),
        ('CERTIFICATE_FOR_HOT_WORK', 'CERTIFICATE_FOR_HOT_WORK'),
        ('CERTIFICATE_FOR_ELECTRICAL_WORK', 'CERTIFICATE_FOR_ELECTRICAL_WORK'),
        ('GAS_TEST_FORM', 'GAS_TEST_FORM'),
        ('CERTIFICATE_FOR_CONFINED_SPACES', 'CERTIFICATE_FOR_CONFINED_SPACES'),
        ('NOT_APPLICABLE', 'NOT_APPLICABLE'),
    ], blank=True, null=True)

    # Section 6: Validity and Renewal
    valid_from = models.DateField(null=True)
    valid_to = models.DateField(null=True)
    initials = models.CharField(max_length=100, null=True)

    # Section 7: Contractor
    contractor_name = models.CharField(max_length=255, null=True)
    contractor_date = models.DateField(null=True)
    contractor_sign = models.CharField(max_length=255, null=True)

    # Section 8: HSEQ
    hseq_name = models.CharField(max_length=255, null=True)
    hseq_date = models.DateField(null=True)
    hseq_sign = models.CharField(max_length=255, null=True)

    # Section 9: Manager
    manager_name = models.CharField(max_length=255, null=True)
    manager_date = models.DateField(null=True)
    manager_sign = models.CharField(max_length=255, null=True)

    @property
    def remark(self):
        if self.start_datetime and self.days is not None:
            try:
                end_date = self.start_datetime + timedelta(days=self.days)
                if end_date < timezone.now():
                    return "Closed"
                else:
                    return "Open"
            except Exception:
                return "Invalid Date"
        return "Incomplete Data"


    status = models.CharField(
        max_length=20,
        choices=[
            ('awaiting_supervisor', 'Awaiting Supervisor Approval'),
            ('supervisor_signed', 'Supervisor Signed'),
            ('awaiting_manager', 'Awaiting Manager Approval'),
            ('manager_signed', 'Manager Signed'),
            ('approved', 'Approved'),
            ('disapproved', 'Disapproved'),
        ],
        default='awaiting_supervisor',
    )

    def __str__(self):
        return self.name


class NHISForm(models.Model):
    # Section 1: General Information
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    date_submitted = models.DateTimeField(auto_now_add=True, null=True)
    location = models.CharField(max_length=50, choices=[
        ('HQ_Lekki', 'HQ_Lekki'),
        ('CGS_Ikorodu', 'CGS_Ikorodu'),
        ('LNG_PH', 'LNG_PH'),
        ('LFZ_Ibeju', 'LFZ_Ibeju'),
    ], blank=True, null=True)
    date = models.DateField(null=True)
    observed_by = models.CharField(max_length=255, null=True)
    other_location = models.CharField(max_length=255, null=True)
    activity = models.CharField(max_length=255, null=True)
    observation = models.TextField(blank=True)
    hazard = models.ManyToManyField(Hazards, blank=True)
    action_taken = models.TextField(blank=True)
    preventive_action = models.TextField(blank=True)   
    status = models.CharField(
        max_length=20,
        choices=[
            ('awaiting_supervisor', 'Awaiting Supervisor Approval'),
            ('awaiting_manager', 'Awaiting Manager Approval'),
            ('closed', 'Closed'),
            ('denied', 'Denied'),
        ],
        default='awaiting_supervisor',
    )

    def __str__(self):
        return self.name



class Notification(models.Model):
    recipient = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    message = models.TextField(null=True)
    link = models.URLField(blank=True, null=True)  # Link to the form, if needed
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To {self.recipient.username} - {self.message[:30]}"
