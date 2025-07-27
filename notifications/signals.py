from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from orders.models import Order
from delivery.models import DeliveryRequest, DeliveryAvailability
from accounts.models import User
from .services import (
    NotificationService, 
    notify_order_placed, 
    notify_delivery_request, 
    notify_delivery_status_change,
    notify_availability_update
)

@receiver(post_save, sender=Order)
def create_order_notification(sender, instance, created, **kwargs):
    """Create notification when order is placed or status changes"""
    if created:
        # Order placed notification
        notify_order_placed(instance)
    else:
        # Order status change notification
        if instance.status in ['confirmed', 'shipped', 'delivered', 'cancelled']:
            notification_type = f'order_{instance.status}'
            NotificationService.create_notification(
                recipient=instance.user,
                notification_type=notification_type,
                content_object=instance,
                priority='medium'
            )

@receiver(post_save, sender=DeliveryRequest)
def create_delivery_request_notification(sender, instance, created, **kwargs):
    """Create notification when delivery request is created or updated"""
    if created:
        # New delivery request notification to delivery partner
        notify_delivery_request(instance)
    else:
        # Status change notification to vendor
        if hasattr(instance, '_status_changed'):
            notify_delivery_status_change(instance, instance.status)

@receiver(pre_save, sender=DeliveryRequest)
def track_delivery_status_change(sender, instance, **kwargs):
    """Track status changes in delivery requests"""
    if instance.pk:
        try:
            old_instance = DeliveryRequest.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                instance._status_changed = True
        except DeliveryRequest.DoesNotExist:
            pass

@receiver(post_save, sender=DeliveryAvailability)
def create_availability_notification(sender, instance, created, **kwargs):
    """Create notification when delivery partner updates availability"""
    if instance.is_available:
        # Find vendors in the area (simplified - you can implement proper geolocation)
        vendors_in_area = User.objects.filter(
            user_type='vendor',
            is_active=True
        )[:10]  # Limit to prevent spam
        
        notify_availability_update(instance.delivery_partner, vendors_in_area)