from django.shortcuts import render, redirect, get_object_or_404
from .forms import CreateUserForm, PTWSubmissionForm, NHISSubmissionForm
from django.contrib.auth.models import Group, User
from django.contrib.auth import authenticate, login, logout
from .models import Member, PTWForm, NHISForm, Notification
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import allowed_users, unauthenticated_user
from django.core.mail import send_mail
from django.conf import settings
from django.utils.dateparse import parse_date
from datetime import datetime
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

import openpyxl

import numpy as np


from io import BytesIO
import os
import matplotlib.pyplot as plt
import matplotlib
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import tempfile

import io
import base64
from django.db.models import Count
from django.db.models.functions import TruncMonth
from matplotlib.ticker import MaxNLocator
import matplotlib.dates as mdates
import seaborn as sns

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.html import format_html



# Ensure we use the Agg backend for matplotlib (headless rendering)
matplotlib.use('Agg')


def custom_404(request, exception=None):
    return render(request, '404.html', status=404)



@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('app:dashboard')

        else:
            messages.info(request, 'Username or Password is incorrect')
    return render(request, 'login.html')



@login_required(login_url='app:login')
def logoutUser(request):
    logout(request)
    return redirect('app:login') 


@unauthenticated_user
def registerPage(request):   
    form = CreateUserForm()
    
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            group_name = form.cleaned_data.get('group_choices')

            try:
                group = Group.objects.get(name=group_name)
            except Group.DoesNotExist:
                messages.error(request, f"Group {group_name} does not exist.")
                return redirect('app:register')

            user.groups.add(group)
            Member.objects.create(
                user=user,
                )

            messages.success(request, f"Account was created for {username}.")

            return redirect('app:register')

    context = {'form':form}
    return render(request, 'register.html', context)


@login_required(login_url='app:login')
def dashboard(request):
    return render(request, 'dashboard.html')



@login_required(login_url='app:login')
@allowed_users(allowed_roles=['staff', 'vendor'])
def clientDashboard(request):
    return render(request, 'client.html')




@login_required(login_url='app:login')
@allowed_users(allowed_roles=['supervisor'])
def supervisorDashboard(request):

    location_group_map = {
        'supervisor_hq': 'HQ_Lekki',
        'supervisor_cgs': 'CGS_Ikorodu',
        'supervisor_lng': 'LNG_PH',
        'supervisor_lfz': 'LFZ_Ibeju',
    }

    # Get the supervisor's group and determine their location
    user_groups = request.user.groups.values_list('name', flat=True)
    user_location = None
    for group in user_groups:
        if group in location_group_map:
            user_location = location_group_map[group]
            break

    # Fallback: show no data if location isn't matched
    if not user_location:
        context = {
            'total_ptw': 0,
            'approved_ptw': 0,
            'disapproved_ptw': 0,
            'pending_ptw': 0,
            'total_nhis': 0,
            'closed_nhis': 0,
            'denied_nhis': 0,
            'pending_nhis': 0,
            'combined_chart': None,
        }
        return render(request, 'supervisor.html', context)

    # Query PTW forms filtered by the supervisor's location
    total_ptw = PTWForm.objects.filter(location=user_location).count()
    approved_ptw = PTWForm.objects.filter(location=user_location, status='approved').count()
    disapproved_ptw = PTWForm.objects.filter(location=user_location, status='disapproved').count()
    pending_ptw = PTWForm.objects.filter(location=user_location, status__in=['awaiting_supervisor', 'awaiting_manager']).count()

    # Query NHIS forms filtered by the supervisor's location
    total_nhis = NHISForm.objects.filter(location=user_location).count()
    closed_nhis = NHISForm.objects.filter(location=user_location, status='closed').count()
    denied_nhis = NHISForm.objects.filter(location=user_location, status='denied').count()
    pending_nhis = NHISForm.objects.filter(location=user_location, status__in=['awaiting_supervisor', 'awaiting_manager']).count()

    # Get the current year
    current_year = datetime.now().year

    # Define the list of all months
    all_months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    # Query PTW forms grouped by month
    ptw_monthly_stats = PTWForm.objects.filter(date_submitted__year=current_year, location=user_location) \
                                       .annotate(month=TruncMonth('date_submitted')) \
                                       .values('month') \
                                       .annotate(count=Count('id')) \
                                       .order_by('month')

    # Initialize the counts for each month (start with zero)
    ptw_counts = [0] * 12
    ptw_months = all_months[:]  # Copy the list of all months

    # Map the month data from the query into the list
    for stat in ptw_monthly_stats:
        month_index = stat['month'].month - 1
        ptw_counts[month_index] = stat['count']

    # Query NHIS forms grouped by month
    nhis_monthly_stats = NHISForm.objects.filter(date_submitted__year=current_year, location=user_location) \
                                         .annotate(month=TruncMonth('date_submitted')) \
                                         .values('month') \
                                         .annotate(count=Count('id')) \
                                         .order_by('month')

    # Initialize the counts for each month (start with zero)
    nhis_counts = [0] * 12

    # Map the month data from the query into the list
    for stat in nhis_monthly_stats:
        month_index = stat['month'].month - 1
        nhis_counts[month_index] = stat['count']

    # Set Seaborn style
    sns.set_theme(style="whitegrid")  # You can experiment with different themes like "darkgrid", "ticks", etc.
    
    # Create the combined bar chart for PTW and NHIS forms
    fig, ax = plt.subplots(figsize=(11, 6))  # Increase figure size for better visibility
    width = 0.35  # the width of the bars

    # Create positions for PTW and NHIS bars
    x = range(12)

    # Use Seaborn color palettes
    ptw_color = sns.color_palette("Blues")[5]  # A nice shade of blue
    nhis_color = sns.color_palette("Oranges")[4]  # A nice shade of orange

    ax.bar(x, ptw_counts, width, label='PTW Forms', color=ptw_color, edgecolor='black')
    ax.bar([p + width for p in x], nhis_counts, width, label='NHIS Forms', color=nhis_color, edgecolor='black')

    ax.set_xticks([p + width / 2 for p in x])
    ax.set_xticklabels(all_months, rotation=45, ha='right')  # Rotate month labels for readability

    # Beautify chart with gridlines, title, and axis labels
    ax.set_xlabel('Month', fontsize=14, fontweight='bold')
    ax.set_ylabel('Number of Forms', fontsize=14, fontweight='bold')
    ax.set_title(f'Monthly PTW and NHIS Form Submissions ({current_year})', fontsize=16, fontweight='bold')

    ax.legend(title='Form Types', fontsize=12)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))  # Ensure the y-axis is integer

    # Add gridlines for better readability
    ax.grid(True, linestyle='--', alpha=0.6)

    # Save the combined chart to a BytesIO object to embed in the template
    buffer = io.BytesIO()
    plt.tight_layout()  # Improve layout to avoid clipping of labels
    plt.savefig(buffer, format='png', transparent=True)
    buffer.seek(0)
    combined_chart_image = base64.b64encode(buffer.read()).decode()

    # Return the context with the metrics and the combined chart
    context = {
        'total_ptw': total_ptw,
        'approved_ptw': approved_ptw,
        'disapproved_ptw': disapproved_ptw,
        'pending_ptw': pending_ptw,
        'total_nhis': total_nhis,
        'closed_nhis': closed_nhis,
        'denied_nhis': denied_nhis,
        'pending_nhis': pending_nhis,
        'combined_chart': combined_chart_image,  # Combined chart image
    }

    return render(request, 'supervisor.html', context)



@login_required(login_url='app:login')
@allowed_users(allowed_roles=['manager'])
def managerDashboard(request):
    location_group_map = {
        'manager_hq': 'HQ_Lekki',
        'manager_cgs': 'CGS_Ikorodu',
        'manager_lng': 'LNG_PH',
        'manager_lfz': 'LFZ_Ibeju',
    }

    # Get the manager's group and determine their location
    user_groups = request.user.groups.values_list('name', flat=True)
    user_location = None
    for group in user_groups:
        if group in location_group_map:
            user_location = location_group_map[group]
            break

    # Fallback: show no data if location isn't matched
    if not user_location:
        context = {
            'approved_ptw': 0,
            'pending_ptw_manager': 0,
            'closed_nhis': 0,
            'pending_nhis_manager': 0,
            'combined_chart': None,
        }
        return render(request, 'manager.html', context)

    # Query PTW forms filtered by manager's location
    approved_ptw = PTWForm.objects.filter(location=user_location, status='approved').count()
    pending_ptw_manager = PTWForm.objects.filter(location=user_location, status='awaiting_manager').count()

    # Query NHIS forms filtered by manager's location
    closed_nhis = NHISForm.objects.filter(location=user_location, status='closed').count()
    pending_nhis_manager = NHISForm.objects.filter(location=user_location, status='awaiting_manager').count()

    # Get the current year and month list
    current_year = datetime.now().year
    all_months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    # Query PTW forms grouped by month
    ptw_monthly_stats = PTWForm.objects.filter(date_submitted__year=current_year, location=user_location) \
                                       .annotate(month=TruncMonth('date_submitted')) \
                                       .values('month') \
                                       .annotate(count=Count('id')) \
                                       .order_by('month')

    ptw_counts = [0] * 12
    for stat in ptw_monthly_stats:
        month_index = stat['month'].month - 1
        ptw_counts[month_index] = stat['count']

    # Query NHIS forms grouped by month
    nhis_monthly_stats = NHISForm.objects.filter(date_submitted__year=current_year, location=user_location) \
                                         .annotate(month=TruncMonth('date_submitted')) \
                                         .values('month') \
                                         .annotate(count=Count('id')) \
                                         .order_by('month')

    nhis_counts = [0] * 12
    for stat in nhis_monthly_stats:
        month_index = stat['month'].month - 1
        nhis_counts[month_index] = stat['count']

    # Set Seaborn style and create chart
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(11, 6))
    width = 0.35
    x = range(12)
    ptw_color = sns.color_palette("Blues")[5]
    nhis_color = sns.color_palette("Oranges")[4]

    ax.bar(x, ptw_counts, width, label='PTW Forms', color=ptw_color, edgecolor='black')
    ax.bar([p + width for p in x], nhis_counts, width, label='NHIS Forms', color=nhis_color, edgecolor='black')

    ax.set_xticks([p + width / 2 for p in x])
    ax.set_xticklabels(all_months, rotation=45, ha='right')
    ax.set_xlabel('Month', fontsize=14, fontweight='bold')
    ax.set_ylabel('Number of Forms', fontsize=14, fontweight='bold')
    ax.set_title(f'Monthly PTW and NHIS Form Submissions ({current_year})', fontsize=16, fontweight='bold')
    ax.legend(title='Form Types', fontsize=12)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(True, linestyle='--', alpha=0.6)

    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png', transparent=True)
    buffer.seek(0)
    combined_chart_image = base64.b64encode(buffer.read()).decode()

    context = {
        'approved_ptw': approved_ptw,
        'pending_ptw_manager': pending_ptw_manager,
        'closed_nhis': closed_nhis,
        'pending_nhis_manager': pending_nhis_manager,
        'combined_chart': combined_chart_image,
    }

    return render(request, 'manager.html', context)



def send_mail_to_user_and_location_supervisors(user_email, subject, message_html, location):
    
    location_group_map = {
        'supervisor_hq': 'HQ_Lekki',
        'supervisor_cgs': 'CGS_Ikorodu',
        'supervisor_lng': 'LNG_PH',
        'supervisor_lfz': 'LFZ_Ibeju',
    }

    supervisor_group_name = next(
        (group_key for group_key, group_location in location_group_map.items()
         if group_location == location and group_key.startswith('supervisor')), None
    )

    if supervisor_group_name:
        try:
            supervisor_group = Group.objects.get(name=supervisor_group_name)
            supervisor_emails = User.objects.filter(groups=supervisor_group).values_list('email', flat=True)
        except Group.DoesNotExist:
            supervisor_emails = []
    else:
        supervisor_emails = []

    recipient_list = [user_email] + list(supervisor_emails)

    # Strip HTML to create plain text version
    text_content = strip_tags(message_html)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.EMAIL_HOST_USER,
        to=recipient_list,
    )
    email.attach_alternative(message_html, "text/html")
    email.send()



@login_required(login_url='app:login')
@allowed_users(allowed_roles=['vendor'])
def create_ptw_form(request):
    if request.method == 'POST':
        form = PTWSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            attachment = request.FILES.get('attachment')  # For single file upload
            project_attachment = request.FILES.get('project_attachment')
            submission.attachment = attachment
            submission.project_attachment = project_attachment
            submission.user = request.user
            submission.save()

            form.save_m2m()
            notify_users_by_location(submission, form_type='PTW Form')


            # Construct the email message
            subject = "🚧 New PTW Form Submission"

            message_html = f"""
            <html>
            <head></head>
            <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
              <div style="max-width: 600px; margin: auto; background-color: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
                <h2 style="color: #2c3e50;">🔔 PTW Form Submission Notification</h2>
                <p>A new <strong>Permit to Work (PTW)</strong> form has been submitted. Here are the details:</p>

                <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                  <tr><td style="padding: 8px; border: 1px solid #ddd;">👤 <strong>User:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{request.user.get_full_name()} ({request.user.email})</td></tr>
                  <tr><td style="padding: 8px; border: 1px solid #ddd;">📍 <strong>Location:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{submission.location}</td></tr>
                  <tr><td style="padding: 8px; border: 1px solid #ddd;">📅 <strong>Date Started:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{submission.start_datetime.strftime('%Y-%m-%d %H:%M')}</td></tr>
                  <tr><td style="padding: 8px; border: 1px solid #ddd;">📝 <strong>Description:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{submission.work_description}</td></tr>
                </table>

                <p style="margin-top: 20px;">🔗 You can view the full details in the <a href="{request.build_absolute_uri('/admin/')}" style="color: #3498db;">Admin Panel</a>.</p>

                <p style="margin-top: 30px; font-size: 12px; color: #888;">This is an automated message. Please do not reply.</p>
              </div>
            </body>
            </html>
            """

            send_mail_to_user_and_location_supervisors(
                submission.user.email,
                subject,
                message_html,
                submission.location
            )
            return redirect('app:form_list')

        else:
            print(form.errors)
    else:
        form = PTWSubmissionForm()
    return render(request, 'ptw.html', {'form':form})



@login_required(login_url='app:login')
@allowed_users(allowed_roles=['vendor','supervisor','manager'])
def form_list(request):
    submissions = PTWForm.objects.none()

    if request.user.is_authenticated:
        start_date_str = request.GET.get('start_date', '')
        end_date_str = request.GET.get('end_date', '')

        start_date = None
        end_date = None

        try:
            if start_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            pass

        # All forms optionally filtered by search
        all_forms = PTWForm.objects.all()

        if start_date and end_date:
            all_forms = all_forms.filter(date_submitted__range=(start_date, end_date))

        # Staff: only see their own submissions
        if request.user.groups.filter(name='vendor').exists():
            submissions = all_forms.filter(user=request.user)


        else:
            # Map groups to their allowed locations
            location_group_map = {
                'supervisor_hq': 'HQ_Lekki',
                'supervisor_cgs': 'CGS_Ikorodu',
                'supervisor_lng': 'LNG_PH',
                'supervisor_lfz': 'LFZ_Ibeju',
                'manager_hq': 'HQ_Lekki',
                'manager_cgs': 'CGS_Ikorodu',
                'manager_lng': 'LNG_PH',
                'manager_lfz': 'LFZ_Ibeju',
            }

            # Loop through the user's groups to find matching access
            user_groups = request.user.groups.values_list('name', flat=True)
            for group in user_groups:
                if group.startswith('supervisor'):
                    allowed_location = location_group_map.get(group)
                    if allowed_location:
                        submissions = all_forms.filter(location=allowed_location)
                        break
                elif group.startswith('manager'):
                    allowed_location = location_group_map.get(group)
                    if allowed_location:
                        submissions = all_forms.filter(
                            location=allowed_location,
                            status__in=['awaiting_manager', 'closed']
                        )
                        break

    return render(request, 'form_list.html', {
        'submissions': submissions,
    })


@login_required(login_url='app:login')
@allowed_users(allowed_roles=['vendor','supervisor','manager'])
def edit_form(request, pk):
    submission = get_object_or_404(PTWForm, pk=pk)
    
    if request.method == 'POST':
        print("Form is being submitted")
        form = PTWSubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            form.save()

            # Check if the user is in the supervisor group
            if request.user.groups.filter(name='supervisor').exists():
                if submission.status == 'awaiting_supervisor':
                    submission.status = 'supervisor_signed'  # Change status to 'supervisor_signed'
                    submission.save()

            # Check if the user is in the manager group
            elif request.user.groups.filter(name='manager').exists():
                if submission.status == 'awaiting_manager':
                    submission.status = 'manager_signed'  # Change status to 'manager_signed'
                    submission.save()

            # After status update, redirect to the form list
            return redirect('app:form_list')
        else:
            print(form.errors)

    else:
        form = PTWSubmissionForm(instance=submission)

    return render(request, 'edit_form.html', {'form': form, 'submission': submission})




@login_required(login_url='app:login')
@allowed_users(allowed_roles=['vendor'])
def delete_form(request, pk):
    # Fetch the FormSubmission object or return a 404 if it doesn't exist
    submission = get_object_or_404(PTWForm, pk=pk)
    
    # Delete the submission
    submission.delete()

    # Redirect to the form list page after deletion
    return redirect('app:form_list')


@login_required(login_url='app:login')

def view_form(request, pk):
    # Get the form submission by its primary key (pk)
    submission = get_object_or_404(PTWForm, pk=pk)
    attachment_ext = os.path.splitext(submission.attachment.name)[1].lower()
    project_attachment_ext = os.path.splitext(submission.project_attachment.name)[1].lower()

    # Pass the form submission to the template for rendering
    return render(request, 'view_form.html', {'submission': submission, 'attachment_ext': attachment_ext, 'project_attachment_ext': project_attachment_ext})



@login_required(login_url='app:login')
@allowed_users(allowed_roles=['supervisor'])
def approve_supervisor(request, pk):
    submission = get_object_or_404(PTWForm, pk=pk)
    if submission.status == 'supervisor_signed':
        submission.status = 'awaiting_manager'  # Change status to 'awaiting supervisor approval'
        submission.save()
    return redirect('app:form_list')


@login_required(login_url='app:login')
@allowed_users(allowed_roles=['supervisor'])
def disapprove_supervisor(request, pk):
    submission = get_object_or_404(PTWForm, pk=pk)
    
    if request.user.groups.filter(name='supervisor').exists():  # Check if the user is a supervisor
        submission.status = 'disapproved'  # Change the status to 'disapproved'
        submission.save()  # Save the updated status
    return redirect('app:form_list')

# View to approve a submission (Manager Approval)
@login_required(login_url='app:login')
@allowed_users(allowed_roles=['manager'])
def approve_manager(request, pk):
    submission = get_object_or_404(PTWForm, pk=pk)
    if submission.status == 'manager_signed':
        submission.status = 'approved'
        submission.save()


        subject = "✅ PTW Form Approved"

        # Styled HTML Email Content
        message_html = f"""
        <html>
        <head></head>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px;">
          <div style="max-width: 600px; margin: auto; background-color: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
            <h2 style="color: #27ae60; font-size: 24px; text-align: center;">🎉 PTW Form Approved</h2>
            <p style="color: #555; font-size: 16px;">Dear {submission.user.get_full_name()},</p>
            
            <p style="color: #555; font-size: 16px;">
              We are pleased to inform you that your <strong>PTW (Permit To Work)</strong> form has been approved. Here are the details:
            </p>

            <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
              <tr><td style="padding: 12px; border: 1px solid #ddd; background-color: #f9f9f9;">📍 <strong>Location:</strong></td><td style="padding: 12px; border: 1px solid #ddd;">{submission.location}</td></tr>
              <tr><td style="padding: 12px; border: 1px solid #ddd; background-color: #f9f9f9;">📅 <strong>Date Submitted:</strong></td><td style="padding: 12px; border: 1px solid #ddd;">{submission.start_datetime.strftime('%Y-%m-%d %H:%M')}</td></tr>
              <tr><td style="padding: 12px; border: 1px solid #ddd; background-color: #f9f9f9;">📝 <strong>Work Description:</strong></td><td style="padding: 12px; border: 1px solid #ddd;">{submission.work_description}</td></tr>
            </table>

            <p style="color: #555; font-size: 16px; margin-top: 20px;">
               The Permit to Work (PTW) form has been successfully reviewed and approved. Your safety and compliance are important to us, and this approval ensures that the necessary safety measures are in place for the task. Please proceed with the work according to the approved terms, and always prioritize safety.
            </p>

            <p style="margin-top: 30px; font-size: 12px; color: #888; text-align: center;">This is an automated message. Please do not reply.</p>
          </div>
        </body>
        </html>
        """

        # Send the email to the user and supervisors based on the location
        send_mail_to_user_and_location_supervisors(
            submission.user.email,  # Send to the user's email
            subject,  # Subject of the email
            message_html,  # HTML content
            submission.location  # Location for the supervisors
        )


        Notification.objects.create(
            recipient=submission.user,
            message=f"Your NHIS form has been approved. The form is now closed.",
            link=f"/view_form/{submission.id}/"  # Link to view the form details
        )

    return redirect('app:form_list')


@login_required(login_url='app:login')
@allowed_users(allowed_roles=['manager'])
def disapprove_manager(request, pk):
    submission = get_object_or_404(PTWForm, pk=pk)

    if request.user.groups.filter(name='manager').exists(): 
        submission.status = 'disapproved' 
        submission.save()  
    return redirect('app:form_list')


@login_required(login_url='app:login')
@allowed_users(allowed_roles=['staff'])
def create_nhis_form(request):
    if request.method == 'POST':
        form = NHISSubmissionForm(request.POST)
        if form.is_valid():
            # Access the cleaned data for hazard
            submission = form.save(commit=False)
            submission.user = request.user
            submission.save()

            # Save the Many-to-Many relationship
            form.save_m2m()
            notify_users_by_location(submission, form_type='NHIS Form')

            subject = "🚧 New NHIR Form Submission"

            message_html = f"""
            <html>
            <head></head>
            <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
              <div style="max-width: 600px; margin: auto; background-color: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
                <h2 style="color: #2c3e50;">🔔 NHIR Form Submission Notification</h2>
                <p>A new <strong>Near Hazard Incident Report (NHIR)</strong> form has been submitted. Here are the details:</p>

                <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                  <tr><td style="padding: 8px; border: 1px solid #ddd;">👤 <strong>User:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{request.user.get_full_name()} ({request.user.email})</td></tr>
                  <tr><td style="padding: 8px; border: 1px solid #ddd;">📍 <strong>Location:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{submission.location}</td></tr>
                  <tr><td style="padding: 8px; border: 1px solid #ddd;">📅 <strong>Date Started:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{submission.date}</td></tr>
                  <tr><td style="padding: 8px; border: 1px solid #ddd;">📝 <strong>Observation:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{submission.observation}</td></tr>
                </table>

                <p style="margin-top: 20px;">🔗 You can view the full details in the System.</p>

                <p style="margin-top: 30px; font-size: 12px; color: #888;">This is an automated message. Please do not reply.</p>
              </div>
            </body>
            </html>
            """

            send_mail_to_user_and_location_supervisors(
                submission.user.email,
                subject,
                message_html,
                submission.location
            )

            return redirect('app:nhis_list')
    else:
        form = NHISSubmissionForm()
    return render(request, 'nhis.html', {'form':form})


def notify_users_by_location(form_submission, form_type='Form'):
    location_group_map = {
        'supervisor_hq': 'HQ_Lekki',
        'supervisor_cgs': 'CGS_Ikorodu',
        'supervisor_lng': 'LNG_PH',
        'supervisor_lfz': 'LFZ_Ibeju',
        'manager_hq': 'HQ_Lekki',
        'manager_cgs': 'CGS_Ikorodu',
        'manager_lng': 'LNG_PH',
        'manager_lfz': 'LFZ_Ibeju',
}

    location = form_submission.location

    for group_name, loc in location_group_map.items():
        if loc == location:
            try:
                group = Group.objects.get(name=group_name)
                for user in group.user_set.all():
                    # Generate the correct link based on the form type
                    if form_type == 'NHIS Form':
                        link = f"/view_nhis_form/{form_submission.id}/"  # Correct link for NHIS forms
                    elif form_type == 'PTW Form':
                        link = f"/view_form/{form_submission.id}/"  # Correct link for PTW forms
                    else:
                        link = f"/view_form/{form_submission.id}/"  # Default link

                    Notification.objects.create(
                        recipient=user,
                        message=f"New {form_type} submitted at {location}",
                        link=link
                    )
            except Group.DoesNotExist:
                continue



@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')
    return render(request, 'notifications.html', {'notifications': notifications})

@login_required
def read_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return redirect(notification.link or 'dashboard')  # or wherever you want



@login_required(login_url='app:login')
@allowed_users(allowed_roles=['staff','supervisor','manager'])
def nhis_list(request):
    submissions = NHISForm.objects.none()

    if request.user.is_authenticated:
        start_date_str = request.GET.get('start_date', '')
        end_date_str = request.GET.get('end_date', '')

        start_date = None
        end_date = None

        try:
            if start_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            pass

        # All forms optionally filtered by search
        all_forms = NHISForm.objects.all()
        if start_date and end_date:
            all_forms = all_forms.filter(date_submitted__range=(start_date, end_date))

        # Staff: only see their own submissions
        if request.user.groups.filter(name='staff').exists():
            submissions = all_forms.filter(user=request.user)

        # Supervisor and Manager role-based location filtering
        else:
            # Map groups to their allowed locations
            location_group_map = {
                'supervisor_hq': 'HQ_Lekki',
                'supervisor_cgs': 'CGS_Ikorodu',
                'supervisor_lng': 'LNG_PH',
                'supervisor_lfz': 'LFZ_Ibeju',
                'manager_hq': 'HQ_Lekki',
                'manager_cgs': 'CGS_Ikorodu',
                'manager_lng': 'LNG_PH',
                'manager_lfz': 'LFZ_Ibeju',
            }

            # Loop through the user's groups to find matching access
            user_groups = request.user.groups.values_list('name', flat=True)
            for group in user_groups:
                if group.startswith('supervisor'):
                    allowed_location = location_group_map.get(group)
                    if allowed_location:
                        submissions = all_forms.filter(location=allowed_location)
                        break
                elif group.startswith('manager'):
                    allowed_location = location_group_map.get(group)
                    if allowed_location:
                        submissions = all_forms.filter(
                            location=allowed_location,
                            status__in=['awaiting_manager', 'closed']
                        )
                        break

    return render(request, 'nhis_list.html', {
        'submissions': submissions,
    })


@login_required(login_url='app:login')
@allowed_users(allowed_roles=['supervisor'])
def approve_nhis_supervisor(request, pk):
    submission = get_object_or_404(NHISForm, pk=pk)
    if submission.status == 'awaiting_supervisor':
        submission.status = 'closed'  # Change status to 'awaiting supervisor approval'
        submission.save()

        subject = "✅ NHIR Form Approved"

        # Styled HTML Email Content
        message_html = f"""
        <html>
        <head></head>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px;">
          <div style="max-width: 600px; margin: auto; background-color: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
            <h2 style="color: #27ae60; font-size: 24px; text-align: center;">🎉 NHIR Form Approved</h2>
            <p style="color: #555; font-size: 16px;">Dear {submission.user.get_full_name()},</p>
            
            <p style="color: #555; font-size: 16px;">
              We are pleased to inform you that your <strong>NHIS (Near Hazard Incident Report)</strong> form has been approved. Here are the details:
            </p>

            <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
              <tr><td style="padding: 12px; border: 1px solid #ddd; background-color: #f9f9f9;">📍 <strong>Location:</strong></td><td style="padding: 12px; border: 1px solid #ddd;">{submission.location}</td></tr>
              <tr><td style="padding: 12px; border: 1px solid #ddd; background-color: #f9f9f9;">📅 <strong>Date Submitted:</strong></td><td style="padding: 12px; border: 1px solid #ddd;">{submission.date}</td></tr>
              <tr><td style="padding: 12px; border: 1px solid #ddd; background-color: #f9f9f9;">📝 <strong>Observation:</strong></td><td style="padding: 12px; border: 1px solid #ddd;">{submission.observation}</td></tr>
            </table>

            <p style="color: #555; font-size: 16px; margin-top: 20px;">
              The form has been successfully processed, and we appreciate your attention to safety and hazard reporting.
            </p>

            <p style="margin-top: 30px; font-size: 12px; color: #888; text-align: center;">This is an automated message. Please do not reply.</p>
          </div>
        </body>
        </html>
        """

        # Send the email to the user and supervisors based on the location
        send_mail_to_user_and_location_supervisors(
            submission.user.email,  # Send to the user's email
            subject,  # Subject of the email
            message_html,  # HTML content
            submission.location  # Location for the supervisors
        )


        Notification.objects.create(
            recipient=submission.user,
            message=f"Your NHIS form has been approved. The form is now closed.",
            link=f"/view_nhis_form/{submission.id}/"  # Link to view the form details
        )
    return redirect('app:nhis_list')


@login_required(login_url='app:login')
@allowed_users(allowed_roles=['supervisor'])
def disapprove_nhis_supervisor(request, pk):
    submission = get_object_or_404(NHISForm, pk=pk)
    
    if request.user.groups.filter(name='supervisor').exists():  # Check if the user is a supervisor
        submission.status = 'denied'  # Change the status to 'disapproved'
        submission.save()  # Save the updated status
    return redirect('app:nhis_list')

# View to approve a submission (Manager Approval)
@login_required(login_url='app:login')
@allowed_users(allowed_roles=['manager'])
def approve_nhis_manager(request, pk):
    submission = get_object_or_404(NHISForm, pk=pk)
    if submission.status == 'awaiting_manager':
        submission.status = 'closed' 
        submission.save()

        subject = "NHIS Form Approved"
        message = f"Dear {submission.user.get_full_name()},\n\nYour NHIS form located at '{submission.location}', \n\n Dated  '{submission.date}' has been approved by the manager.\n\nThank you."

        send_mail_to_user_and_supervisors(submission.user.email, subject, message)
    return redirect('app:nhis_list')


@login_required(login_url='app:login')
@allowed_users(allowed_roles=['manager'])
def disapprove_nhis_manager(request, pk):
    submission = get_object_or_404(NHISForm, pk=pk)

    if request.user.groups.filter(name='manager').exists(): 
        submission.status = 'denied' 
        submission.save()  
    return redirect('app:nhis_list')




@login_required(login_url='app:login')
@allowed_users(allowed_roles=['staff'])
def edit_nhis_form(request, pk):
    submission = get_object_or_404(NHISForm, pk=pk)
    if request.method == 'POST':
        form = NHISSubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            return redirect('app:nhis_list')  # Redirect to the list view after updating
    else:
        form = NHISSubmissionForm(instance=submission)
    return render(request, 'edit_nhis_form.html', {'form': form, 'submission': submission})


@login_required(login_url='app:login')
@allowed_users(allowed_roles=['staff'])
def delete_nhis_form(request, pk):
    # Fetch the FormSubmission object or return a 404 if it doesn't exist
    submission = get_object_or_404(NHISForm, pk=pk)
    
    # Delete the submission
    submission.delete()

    # Redirect to the form list page after deletion
    return redirect('app:nhis_list')


@login_required(login_url='app:login')
def view_nhis_form(request, pk):
    # Get the form submission by its primary key (pk)
    submission = get_object_or_404(NHISForm, pk=pk)

    # Pass the form submission to the template for rendering
    return render(request, 'view_nhis_form.html', {'submission': submission})




@login_required(login_url='app:login')
@allowed_users(allowed_roles=['admin', 'supervisor'])
def form_report(request):
    start_date = None
    end_date = None

    # Get the date range parameters from the request
    if 'startDate' in request.GET and 'endDate' in request.GET:
        start_date = request.GET.get('startDate')
        end_date = request.GET.get('endDate')

    # Parse the dates if they exist
    start_date = parse_date(start_date) if start_date else None
    end_date = parse_date(end_date) if end_date else None

    print(f"Start date: {start_date}, End date: {end_date}")

    # Initialize report_data to None initially
    report_data = []

    pie_chart_data_form_type = {'NHIS': 0, 'PTW': 0}
    pie_chart_data_status = {
        'approved': 0,
        'disapproved': 0,
        'awaiting_manager': 0,
        'awaiting_supervisor': 0,
        'closed': 0,
        'denied': 0,
    }
        # Location group map for access control
    location_group_map = {
        'supervisor_hq': 'HQ_Lekki',
        'supervisor_cgs': 'CGS_Ikorodu',
        'supervisor_lng': 'LNG_PH',
        'supervisor_lfz': 'LFZ_Ibeju',
        'manager_hq': 'HQ_Lekki',
        'manager_cgs': 'CGS_Ikorodu',
        'manager_lng': 'LNG_PH',
        'manager_lfz': 'LFZ_Ibeju',
    }

    # Determine user's allowed location from group
    user_groups = request.user.groups.values_list('name', flat=True)
    user_location = None
    for group in user_groups:
        if group in location_group_map:
            user_location = location_group_map[group]
            break


    # If a valid date range is provided, filter and fetch the data
    if start_date or end_date:
        # Fetch NHIS form submissions within the date range
        nhis_submissions = NHISForm.objects.all()
        if user_location:
            nhis_submissions = nhis_submissions.filter(location=user_location)
        if start_date and end_date:
            nhis_submissions = nhis_submissions.filter(date_submitted__range=[start_date, end_date])
        elif start_date:
            nhis_submissions = nhis_submissions.filter(date_submitted__gte=start_date)
        elif end_date:
            nhis_submissions = nhis_submissions.filter(date_submitted__lte=end_date)

        # Fetch PTW form submissions within the date range
        ptw_submissions = PTWForm.objects.all()
        if user_location:
            ptw_submissions = ptw_submissions.filter(location=user_location)
        if start_date and end_date:
            ptw_submissions = ptw_submissions.filter(date_submitted__range=[start_date, end_date])
        elif start_date:
            ptw_submissions = ptw_submissions.filter(date_submitted__gte=start_date)
        elif end_date:
            ptw_submissions = ptw_submissions.filter(date_submitted__lte=end_date)

        # Combine both form submissions into one list
        
        for submission in nhis_submissions:
            report_data.append({
                'form_type': 'NHIS',
                'form_id': submission.id,
                'date_submitted': submission.date_submitted.strftime('%Y-%m-%d'),
                'user': submission.user.get_full_name(),
                'location': submission.location,
                'status': submission.status,
            })

        for submission in ptw_submissions:
            report_data.append({
                'form_type': 'PTW',
                'form_id': submission.id,
                'date_submitted': submission.date_submitted.strftime('%Y-%m-%d'),
                'user': submission.user.get_full_name(),
                'location': submission.location,
                'status': submission.status,
            })

        

        for submission in report_data:
            pie_chart_data_form_type[submission['form_type']] += 1
            pie_chart_data_status[submission['status']] += 1

    else:
        pie_chart_data_form_type = None
        pie_chart_data_status = None



    if 'download_pdf' in request.GET:
        if not report_data:
             return HttpResponse('''                
                         <h1>There are no submissions made within specified</h1>
                         <button onclick="window.history.back();">Go Back</button>
                     ''')
        pdf_buffer = generate_pdf({
            'start_date': start_date,
            'end_date': end_date,
            'report_data': report_data,
        }, pie_chart_data_form_type, pie_chart_data_status)

        # Send PDF response
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="form_report_{datetime.now().strftime("%Y%m%d%H%M%S")}.pdf"'
        return response

    

    if 'export' in request.GET:
        return export_to_excel(report_data)

    # Return data to template for display
    return render(request, 'report.html', {
        'start_date': start_date,
        'end_date': end_date,
        'total_nhis': len(nhis_submissions) if report_data else 0,
        'total_ptw': len(ptw_submissions) if report_data else 0,
        'report_data': report_data,
        'pie_chart_data_form_type': pie_chart_data_form_type,
        'pie_chart_data_status': pie_chart_data_status,
    })



def export_to_excel(report_data):
    if not report_data:
             return HttpResponse('''                
                         <h1>There are no submissions made within specified</h1>
                         <button onclick="window.history.back();">Go Back</button>
                     ''')
    # Create a workbook and add a sheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Form Report"
    
    # Define the headers for the Excel sheet
    headers = ['Form Type', 'Form ID', 'Date Submitted', 'User', 'Location', 'Status']
    ws.append(headers)

    # Add the report data to the sheet
    for data in report_data:
        ws.append([
            data['form_type'],
            data['form_id'],
            data['date_submitted'],
            data['user'],
            data['location'],
            data['status'],
        ])

    # Set the response for downloading the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="form_report_{datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx"'

    # Save the workbook to the response
    wb.save(response)

    return response



# Generate a pie chart and return it as a BytesIO object
def generate_pie_chart(data, labels, title, colors):
    data = [d for d in data if d > 0]  # Only keep non-zero values
    labels = [labels[i] for i in range(len(data))]  # Corresponding labels
         
    fig, ax = plt.subplots(figsize=(4, 4))  # Pie chart size
    ax.pie(data, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, wedgeprops={'edgecolor': 'black'})
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
         
             # Save the pie chart to a temporary file in memory
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='PNG')
    plt.close(fig)
    img_buffer.seek(0)  # Reset the buffer position to the beginning
    return img_buffer

# Assuming `generate_pie_chart` and `save_image_to_temp_file` are already defined as per your code.
def generate_pdf(report_data, pie_chart_data_form_type, pie_chart_data_status):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 800, "Form Report")
    
    # Date Range
    p.setFont("Helvetica", 12)
    p.drawString(50, 730, f"Start Date: {report_data['start_date']}")
    p.drawString(50, 710, f"End Date: {report_data['end_date']}")

    # Report Data Table (Form Details)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 670, "Form Details:")
    y_position = 650

    # Table Headers
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y_position, "Form Type")
    p.drawString(130, y_position, "Form ID")
    p.drawString(210, y_position, "Date Submitted")
    p.drawString(330, y_position, "User")
    p.drawString(440, y_position, "Location")
    p.drawString(500, y_position, "Status")
    y_position -= 20

    # Table Rows
    p.setFont("Helvetica", 10)
    for submission in report_data['report_data']:
        p.drawString(50, y_position, submission['form_type'])
        p.drawString(130, y_position, str(submission['form_id']))
        p.drawString(210, y_position, submission['date_submitted'])
        p.drawString(330, y_position, submission['user'])
        p.drawString(440, y_position, submission['location'])
        p.drawString(500, y_position, submission['status'])
        y_position -= 20

    # Move to a new page before adding the images
    p.showPage()

    # Generate Pie Charts as images
    # Form Type Distribution Pie Chart
    form_type_data = [pie_chart_data_form_type.get('NHIS', 0), pie_chart_data_form_type.get('PTW', 0)]
    form_type_labels = ['NHIS', 'PTW']
    form_type_colors = ['#36A2EB', '#FFCE56']
    form_type_img_buffer = generate_pie_chart(form_type_data, form_type_labels, "Form Type Distribution", form_type_colors)

    # Completed PTW Status Distribution Pie Chart
    status_data = [pie_chart_data_status.get('approved', 0), pie_chart_data_status.get('disapproved', 0)]
    status_labels = ['Approved', 'Disapproved']
    status_colors = ['#4CAF50', '#d7290a']
    status_img_buffer = generate_pie_chart(status_data, status_labels, "Completed PTW Status Distribution", status_colors)

    # Completed NHIS Status Distribution Pie Chart
    nhis_status_data = [pie_chart_data_status.get('closed', 0), pie_chart_data_status.get('denied', 0)]
    nhis_status_labels = ['Closed', 'Denied']
    nhis_status_colors = ['#4CAF50', '#d7290a']
    nhis_status_img_buffer = generate_pie_chart(nhis_status_data, nhis_status_labels, "Completed NHIS Status Distribution", nhis_status_colors)

    # Status Distribution Pie Chart
    pending_data = [pie_chart_data_status.get('awaiting_manager', 0), pie_chart_data_status.get('awaiting_supervisor', 0)]
    pending_labels = ['Awaiting Manager', 'Awaiting Supervisor']
    pending_colors = ['#f48d0c', '#331f07']
    pending_img_buffer = generate_pie_chart(pending_data, pending_labels, "Pending Distribution", pending_colors)

    # Save images from buffer to temporary files
    temp_file_path_form_type = save_image_to_temp_file(form_type_img_buffer)
    temp_file_path_status = save_image_to_temp_file(status_img_buffer)
    temp_file_path_nhis_status = save_image_to_temp_file(nhis_status_img_buffer)
    temp_file_path_pending = save_image_to_temp_file(pending_img_buffer)

    chart_width = 180  # Smaller size
    chart_height = 180


    # Insert the images into the PDF using temporary file paths
    p.drawImage(temp_file_path_form_type, 50, 520, width=chart_width, height=chart_height)  # Form Type chart
    p.setFont("Helvetica", 8)
    p.drawString(50, 510, "Form Type Distribution (NHIS vs PTW)")  # Description under the chart

    p.drawImage(temp_file_path_status, 320, 520, width=chart_width, height=chart_height)  # PTW Status chart
    p.drawString(320, 510, "Completed PTW Status Distribution (Approved vs Disapproved)")  # Description under the chart

    p.drawImage(temp_file_path_nhis_status, 50, 320, width=chart_width, height=chart_height)  # NHIS Status chart
    p.drawString(50, 300, "Completed NHIS Status Distribution (Closed vs Denied)")  # Description under the chart

    p.drawImage(temp_file_path_pending, 320, 320, width=chart_width, height=chart_height)  # Pending Distribution chart
    p.drawString(320, 300, "Pending Distribution (Awaiting Manager vs Awaiting Supervisor)")  # Description under the chart

    p.showPage()  # Optional: Add another page if needed
    p.save()

    buffer.seek(0)
    return buffer


def save_image_to_temp_file(image_buffer):
    # Save image buffer to a temporary file and return the file path
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    temp_file.write(image_buffer.getvalue())
    temp_file.close()  # Close the file to ensure it's saved
    return temp_file.name  # Return the file path

