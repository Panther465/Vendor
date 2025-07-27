from django import template
from delivery.models import DeliveryNotification

register = template.Library()

@register.simple_tag
def unread_notifications_count(user):
    """Get count of unread delivery notifications for a user"""
    if user.is_authenticated:
        return DeliveryNotification.objects.filter(recipient=user, is_read=False).count()
    return 0

@register.simple_tag
def has_unread_notifications(user):
    """Check if user has unread delivery notifications"""
    if user.is_authenticated:
        return DeliveryNotification.objects.filter(recipient=user, is_read=False).exists()
    return False