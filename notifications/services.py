from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.template import Template, Context
from .models import Notification, NotificationTemplate, NotificationPreference
from accounts.models import User

class NotificationService:
    """Service class for creating and managing notifications"""
    
    @staticmethod
    def create_notification(
        recipient,
        notification_type,
        title=None,
        message=None,
        sender=None,
        content_object=None,
        action_url=None,
        priority='medium',
        metadata=None
    ):
        """
        Create a new notification
        
        Args:
            recipient: User who will receive the notification
            notification_type: Type of notification (from NOTIFICATION_TYPES)
            title: Custom title (optional, will use template if not provided)
            message: Custom message (optional, will use template if not provided)
            sender: User who triggered the notification (optional)
            content_object: Related object (Order, DeliveryRequest, etc.)
            action_url: URL to redirect when notification is clicked
            priority: Priority level (low, medium, high, urgent)
            metadata: Additional data as dict
        """
        
        # Get or create notification preferences for recipient
        preferences, created = NotificationPreference.objects.get_or_create(
            user=recipient
        )
        
        # Check if user wants this type of notification
        if not NotificationService._should_send_notification(preferences, notification_type):
            return None
        
        # Use template if title/message not provided
        if not title or not message:
            template_title, template_message = NotificationService._get_template_content(
                notification_type, content_object, sender, recipient
            )
            title = title or template_title
            message = message or template_message
        
        # Generate action URL if not provided
        if not action_url and content_object:
            action_url = NotificationService._generate_action_url(content_object)
        
        # Create the notification
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            title=title,
            message=message,
            priority=priority,
            content_object=content_object,
            action_url=action_url,
            metadata=metadata or {}
        )
        
        return notification
    
    @staticmethod
    def _should_send_notification(preferences, notification_type):
        """Check if user wants to receive this type of notification"""
        # Map notification types to preference fields
        preference_map = {
            'order_placed': 'inapp_order_updates',
            'order_confirmed': 'inapp_order_updates',
            'order_shipped': 'inapp_order_updates',
            'order_delivered': 'inapp_order_updates',
            'order_cancelled': 'inapp_order_updates',
            'delivery_request': 'inapp_delivery_updates',
            'delivery_accepted': 'inapp_delivery_updates',
            'delivery_rejected': 'inapp_delivery_updates',
            'delivery_completed': 'inapp_delivery_updates',
            'availability_update': 'inapp_delivery_updates',
            'payment_received': 'inapp_payment_updates',
            'payment_failed': 'inapp_payment_updates',
            'group_buying_started': 'inapp_group_buying',
            'group_buying_joined': 'inapp_group_buying',
            'group_buying_completed': 'inapp_group_buying',
            'system_announcement': 'inapp_system_announcements',
            'profile_update': 'inapp_system_announcements',
            'verification_complete': 'inapp_system_announcements',
        }
        
        preference_field = preference_map.get(notification_type, 'inapp_system_announcements')
        return getattr(preferences, preference_field, True)
    
    @staticmethod
    def _get_template_content(notification_type, content_object=None, sender=None, recipient=None):
        """Get title and message from template"""
        try:
            template = NotificationTemplate.objects.get(
                notification_type=notification_type,
                is_active=True
            )
            
            # Prepare context for template rendering
            context_data = {
                'recipient_name': recipient.first_name or recipient.username if recipient else '',
                'sender_name': sender.first_name or sender.username if sender else '',
            }
            
            # Add content object specific data
            if content_object:
                if hasattr(content_object, 'order_number'):
                    context_data['order_number'] = content_object.order_number
                if hasattr(content_object, 'id'):
                    context_data['object_id'] = content_object.id
                if hasattr(content_object, 'total_amount'):
                    context_data['amount'] = content_object.total_amount
            
            # Render templates
            title_template = Template(template.title_template)
            message_template = Template(template.message_template)
            context = Context(context_data)
            
            title = title_template.render(context)
            message = message_template.render(context)
            
            return title, message
            
        except NotificationTemplate.DoesNotExist:
            # Fallback to default messages
            return NotificationService._get_default_content(notification_type)
    
    @staticmethod
    def _get_default_content(notification_type):
        """Get default title and message for notification type"""
        defaults = {
            'order_placed': ('New Order Placed', 'Your order has been placed successfully.'),
            'order_confirmed': ('Order Confirmed', 'Your order has been confirmed.'),
            'order_shipped': ('Order Shipped', 'Your order has been shipped.'),
            'order_delivered': ('Order Delivered', 'Your order has been delivered.'),
            'order_cancelled': ('Order Cancelled', 'Your order has been cancelled.'),
            'delivery_request': ('New Delivery Request', 'You have a new delivery request.'),
            'delivery_accepted': ('Delivery Accepted', 'Your delivery request has been accepted.'),
            'delivery_rejected': ('Delivery Rejected', 'Your delivery request has been rejected.'),
            'delivery_completed': ('Delivery Completed', 'Delivery has been completed.'),
            'availability_update': ('Availability Updated', 'Delivery partner availability has been updated.'),
            'payment_received': ('Payment Received', 'Payment has been received.'),
            'payment_failed': ('Payment Failed', 'Payment has failed.'),
            'group_buying_started': ('Group Buying Started', 'A new group buying session has started.'),
            'group_buying_joined': ('Someone Joined', 'Someone joined your group buying session.'),
            'group_buying_completed': ('Group Buying Completed', 'Group buying session has been completed.'),
            'system_announcement': ('System Announcement', 'New system announcement.'),
            'profile_update': ('Profile Update', 'Please update your profile.'),
            'verification_complete': ('Verification Complete', 'Your account has been verified.'),
        }
        
        return defaults.get(notification_type, ('Notification', 'You have a new notification.'))
    
    @staticmethod
    def _generate_action_url(content_object):
        """Generate action URL based on content object type"""
        try:
            if hasattr(content_object, 'order_number'):
                # Order object
                return reverse('orders:detail', kwargs={'order_number': content_object.order_number})
            elif hasattr(content_object, 'delivery_requests'):
                # DeliveryRequest object
                return reverse('delivery:request_detail', kwargs={'pk': content_object.id})
            elif content_object.__class__.__name__ == 'GroupBuyingSession':
                return reverse('groupbuying:session_detail', kwargs={'pk': content_object.id})
        except:
            pass
        
        return None
    
    @staticmethod
    def mark_as_read(notification_id, user):
        """Mark a notification as read"""
        try:
            notification = Notification.objects.get(id=notification_id, recipient=user)
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False
    
    @staticmethod
    def mark_all_as_read(user):
        """Mark all notifications as read for a user"""
        Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)
    
    @staticmethod
    def get_unread_count(user):
        """Get count of unread notifications for a user"""
        return Notification.objects.filter(recipient=user, is_read=False).count()
    
    @staticmethod
    def get_recent_notifications(user, limit=10):
        """Get recent notifications for a user"""
        return Notification.objects.filter(recipient=user)[:limit]
    
    @staticmethod
    def delete_old_notifications(days=30):
        """Delete notifications older than specified days"""
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count = Notification.objects.filter(created_at__lt=cutoff_date).delete()[0]
        return deleted_count

# Convenience functions for common notification types
def notify_order_placed(order, recipient=None):
    """Create notification for order placed"""
    recipient = recipient or order.user
    if recipient:
        return NotificationService.create_notification(
            recipient=recipient,
            notification_type='order_placed',
            content_object=order,
            priority='medium'
        )

def notify_delivery_request(delivery_request):
    """Create notification for new delivery request"""
    return NotificationService.create_notification(
        recipient=delivery_request.delivery_partner,
        sender=delivery_request.vendor,
        notification_type='delivery_request',
        content_object=delivery_request,
        priority='high'
    )

def notify_delivery_status_change(delivery_request, status):
    """Create notification for delivery status change"""
    notification_types = {
        'accepted': 'delivery_accepted',
        'rejected': 'delivery_rejected',
        'delivered': 'delivery_completed'
    }
    
    notification_type = notification_types.get(status)
    if notification_type:
        return NotificationService.create_notification(
            recipient=delivery_request.vendor,
            sender=delivery_request.delivery_partner,
            notification_type=notification_type,
            content_object=delivery_request,
            priority='medium'
        )

def notify_availability_update(delivery_partner, vendors_in_area):
    """Create notifications for delivery partner availability update"""
    notifications = []
    for vendor in vendors_in_area:
        notification = NotificationService.create_notification(
            recipient=vendor,
            sender=delivery_partner,
            notification_type='availability_update',
            title=f"{delivery_partner.first_name} is now available for delivery",
            message=f"Delivery partner {delivery_partner.first_name} {delivery_partner.last_name} is now available in your area.",
            priority='low'
        )
        if notification:
            notifications.append(notification)
    return notifications