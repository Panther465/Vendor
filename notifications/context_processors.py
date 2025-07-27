from .services import NotificationService

def notification_context(request):
    """Add notification context to all templates"""
    if request.user.is_authenticated:
        unread_count = NotificationService.get_unread_count(request.user)
        recent_notifications = NotificationService.get_recent_notifications(request.user, 5)
        
        return {
            'unread_notifications_count': unread_count,
            'has_unread_notifications': unread_count > 0,
            'recent_notifications': recent_notifications,
        }
    
    return {
        'unread_notifications_count': 0,
        'has_unread_notifications': False,
        'recent_notifications': [],
    }