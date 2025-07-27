from .models import DeliveryNotification

def notification_context(request):
    """Add notification context to all templates"""
    context = {
        'unread_notifications_count': 0,
        'has_unread_notifications': False,
    }
    
    if request.user.is_authenticated:
        unread_count = DeliveryNotification.objects.filter(
            recipient=request.user, 
            is_read=False
        ).count()
        
        context.update({
            'unread_notifications_count': unread_count,
            'has_unread_notifications': unread_count > 0,
        })
    
    return context