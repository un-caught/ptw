# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from django.utils import timezone
from .models import Notification

@receiver(post_save, sender=Notification)
def delete_old_notifications(sender, instance, created, **kwargs):
    """
    Deletes notifications older than 30 days.
    This will trigger every time a Notification instance is saved.
    """
    if created:  # Only run cleanup when a new notification is created
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        # Delete notifications older than 30 days
        old_notifications = Notification.objects.filter(timestamp__lt=thirty_days_ago)
        old_notifications.delete()
