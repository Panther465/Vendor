from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Notification, NotificationPreference
from .services import NotificationService
import json

@login_required
def notification_list(request):
    """Display list of notifications for the current user"""
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    
    # Filter by type if specified
    notification_type = request.GET.get('type')
    if notification_type and notification_type != 'all':
        notifications = notifications.filter(notification_type=notification_type)
    
    # Filter by read status
    status = request.GET.get('status')
    if status == 'unread':
        notifications = notifications.filter(is_read=False)
    elif status == 'read':
        notifications = notifications.filter(is_read=True)
    
    # Get notification types for filter dropdown
    notification_types = Notification.objects.filter(recipient=request.user).values_list('notification_type', flat=True).distinct()
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'unread_count': NotificationService.get_unread_count(request.user),
        'current_type': notification_type,
        'current_status': status,
        'notification_types': notification_types,
    }
    
    return render(request, 'notifications/list.html', context)

@login_required
def notification_detail(request, notification_id):
    """Display notification detail and mark as read"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    
    # Mark as read
    notification.mark_as_read()
    
    # If there's an action URL, redirect to it
    if notification.action_url:
        return redirect(notification.action_url)
    
    context = {
        'notification': notification,
    }
    
    return render(request, 'notifications/detail.html', context)

@login_required
@require_POST
def mark_as_read(request, notification_id):
    """Mark a notification as read via AJAX"""
    success = NotificationService.mark_as_read(notification_id, request.user)
    
    return JsonResponse({
        'success': success,
        'unread_count': NotificationService.get_unread_count(request.user)
    })

@login_required
@require_POST
def mark_all_as_read(request):
    """Mark all notifications as read via AJAX"""
    NotificationService.mark_all_as_read(request.user)
    
    return JsonResponse({
        'success': True,
        'unread_count': 0
    })

@login_required
def get_notifications_json(request):
    """Get notifications as JSON for AJAX requests"""
    limit = int(request.GET.get('limit', 10))
    notifications = NotificationService.get_recent_notifications(request.user, limit)
    
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.notification_type,
            'priority': notification.priority,
            'is_read': notification.is_read,
            'created_at': notification.created_at.isoformat(),
            'action_url': notification.action_url,
            'icon': notification.get_icon(),
            'color_class': notification.get_color_class(),
        })
    
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': NotificationService.get_unread_count(request.user)
    })

@login_required
def notification_preferences(request):
    """Manage notification preferences"""
    preferences, created = NotificationPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update preferences
        for field in ['email_order_updates', 'email_delivery_updates', 'email_payment_updates',
                     'email_group_buying', 'email_system_announcements',
                     'push_order_updates', 'push_delivery_updates', 'push_payment_updates',
                     'push_group_buying', 'push_system_announcements',
                     'inapp_order_updates', 'inapp_delivery_updates', 'inapp_payment_updates',
                     'inapp_group_buying', 'inapp_system_announcements']:
            setattr(preferences, field, field in request.POST)
        
        preferences.save()
        messages.success(request, 'Notification preferences updated successfully.')
        return redirect('notifications:preferences')
    
    context = {
        'preferences': preferences,
    }
    
    return render(request, 'notifications/preferences.html', context)

@login_required
def delete_notification(request, notification_id):
    """Delete a notification"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    
    if request.method == 'POST':
        notification.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'unread_count': NotificationService.get_unread_count(request.user)
            })
        messages.success(request, 'Notification deleted successfully.')
        return redirect('notifications:list')
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
@require_POST
def delete_all_notifications(request):
    """Delete all notifications for the current user"""
    deleted_count = Notification.objects.filter(recipient=request.user).count()
    Notification.objects.filter(recipient=request.user).delete()
    
    return JsonResponse({
        'success': True,
        'deleted_count': deleted_count,
        'unread_count': 0
    })

@login_required
def notification_popup(request):
    """Get notifications for popup display"""
    notifications = NotificationService.get_recent_notifications(request.user, 5)
    unread_count = NotificationService.get_unread_count(request.user)
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    
    return render(request, 'notifications/popup.html', context)
