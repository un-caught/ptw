from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import LeaveBalance, Leave
from django.contrib.auth.models import Group, User
from .forms import LeaveForm
from django.shortcuts import render
from datetime import datetime
from django.db.models import Q

# Create your views here.
def home(request):
    
    return render(request, 'leave/index.html', )


def leave_application(request):
    if request.method == 'POST':
        form = LeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.user = request.user
            leave.status = 'PENDING'
            leave.save()
            return redirect('leave:home')
    else:
        form = LeaveForm()

    # Leave limits
    max_leave_days = {
        'Casual Leave': 5,
        'Annual Leave': 15,
        'Sick Leave': 5,
        'Exam Leave': 14,
        'Maternity Leave': 84,
        'Compassionate Leave': 10,
    }

    try:
        balance = LeaveBalance.objects.get(user=request.user)
        leave_balances = {
            'Casual Leave': {
                'used': balance.casual_leave_used,
                'max': max_leave_days['Casual Leave'],
            },
            'Annual Leave': {
                'used': balance.annual_leave_used,
                'max': max_leave_days['Annual Leave'],
            },
            'Sick Leave': {
                'used': balance.sick_leave_used,
                'max': max_leave_days['Sick Leave'],
            },
            'Exam Leave': {
                'used': balance.exam_leave_used,
                'max': max_leave_days['Exam Leave'],
            },
            'Maternity Leave': {
                'used': balance.maternity_leave_used,
                'max': max_leave_days['Maternity Leave'],
            },
            'Compassionate Leave': {
                'used': balance.compassionate_leave_used,
                'max': max_leave_days['Compassionate Leave'],
            },
        }
    except LeaveBalance.DoesNotExist:
        # If no LeaveBalance record, set all used to 0
        leave_balances = {
            leave_type: {'used': 0, 'max': max_leave_days[leave_type]}
            for leave_type in max_leave_days
        }

    # Calculate outstanding balances
    for data in leave_balances.values():
        data['outstanding'] = data['max'] - data['used']

    return render(request, 'leave_application.html', {
        'form': form,
        'leave_balances': leave_balances
    })


def leave_history(request):
    current_year = datetime.now().year
    current_month = datetime.now().month

    # Get the selected year and month from GET parameters, or default to current month and year
    year = request.GET.get('year', current_year)
    month = request.GET.get('month', current_month)

    # Create a list of years (e.g., current year and previous 5 years)
    years = [current_year - i for i in range(5)]  # This gives a list of the last 5 years

    # Create a list of months
    months = [
        {'value': 1, 'name': 'January'},
        {'value': 2, 'name': 'February'},
        {'value': 3, 'name': 'March'},
        {'value': 4, 'name': 'April'},
        {'value': 5, 'name': 'May'},
        {'value': 6, 'name': 'June'},
        {'value': 7, 'name': 'July'},
        {'value': 8, 'name': 'August'},
        {'value': 9, 'name': 'September'},
        {'value': 10, 'name': 'October'},
        {'value': 11, 'name': 'November'},
        {'value': 12, 'name': 'December'},
    ]

    # Filter leaves by the selected month and year for the logged-in user
    leaves = Leave.objects.filter(
        user=request.user,
        start_date__year=year,
        start_date__month=month
    )

    return render(request, 'leave_history.html', {
        'leaves': leaves,
        'year': year,
        'month': month,
        'current_year': current_year,
        'current_month': current_month,
        'years': years,  # Pass the list of years to the template
        'months': months,  # Pass the list of months to the template
    })



def relief_officer(request):
    user = request.user
    leave_requests = Leave.objects.filter(relief_officer=user)

    context = {
        'leave_requests': leave_requests,
        'leave_count': leave_requests.count(),
    }

    return render(request, 'relief_officer_list.html', context)