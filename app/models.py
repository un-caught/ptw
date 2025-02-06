from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Member(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)

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
    location = models.CharField(max_length=100)
    work_description = models.TextField(null=True)
    equipment_tools_materials = models.TextField(null=True)
    risk_assessment_done = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], null=True)

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
    location = models.CharField(max_length=100)
    date = models.DateField(null=True)
    question = models.CharField(max_length=7, choices=[('option1', 'Option 1'), ('option2', 'Option 2')], null=True)
   
    # Section 2: Hazard Identification
    hazard = models.ManyToManyField(Hazards, blank=True)
    risk_type = models.CharField(max_length=255, choices=[
        ('UA', 'UA (Unsafe Act)'),
        ('UC', 'UC (Unsafe Condition)'),
        ('NM', 'NM (Near Miss)'),
    ], blank=True, null=True)
    ram_rating = models.CharField(max_length=255, choices=[
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ], blank=True, null=True)

    # Section 3: Obeservation
    observation = models.TextField(blank=True)

     # Section 4: Immediate Action Taken
    action_taken = models.TextField(blank=True)

     # Section 5: Preventive Action
    preventive_action = models.TextField(blank=True)

    # Section 6: Responsible Party And Target
    responsible_party = models.CharField(max_length=255, null=True)
    target_date = models.DateField(null=True)

    # Section 7: Observed By
    observed_by = models.CharField(max_length=255, null=True)
    dept = models.CharField(max_length=255, null=True)
    observed_date = models.DateField(null=True)
    
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

