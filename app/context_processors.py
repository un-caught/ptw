from django.contrib.auth.models import Group
from app.models import PTWForm, NHISForm, Notification
from helpdesk.models import HELPForm

def user_groups(request):
    # Ensure the user is authenticated before querying the database
    if request.user.is_authenticated:
        # Count of 'approved' PTWForms created by the logged-in user
        approved_count = PTWForm.objects.filter(status='approved', user=request.user).count()
        open_count = NHISForm.objects.filter(status__in=['awaiting_supervisor', 'awaiting_manager'], user=request.user).count()
        closed_count = NHISForm.objects.filter(status='closed', user=request.user).count()

        #  supervisor page
        total_ptw = PTWForm.objects.all().count()
        total_nhis = NHISForm.objects.all().count()
        approved_ptw = PTWForm.objects.filter(status='approved').count()
        closed_nhis = NHISForm.objects.filter(status='closed').count()
        disapproved_ptw = PTWForm.objects.filter(status='disapproved').count()
        denied_nhis = NHISForm.objects.filter(status='denied').count()
        pending_ptw = PTWForm.objects.filter(status__in=['awaiting_supervisor', 'awaiting_manager']).count()
        pending_nhis = NHISForm.objects.filter(status__in=['awaiting_supervisor', 'awaiting_manager']).count()


        # mannager
        pending_ptw_manager = PTWForm.objects.filter(status='awaiting_manager').count()
        pending_nhis_manager = NHISForm.objects.filter(status='awaiting_manager').count()

        user_tickets = HELPForm.objects.filter(user=request.user).count()
        user_tickets_progress = HELPForm.objects.filter(status='in_progress', user=request.user).count()
        user_tickets_closed = HELPForm.objects.filter(status='resolved', user=request.user).count()
        user_tickets_cbc = HELPForm.objects.filter(status='closed_by_complainant', user=request.user).count()

        admin_tickets = HELPForm.objects.all().count()
        admin_tickets_progress = HELPForm.objects.filter(status='in_progress').count()
        admin_tickets_closed = HELPForm.objects.filter(status='resolved').count()
        admin_tickets_cbc = HELPForm.objects.filter(status='closed_by_complainant').count()


        # Count of 'pending' or other similar statuses for the logged-in user
        pend_count = PTWForm.objects.filter(
            status__in=['awaiting_supervisor', 'awaiting_manager'],
            user=request.user
        ).count()

        # Group checks
        is_supervisor = request.user.groups.filter(name="supervisor").exists()
        is_manager = request.user.groups.filter(name="manager").exists()
        is_staff = request.user.groups.filter(name="staff").exists()
        is_vendor = request.user.groups.filter(name="vendor").exists()
        is_admin = request.user.groups.filter(name="admin").exists()
        is_hr = request.user.groups.filter(name="hr").exists()
        is_em = request.user.groups.filter(name="em").exists()

        unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    else:
        # For unauthenticated users, return default values
        approved_count = 0
        open_count = 0
        closed_count = 0
        pend_count = 0
        is_staff = False
        is_vendor = False
        is_supervisor = False
        is_manager = False
        is_admin = False
        is_hr = False
        is_em = False
        total_ptw = 0
        total_nhis = 0
        approved_ptw = 0
        closed_nhis = 0
        disapproved_ptw = 0
        denied_nhis = 0
        pending_ptw = 0
        pending_nhis = 0
        pending_ptw_manager = 0
        pending_nhis_manager = 0
        unread_count = 0
        user_tickets = 0
        user_tickets_progress = 0
        user_tickets_closed = 0
        user_tickets_cbc = 0
        admin_tickets = 0
        admin_tickets_progress = 0
        admin_tickets_closed = 0
        admin_tickets_cbc = 0

        
        


    # Return the context dictionary
    return {
        'is_staff': is_staff,
        'is_vendor': is_vendor,
        'is_supervisor': is_supervisor,
        'is_manager': is_manager,
        'is_admin': is_admin,
        'is_hr': is_hr,
        'is_em': is_em,
        'approved_count': approved_count,
        'pend_count': pend_count,
        'open_count': open_count,
        'closed_count': closed_count,
        'total_ptw': total_ptw,
        'total_nhis': total_nhis,
        'approved_ptw': approved_ptw,
        'closed_nhis': closed_nhis,
        'disapproved_ptw': disapproved_ptw,
        'denied_nhis': denied_nhis,
        'pending_ptw': pending_ptw,
        'pending_nhis': pending_nhis,
        'pending_ptw_manager': pending_ptw_manager,
        'pending_nhis_manager': pending_nhis_manager,
        'unread_count': unread_count,
        'user_tickets': user_tickets,
        'user_tickets_progress': user_tickets_progress,
        'user_tickets_closed': user_tickets_closed,
        'user_tickets_cbc': user_tickets_cbc,
        'admin_tickets': admin_tickets,
        'admin_tickets_progress': admin_tickets_progress,
        'admin_tickets_closed': admin_tickets_closed,
        'admin_tickets_cbc': admin_tickets_cbc,
        'section': request.GET.get('section')
    }