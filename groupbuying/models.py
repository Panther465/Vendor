from django.db import models
from django.conf import settings
from orders.models import Product, Supplier

class GroupBuyingProfile(models.Model):
    """Vendor's group buying profile and preferences"""
    vendor = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='group_buying_profile',
        limit_choices_to={'user_type': 'vendor'}
    )
    is_enabled = models.BooleanField(default=False, help_text="Enable group buying for this vendor")
    business_name = models.CharField(max_length=255)
    business_phone = models.CharField(max_length=20)
    business_address = models.TextField()
    business_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    business_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Group buying preferences
    max_group_size = models.PositiveIntegerField(default=5, help_text="Maximum vendors in a group")
    preferred_radius = models.PositiveIntegerField(default=10, help_text="Preferred radius in km")
    discrete_delivery_enabled = models.BooleanField(default=False, help_text="Allow separate delivery addresses")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.business_name} - Group Buying"

class GroupBuyingItem(models.Model):
    """Items that a vendor wants to buy in group"""
    profile = models.ForeignKey(GroupBuyingProfile, on_delete=models.CASCADE, related_name='buying_items')
    item_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    estimated_quantity = models.CharField(max_length=100, help_text="e.g., 50kg, 100 pieces")
    description = models.TextField(blank=True)
    priority = models.CharField(
        max_length=20,
        choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')],
        default='medium'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.item_name} - {self.profile.business_name}"

class GroupBuyingRequest(models.Model):
    """Requests between vendors for group buying"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]
    
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_group_requests'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_group_requests'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True)
    items_interested = models.ManyToManyField(GroupBuyingItem, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('sender', 'receiver')
    
    def __str__(self):
        return f"Request from {self.sender.username} to {self.receiver.username}"

class GroupBuyingSession(models.Model):
    """Active group buying session"""
    SESSION_STATUS = [
        ('active', 'Active'),
        ('shopping', 'Shopping'),
        ('checkout', 'Checkout'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_group_sessions'
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='group_sessions'
    )
    session_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=SESSION_STATUS, default='active')
    
    # Delivery preferences
    use_discrete_delivery = models.BooleanField(default=False)
    main_delivery_address = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Group Session: {self.session_name}"

class GroupCart(models.Model):
    """Group buying cart"""
    session = models.OneToOneField(GroupBuyingSession, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())
    
    @property
    def group_discount(self):
        """10% discount for group buying"""
        return self.subtotal * 0.10
    
    @property
    def total_after_discount(self):
        return self.subtotal - self.group_discount
    
    def __str__(self):
        return f"Group Cart - {self.session.session_name}"

class GroupCartItem(models.Model):
    """Items in group cart"""
    cart = models.ForeignKey(GroupCart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Individual delivery address if discrete delivery is enabled
    delivery_address = models.TextField(blank=True)
    delivery_phone = models.CharField(max_length=20, blank=True)
    
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('cart', 'product', 'added_by')
    
    @property
    def total_price(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} by {self.added_by.username}"