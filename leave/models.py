from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# Choices for leave types
LEAVE_TYPES = [
    ('CL', 'Casual Leave'),
    ('AL', 'Annual Leave'),
    ('SL', 'Sick Leave'),
    ('EL', 'Exam/Study Leave'),
    ('ML', 'Maternity Leave'),
    ('CPL', 'Compassionate Leave'),
]

class LeaveBalance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    casual_leave_used = models.IntegerField(default=0)
    annual_leave_used = models.IntegerField(default=0)
    sick_leave_used = models.IntegerField(default=0)
    exam_leave_used = models.IntegerField(default=0)
    maternity_leave_used = models.IntegerField(default=0)
    compassionate_leave_used = models.IntegerField(default=0)

    def __str__(self):
        return f"Leave balance for {self.user.username}"

    def get_remaining_days(self, leave_type):
        max_leave_days = {
            'CL': 5,
            'AL': 15,
            'SL': 5,
            'EL': 14,
            'ML': 84,
            'CPL': 10,
        }
        leave_used = getattr(self, f"{leave_type.lower()}_used", 0)
        return max_leave_days.get(leave_type, 0) - leave_used

    def update_leave_balance(self, leave_type, days):
        if leave_type == 'CL':
            self.casual_leave_used += days
        elif leave_type == 'AL':
            self.annual_leave_used += days
        elif leave_type == 'SL':
            self.sick_leave_used += days
        elif leave_type == 'EL':
            self.exam_leave_used += days
        elif leave_type == 'ML':
            self.maternity_leave_used += days
        elif leave_type == 'CPL':
            self.compassionate_leave_used += days
        self.save()

class Leave(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=3, choices=LEAVE_TYPES)
    year = models.IntegerField()
    relief_officer = models.ForeignKey(User, related_name='relief_officer', on_delete=models.CASCADE)
    relief_officer_remark = models.TextField(blank=True, null=True)  # ➕ Relief officer remark
    hod_or_line_manager = models.ForeignKey(User, related_name='hod_or_line_manager', on_delete=models.CASCADE)
    purpose = models.TextField()
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    start_date = models.DateField()
    end_date = models.DateField()
    number_of_days = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')  # ➕ Leave status

    def save(self, *args, **kwargs):
        # Calculate number of days between start and end date
        self.number_of_days = (self.end_date - self.start_date).days + 1
        # Leave type validation based on the days
        if self.leave_type == 'CL' and self.number_of_days > 5:
            raise ValueError('Casual Leave can only be up to 5 days.')
        elif self.leave_type == 'AL' and self.number_of_days > 15:
            raise ValueError('Annual Leave can only be up to 15 days.')
        elif self.leave_type == 'EL' and self.number_of_days > 14:
            raise ValueError('Exam/Study Leave can only be up to 14 days.')
        elif self.leave_type == 'ML' and self.number_of_days > 84:
            raise ValueError('Maternity Leave can only be up to 84 days.')
        elif self.leave_type == 'CPL' and self.number_of_days > 10:
            raise ValueError('Compassionate Leave can only be up to 10 days.')
        super().save(*args, **kwargs)

        # Update leave balance only if approved
        if self.status == 'APPROVED':
            leave_balance = LeaveBalance.objects.get(user=self.user)
            leave_balance.update_leave_balance(self.leave_type, self.number_of_days)