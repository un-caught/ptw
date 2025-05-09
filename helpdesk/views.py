from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import HELPSubmissionForm
from django.contrib.auth.models import Group, User
from django.contrib.auth import authenticate, login, logout
from .models import HELPForm, Category, Priority
from django.utils.dateparse import parse_date
from datetime import datetime 
from django.contrib import messages
from .forms import CategoryForm, PriorityForm, AdminResponseForm, UserRatingForm
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from django.db.models import Count

import openpyxl
from django.contrib.auth.decorators import login_required
from openpyxl import Workbook

import io
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Image

from django.core.mail import EmailMessage
from django.utils.html import strip_tags
from .decorators import allowed_users
# Create your views here.

@login_required(login_url='app:login')
def home(request):
    
    return render(request, 'index.html', )

@login_required(login_url='app:login')
def create_help_form(request):
    if request.method == 'POST':
        form = HELPSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            attachment = request.FILES.get('attachment')  # For single file upload
            submission.attachment = attachment
            submission.user = request.user
            submission.save()
            messages.success(request, f"Ticket submitted successfully! Your reference ID is {submission.form_id}")

            form.save_m2m()

            # Get admin group emails
            admin_group = Group.objects.get(name="admin")
            admin_emails = list(admin_group.user_set.values_list('email', flat=True))
            recipients = admin_emails + [request.user.email]

            # Construct the inline HTML email
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f9f9f9;
                        padding: 20px;
                        color: #333;
                    }}
                    .container {{
                        background-color: #ffffff;
                        border-radius: 8px;
                        padding: 20px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                    }}
                    h2 {{
                        color: #007bff;
                        margin-bottom: 20px;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                    }}
                    th, td {{
                        text-align: left;
                        padding: 8px;
                        vertical-align: top;
                    }}
                    th {{
                        width: 150px;
                        color: #555;
                    }}
                    .footer {{
                        margin-top: 30px;
                        font-size: 12px;
                        color: #888;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>New Help Ticket Submitted</h2>
                    <p><strong>{request.user.get_full_name()}</strong> ({request.user.email}) has submitted a new help ticket.</p>

                    <table>
                        <tr>
                            <th>Reference ID:</th>
                            <td>{submission.form_id}</td>
                        </tr>
                        <tr>
                            <th>Location:</th>
                            <td>{submission.location}</td>
                        </tr>
                        <tr>
                            <th>Date Started:</th>
                            <td>{submission.date_submitted.strftime('%Y-%m-%d')}</td>
                        </tr>
                        <tr>
                            <th>Subject:</th>
                            <td>{submission.subject}</td>
                        </tr>
                    </table>

                    <p class="footer">
                        This is an automated message. You can view this ticket in the admin panel.
                    </p>
                </div>
            </body>
            </html>
            """

            # Strip tags for plain text fallback
            plain_text = strip_tags(html_content)

            email = EmailMessage(
                subject="New HELP Ticket Submitted",
                body=plain_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=recipients,
            )
            email.content_subtype = "html"
            email.body = html_content
            email.send(fail_silently=False)

            return redirect('helpdesk:help_list')

        else:
            print(form.errors)
    else:
        form = HELPSubmissionForm()

    context = {'form':form}
    return render(request, 'new_ticket.html', context)


@login_required(login_url='app:login')
def help_list(request):
    start_date = None
    end_date = None
    status = None

    # Get the date range parameters from the request
    if 'startDate' in request.GET and 'endDate' in request.GET:
        start_date = request.GET.get('startDate')
        end_date = request.GET.get('endDate')
    
    # Parse the dates if they exist
    start_date = parse_date(start_date) if start_date else None
    end_date = parse_date(end_date) if end_date else None
    status = request.GET.get('status', None)

    report_data = []

    help_submissions = HELPForm.objects.filter(user=request.user)

    if start_date or end_date:
        if start_date and end_date:
            help_submissions = help_submissions.filter(date_submitted__range=[start_date, end_date])
        elif start_date:
            help_submissions = help_submissions.filter(date_submitted__gte=start_date)
        elif end_date:
            help_submissions = help_submissions.filter(date_submitted__lte=end_date)

    if status:
        help_submissions = help_submissions.filter(status=status)

    # Process the filtered submissions
    for submission in help_submissions:
        report_data.append({
            'form_id': submission.id,
            'id': submission.form_id,
            'location': submission.location,
            'date_submitted': submission.date_submitted.strftime('%Y-%m-%d'),
            'complaint': submission.complaint,
            'issue': submission.issue,
            'subject': submission.subject,
            'status': submission.status,
            'user': submission.user,
        })

    return render(request, 'list_ticket.html', {
        'start_date': start_date,
        'end_date': end_date,
        'status': status,  # Add the selected status to the context
        'total_help': len(help_submissions) if report_data else 0,
        'report_data': report_data,
    })


# View to list all categories
@login_required(login_url='app:login')
@allowed_users(allowed_roles=['admin'])
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})

# View to create a new category
@login_required(login_url='app:login')
@allowed_users(allowed_roles=['admin'])
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('category-list')
    else:
        form = CategoryForm()
    
    return render(request, 'category_form.html', {'form': form})

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['admin'])
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('helpdesk:category-list')  # After editing, redirect to the category list
    else:
        form = CategoryForm(instance=category)

    return render(request, 'category_form.html', {'form': form})


# View to delete a category
@login_required(login_url='app:login')
@allowed_users(allowed_roles=['admin'])
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('category-list')
    return render(request, 'category_confirm_delete.html', {'category': category})


# View to list all priority
@login_required(login_url='app:login')
@allowed_users(allowed_roles=['admin'])
def priority_list(request):
    priority = Priority.objects.all()
    return render(request, 'priority_list.html', {'priority': priority})

# View to create a new priority
@login_required(login_url='app:login')
@allowed_users(allowed_roles=['admin'])
def priority_create(request):
    if request.method == 'POST':
        form = PriorityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Priority created successfully!')
            return redirect('priority-list')
    else:
        form = PriorityForm()
    
    return render(request, 'priority_form.html', {'form': form})

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['admin'])
def priority_edit(request, pk):
    priority = get_object_or_404(Priority, pk=pk)

    if request.method == 'POST':
        form = PriorityForm(request.POST, instance=priority)
        if form.is_valid():
            form.save()
            return redirect('helpdesk:priority-list')  # After editing, redirect to the priority list
    else:
        form = PriorityForm(instance=priority)

    return render(request, 'priority_form.html', {'form': form})


# View to delete a priority
@login_required(login_url='app:login')
@allowed_users(allowed_roles=['admin'])
def priority_delete(request, pk):
    priority = get_object_or_404(Priority, pk=pk)
    if request.method == 'POST':
        priority.delete()
        messages.success(request, 'Priority deleted successfully!')
        return redirect('priority-list')
    return render(request, 'priority_confirm_delete.html', {'priority': priority})


@login_required(login_url='app:login')
@allowed_users(allowed_roles=['admin'])
def ticket_others(request):
    users = User.objects.all()
    if request.method == 'POST':
        form = HELPSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            attachment = request.FILES.get('attachment')  # For single file upload
            submission.attachment = attachment
            user_id = request.POST.get('user')  # Assuming 'user' is the name of the field in the form
            submission.user = User.objects.get(id=user_id)
            submission.save()
            messages.success(request, f"Ticket submitted successfully! Your reference ID is {submission.form_id}")

            form.save_m2m()
            admin_group = Group.objects.get(name="admin")
            admin_emails = list(admin_group.user_set.values_list('email', flat=True))
            recipients = admin_emails + [submission.user.email]

            # Construct the inline HTML email
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f9f9f9;
                        padding: 20px;
                        color: #333;
                    }}
                    .container {{
                        background-color: #ffffff;
                        border-radius: 8px;
                        padding: 20px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                    }}
                    h2 {{
                        color: #007bff;
                        margin-bottom: 20px;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                    }}
                    th, td {{
                        text-align: left;
                        padding: 8px;
                        vertical-align: top;
                    }}
                    th {{
                        width: 150px;
                        color: #555;
                    }}
                    .footer {{
                        margin-top: 30px;
                        font-size: 12px;
                        color: #888;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>New Help Ticket Submitted</h2>
                    <p><strong>{submission.user.get_full_name()}</strong> ({submission.user.email}) has submitted a new help ticket.</p>

                    <table>
                        <tr>
                            <th>Reference ID:</th>
                            <td>{submission.form_id}</td>
                        </tr>
                        <tr>
                            <th>Location:</th>
                            <td>{submission.location}</td>
                        </tr>
                        <tr>
                            <th>Date Started:</th>
                            <td>{submission.date_submitted.strftime('%Y-%m-%d')}</td>
                        </tr>
                        <tr>
                            <th>Subject:</th>
                            <td>{submission.subject}</td>
                        </tr>
                    </table>

                    <p class="footer">
                        This is an automated message. You can view this ticket in the admin panel.
                    </p>
                </div>
            </body>
            </html>
            """

            # Strip tags for plain text fallback
            plain_text = strip_tags(html_content)

            email = EmailMessage(
                subject="New HELP Ticket Submitted",
                body=plain_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=recipients,
            )
            email.content_subtype = "html"
            email.body = html_content
            email.send(fail_silently=False)

            return redirect('helpdesk:it_help_list')

        else:
            print(form.errors)
    else:
        form = HELPSubmissionForm()

    context = {'form':form, 'users': users}

    return render(request, 'ticket_others.html', context)


@login_required(login_url='app:login')
@allowed_users(allowed_roles=['admin'])
def it_help_list(request):
    start_date = None
    end_date = None
    status = None

    # Get the date range parameters from the request
    if 'startDate' in request.GET and 'endDate' in request.GET:
        start_date = request.GET.get('startDate')
        end_date = request.GET.get('endDate')
    
    # Parse the dates if they exist
    start_date = parse_date(start_date) if start_date else None
    end_date = parse_date(end_date) if end_date else None
    status = request.GET.get('status', None)

    report_data = []

    help_submissions = HELPForm.objects.all()

    if start_date or end_date:
        if start_date and end_date:
            help_submissions = help_submissions.filter(date_submitted__range=[start_date, end_date])
        elif start_date:
            help_submissions = help_submissions.filter(date_submitted__gte=start_date)
        elif end_date:
            help_submissions = help_submissions.filter(date_submitted__lte=end_date)

    if status:
        help_submissions = help_submissions.filter(status=status)

    # Process the filtered submissions
    for submission in help_submissions:
        report_data.append({
            'form_id': submission.id,
            'id': submission.form_id,
            'location': submission.location,
            'date_submitted': submission.date_submitted.strftime('%Y-%m-%d'),
            'complaint': submission.complaint,
            'issue': submission.issue,
            'subject': submission.subject,
            'status': submission.status,
            'user': submission.user,  
        })

    return render(request, 'it_list_ticket.html', {
        'start_date': start_date,
        'end_date': end_date,
        'status': status,  # Add the selected status to the context
        'total_help': len(help_submissions) if report_data else 0,
        'report_data': report_data,
    })

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['admin'])
def admin_dash(request):
    
    return render(request, 'admin_dash.html', )


@login_required(login_url='app:login')
def ticket_detail(request, pk):
    # Fetch the ticket by form_id
    ticket = get_object_or_404(HELPForm, pk=pk)

    if request.user.groups.filter(name='admin').exists(): 
        if ticket.status == 'pending':
            ticket.status = 'in_progress'
            ticket.save()

    # Render the template and pass the ticket details to it
    return render(request, 'ticket_detail.html', {'ticket': ticket})



@login_required(login_url='app:login')
def close_complainant(request, pk):
    submission = get_object_or_404(HELPForm, pk=pk)

    if request.user.groups.filter(name='admin').exists(): 
        submission.status = 'closed' 
        submission.save()
        return redirect('helpdesk:it_help_list')
    else:
        submission.status = 'closed_by_complainant'
        submission.save()  
    return redirect('helpdesk:help_list')


@login_required(login_url='app:login')
@allowed_users(allowed_roles=['admin'])
def admin_reply_ticket(request, pk):
    ticket = get_object_or_404(HELPForm, pk=pk)
    
    # If the user is an admin, allow them to respond
    if request.user.is_staff:
        if request.method == "POST":
            form = AdminResponseForm(request.POST, instance=ticket)
            if form.is_valid():
                response = form.save(commit=False)
                response.status = 'resolved'  # set status to resolved
                response.save()
                messages.success(request, 'Response saved successfully.')

                recipients = [response.user.email]

                # Construct the inline HTML email
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            background-color: #f9f9f9;
                            padding: 20px;
                            color: #333;
                        }}
                        .container {{
                            background-color: #ffffff;
                            border-radius: 8px;
                            padding: 20px;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                        }}
                        h2 {{
                            color: #007bff;
                            margin-bottom: 20px;
                        }}
                        table {{
                            width: 100%;
                            border-collapse: collapse;
                        }}
                        th, td {{
                            text-align: left;
                            padding: 8px;
                            vertical-align: top;
                        }}
                        th {{
                            width: 150px;
                            color: #555;
                        }}
                        .footer {{
                            margin-top: 30px;
                            font-size: 12px;
                            color: #888;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h2>Your Ticket Has Been Resolved</h2>
                        <p><strong>{response.user.get_full_name()}</strong> ({response.user.email}), your ticket has been resolved.</p>

                        <table>
                            <tr>
                                <th>Reference ID:</th>
                                <td>{response.form_id}</td>
                            </tr>
                            <tr>
                                <th>Location:</th>
                                <td>{response.location}</td>
                            </tr>
                            <tr>
                                <th>Date Started:</th>
                                <td>{response.date_submitted.strftime('%Y-%m-%d')}</td>
                            </tr>
                            <tr>
                                <th>Subject:</th>
                                <td>{response.subject}</td>
                            </tr>
                        </table>

                        <p class="footer">
                            This is an automated message. You can view this ticket in the admin panel.
                        </p>
                    </div>
                </body>
                </html>
                """

                # Strip tags for plain text fallback
                plain_text = strip_tags(html_content)

                email = EmailMessage(
                    subject="HELP Ticket Resolved",
                    body=plain_text,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=recipients,
                )
                email.content_subtype = "html"
                email.body = html_content
                email.send(fail_silently=False)

                return redirect('helpdesk:it_help_list')
        else:
            form = AdminResponseForm(instance=ticket)
        
        return render(request, 'admin_reply_ticket.html', {'form': form, 'ticket': ticket})

    else:
        messages.error(request, 'You do not have permission to respond to this ticket.')
        return redirect('helpdesk:it_help_list')

@login_required(login_url='app:login')
def rate_ticket_response(request, pk):
    ticket = get_object_or_404(HELPForm, pk=pk)

    # Check if the user is the one who submitted the ticket
    if ticket.user != request.user:
        messages.error(request, 'You are not authorized to rate this ticket.')
        return redirect('helpdesk:help_list')  # Or redirect to the list of tickets

    # If ticket is resolved or closed, allow the user to rate it
    if ticket.status in ['resolved', 'closed']:
        if request.method == 'POST':
            form = UserRatingForm(request.POST, instance=ticket)
            if form.is_valid():
                form.save()
                messages.success(request, 'Thank you for your feedback!')
                return redirect('helpdesk:ticket_detail', pk=ticket.pk)
        else:
            form = UserRatingForm(instance=ticket)

        return render(request, 'rate_ticket.html', {'form': form, 'ticket': ticket})
    else:
        messages.error(request, 'You cannot rate a ticket that is still in progress.')
        return redirect('helpdesk:help_list')


@login_required(login_url='app:login')
@allowed_users(allowed_roles=['admin'])
def report_page(request):
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    status = request.GET.get('status')

    # Parse and normalize dates
    start_date = parse_date(start_date) if start_date else None
    end_date = parse_date(end_date) if end_date else None

    if start_date:
        start_date = datetime.combine(start_date, datetime.min.time())
    if end_date:
        end_date = datetime.combine(end_date, datetime.max.time())
    

    # Start with all forms
    help_submissions = HELPForm.objects.all()

    # Filter by date range
    if start_date and end_date:
        help_submissions = help_submissions.filter(date_submitted__range=(start_date, end_date))
    elif start_date:
        help_submissions = help_submissions.filter(date_submitted__gte=start_date)
    elif end_date:
        help_submissions = help_submissions.filter(date_submitted__lte=end_date)

    if status:
        help_submissions = help_submissions.filter(status=status)

    # Get the report data
    report_data = [{
        'form_id': submission.form_id,
        'location': submission.location,
        'date_submitted': submission.date_submitted.strftime('%Y-%m-%d'),
        'complaint': submission.complaint,
        'priority': submission.priority.name,  # Assuming Priority has a 'name' field
        'status': submission.status,
    } for submission in help_submissions]

    # Get the count of each priority and status for pie chart
    priority_counts = help_submissions.values('priority__name').annotate(count=Count('priority')).order_by('priority__name')
    status_counts = help_submissions.values('status').annotate(count=Count('status')).order_by('status')

    # Prepare the data for the chart
    priority_labels = [item['priority__name'] for item in priority_counts]
    priority_values = [item['count'] for item in priority_counts]
    status_labels = [item['status'] for item in status_counts]
    status_values = [item['count'] for item in status_counts]

    if 'export' in request.GET:
        return export_to_excel(request, help_submissions)

    if 'download_pdf' in request.GET:
        if not help_submissions.exists():
            return HttpResponse('<h1>No data available in selected date range.</h1>')
        return export_to_pdf(request, help_submissions)

    return render(request, 'report_page.html', {
        'start_date': start_date.date() if start_date else '',
        'end_date': end_date.date() if end_date else '',
        'status': status,
        'report_data': report_data,
        'priority_labels': priority_labels,
        'priority_values': priority_values,
        'status_labels': status_labels,
        'status_values': status_values,
    })



@login_required(login_url='app:login')
@allowed_users(allowed_roles=['admin'])
def export_to_excel(request, help_submissions):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Ticket Report'

    headers = [
        'S/N', 'Ticket ID', 'Location', 'Date Submitted', 'Time Submitted',
        'Date Resolved', 'Time Resolved', 'Complainant Name', 'Subject',
        'Category', 'Priority', 'Reply', 'Status', 'Duration'
    ]
    worksheet.append(headers)

    for sn, submission in enumerate(help_submissions, start=1):
        date_submitted = submission.date_submitted.strftime('%Y-%m-%d')
        time_submitted = submission.date_submitted.strftime('%H:%M:%S')

        date_resolved = submission.response_timestamp.strftime('%Y-%m-%d') if submission.response_timestamp else ""
        time_resolved = submission.response_timestamp.strftime('%H:%M:%S') if submission.response_timestamp else ""

        complainant_name = submission.user.get_full_name() if submission.user else "Anonymous"

        duration = ""
        if submission.date_submitted and submission.response_timestamp:
            delta = submission.response_timestamp - submission.date_submitted
            hours, remainder = divmod(delta.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            duration = f"{int(hours)} hours {int(minutes)} minutes"

        row = [
            sn,
            submission.form_id,
            submission.location,
            date_submitted,
            time_submitted,
            date_resolved,
            time_resolved,
            complainant_name,
            submission.subject,
            submission.category.name if submission.category else "",
            submission.priority.name if submission.priority else "",
            submission.admin_response,
            submission.status,
            duration
        ]
        worksheet.append(row)

    # Get dates from request to use in the filename
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')

    # Fallbacks if dates aren't present
    start_str = start_date if start_date else 'Start'
    end_str = end_date if end_date else 'Today'

    # Format for file-safe naming (optional: replace spaces or special characters)
    status_label = request.GET.get('status') or 'All Statuses'
    filename = f"List Of Tickets From {start_str} To {end_str} - {status_label}.xlsx"
    filename = filename.replace(" ", "_")  # Optional: make it filesystem friendly

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    workbook.save(response)
    return response

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['admin'])
def export_to_pdf(request, help_submissions):
    # Count priority and status
    priority_counts = help_submissions.values('priority__name').annotate(count=Count('priority')).order_by('priority__name')
    status_counts = help_submissions.values('status').annotate(count=Count('status')).order_by('status')

    priority_labels = [item['priority__name'] for item in priority_counts]
    priority_values = [item['count'] for item in priority_counts]

    status_labels = [item['status'] for item in status_counts]
    status_values = [item['count'] for item in status_counts]

    # Priority pie chart
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(priority_values, labels=priority_labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    priority_img = io.BytesIO()
    plt.savefig(priority_img, format='png')
    plt.close(fig)
    priority_img.seek(0)

    # Status pie chart
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(status_values, labels=status_labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    status_img = io.BytesIO()
    plt.savefig(status_img, format='png')
    plt.close(fig)
    status_img.seek(0)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ticket_report.pdf"'

    pdf = canvas.Canvas(response, pagesize=letter)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, 750, "HELP Ticket Report - Priority and Status Distribution")

    # Draw Priority Chart
    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 700, "Priority Distribution:")
    img = Image(priority_img)
    img.drawHeight = 300
    img.drawWidth = 400
    img.wrapOn(pdf, 400, 300)
    img.drawOn(pdf, 100, 400)

    # Draw Status Chart
    pdf.drawString(100, 380, "Status Distribution:")
    img = Image(status_img)
    img.drawHeight = 300
    img.drawWidth = 400
    img.wrapOn(pdf, 400, 300)
    img.drawOn(pdf, 100, 80)

    pdf.showPage()
    pdf.save()
    return response