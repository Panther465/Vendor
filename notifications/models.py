from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('order_placed', 'Order Placed'),
        ('order_confirmed', 'Order Confirmed'),
        ('order_shipped', 'Order Shipped'),
        ('order_delivered', 'Order Delivered'),
        ('order_cancelled', 'Order Cancelled'),
        ('delivery_request', 'New Delivery Request'),
        ('delivery_accepted', 'Delivery Request Accepted'),
        ('delivery_rejected', 'Delivery Request Rejected'),
        ('delivery_completed', 'Delivery Completed'),
        ('availability_update', 'Delivery Partner Availability Update'),
        ('payment_received', 'Payment Received'),
        ('payment_failed', 'Payment Failed'),
        ('group_buying_started', 'Group Buying Session Started'),
        ('group_buying_joined', 'Someone Joined Your Group Buying'),
        ('group_buying_completed', 'Group Buying Session Completed'),
        ('system_announcement', 'System Announcement'),
        ('profile_update', 'Profile Update Required'),
        ('verification_complete', 'Account Verification Complete'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        null=True,
        blank=True
    )
    
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Generic foreign key to link to any model (Order, DeliveryRequest, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Action URL for when notification is clicked
    action_url = models.URLField(blank=True, null=True)
    
    # Status fields
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['recipient', 'created_at']),
            models.Index(fields=['notification_type']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def get_icon(self):
        """Return appropriate icon based on notification type"""
        icon_map = {
            'order_placed': 'fas fa-shopping-cart',
            'order_confirmed': 'fas fa-check-circle',
            'order_shipped': 'fas fa-truck',
            'order_delivered': 'fas fa-box-open',
            'order_cancelled': 'fas fa-times-circle',
            'delivery_request': 'fas fa-motorcycle',
            'delivery_accepted': 'fas fa-thumbs-up',
            'delivery_rejected': 'fas fa-thumbs-down',
            'delivery_completed': 'fas fa-check-double',
            'availability_update': 'fas fa-map-marker-alt',
            'payment_received': 'fas fa-credit-card',
            'payment_failed': 'fas fa-exclamation-triangle',
            'group_buying_started': 'fas fa-users',
            'group_buying_joined': 'fas fa-user-plus',
            'group_buying_completed': 'fas fa-handshake',
            'system_announcement': 'fas fa-bullhorn',
            'profile_update': 'fas fa-user-edit',
            'verification_complete': 'fas fa-shield-alt',
        }
        return icon_map.get(self.notification_type, 'fas fa-bell')
    
    def get_color_class(self):
        """Return CSS class based on priority"""
        color_map = {
            'low': 'notification-low',
            'medium': 'notification-medium',
            'high': 'notification-high',
            'urgent': 'notification-urgent',
        }
        return color_map.get(self.priority, 'notification-medium')

class NotificationPreference(models.Model):
    """User preferences for notifications"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Email notifications
    email_order_updates = models.BooleanField(default=True)
    email_delivery_updates = models.BooleanField(default=True)
    email_payment_updates = models.BooleanField(default=True)
    email_group_buying = models.BooleanField(default=True)
    email_system_announcements = models.BooleanField(default=True)
    
    # Push notifications (for future mobile app)
    push_order_updates = models.BooleanField(default=True)
    push_delivery_updates = models.BooleanField(default=True)
    push_payment_updates = models.BooleanField(default=True)
    push_group_buying = models.BooleanField(default=True)
    push_system_announcements = models.BooleanField(default=False)
    
    # In-app notifications
    inapp_order_updates = models.BooleanField(default=True)
    inapp_delivery_updates = models.BooleanField(default=True)
    inapp_payment_updates = models.BooleanField(default=True)
    inapp_group_buying = models.BooleanField(default=True)
    inapp_system_announcements = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification Preferences - {self.user.username}"

class NotificationTemplate(models.Model):
    """Templates for different types of notifications"""
    notification_type = models.CharField(max_length=30, choices=Notification.NOTIFICATION_TYPES, unique=True)
    title_template = models.CharField(max_length=200)
    message_template = models.TextField()
    
    # Template variables help text
    variables_help = models.TextField(
        blank=True,
        help_text="Available variables for this template (e.g., {user_name}, {order_id})"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Template: {self.get_notification_type_display()}"
