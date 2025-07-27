from django.db import models
from django.conf import settings
from orders.models import Order

class DeliveryRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='delivery_requests')
    delivery_partner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='delivery_requests',
        limit_choices_to={'user_type': 'delivery'}
    )
    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_delivery_requests',
        limit_choices_to={'user_type': 'vendor'}
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    pickup_address = models.TextField()
    delivery_address = models.TextField()
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    actual_delivery_time = models.DateTimeField(null=True, blank=True)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Delivery Request #{self.id} - {self.order.id} - {self.status}"

class DeliveryAvailability(models.Model):
    delivery_partner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='availability',
        limit_choices_to={'user_type': 'delivery'}
    )
    is_available = models.BooleanField(default=False)
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_location_update = models.DateTimeField(auto_now=True)
    availability_radius = models.IntegerField(default=10)  # in kilometers
    
    # Pricing and capacity information
    price_per_kg = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    max_weight_capacity = models.DecimalField(max_digits=8, decimal_places=2, default=50.00)  # in kg
    estimated_delivery_time = models.CharField(max_length=50, default="2-4 hours")
    
    # Container options
    normal_container_available = models.BooleanField(default=True)
    cold_container_available = models.BooleanField(default=False)
    cold_container_extra_charge = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    # Additional info
    description = models.TextField(blank=True, help_text="Brief description of services")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.delivery_partner.username} - {'Available' if self.is_available else 'Not Available'}"

class DeliveryNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('availability_update', 'Availability Update'),
        ('new_request', 'New Delivery Request'),
        ('request_accepted', 'Request Accepted'),
        ('request_rejected', 'Request Rejected'),
        ('delivery_completed', 'Delivery Completed'),
    ]
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='delivery_notifications'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_delivery_notifications',
        null=True,
        blank=True
    )
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
