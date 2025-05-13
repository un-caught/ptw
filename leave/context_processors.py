from leave.models import LeaveBalance, Leave
from django.db.models import Sum
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

def leave_data(request):
    # Query the leave balance for the user (this assumes the user is logged in)
    if request.user.is_authenticated:
        try:
            # Try to get the leave balance for the user
            leave_balance = LeaveBalance.objects.get(user=request.user)
        except ObjectDoesNotExist:
            # If no leave balance exists, handle it appropriately (optional)
            leave_balance = None

        # Get total leave days available (this is predefined)
        entitled_leave_days = {
            'CL': 5,   # Casual Leave
            'AL': 15,  # Annual Leave
            'SL': 5,   # Sick Leave
            'EL': 14,  # Exam/Study Leave
            'ML': 84,  # Maternity Leave
            'CPL': 10  # Compassionate Leave
        }

        # Query the leave used for each type by the user
        leave_used = Leave.objects.filter(user=request.user, year=timezone.now().year)
        
        leave_usage = {
            'CL': leave_used.filter(leave_type='CL').aggregate(Sum('number_of_days'))['number_of_days__sum'] or 0,
            'AL': leave_used.filter(leave_type='AL').aggregate(Sum('number_of_days'))['number_of_days__sum'] or 0,
            'SL': leave_used.filter(leave_type='SL').aggregate(Sum('number_of_days'))['number_of_days__sum'] or 0,
            'EL': leave_used.filter(leave_type='EL').aggregate(Sum('number_of_days'))['number_of_days__sum'] or 0,
            'ML': leave_used.filter(leave_type='ML').aggregate(Sum('number_of_days'))['number_of_days__sum'] or 0,
            'CPL': leave_used.filter(leave_type='CPL').aggregate(Sum('number_of_days'))['number_of_days__sum'] or 0,
        }

        # Create a dictionary to send to the context with more meaningful names
        context = {
            'entitled_annual_leave': entitled_leave_days['AL'],  # Total entitled annual leave days
            'used_annual_leave': leave_usage['AL'],  # Annual leave used
            'used_casual_leave': leave_usage['CL'],  # Casual leave used
            'used_sick_leave': leave_usage['SL'],  # Sick leave used
            'used_exam_study_leave': leave_usage['EL'],  # Exam/study leave used
            'used_compassionate_leave': leave_usage['CPL'],  # Compassionate leave used
            'used_maternity_leave': leave_usage['ML'],  # Maternity leave used
            'leave_balance': leave_balance,  # Additional info about leave balance (optional)
        }
    else:
        context = {}

    return context
