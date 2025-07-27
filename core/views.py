from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def vendor_home(request):
    """Vendor home page view"""
    if request.user.user_type != 'vendor':
        messages.error(request, 'Access denied. Vendor account required.')
        return redirect('accounts:login')
    return render(request, 'vendor/home.html')

@login_required
def delivery_home(request):
    """Delivery partner home page view"""
    if request.user.user_type != 'delivery':
        messages.error(request, 'Access denied. Delivery partner account required.')
        return redirect('accounts:login')
    return render(request, 'delivery/home.html')

@login_required
def vendor_dashboard(request):
    """Vendor dashboard with analytics and quick actions"""
    if request.user.user_type != 'vendor':
        messages.error(request, 'Access denied. Vendor account required.')
        return redirect('accounts:login')
    
    # Get vendor statistics
    from orders.models import Order
    from notifications.models import Notification
    
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    total_orders = Order.objects.filter(user=request.user).count()
    pending_orders = Order.objects.filter(user=request.user, status='pending').count()
    recent_notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:5]
    
    context = {
        'recent_orders': recent_orders,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'recent_notifications': recent_notifications,
    }
    return render(request, 'vendor/dashboard.html', context)

@login_required
def delivery_dashboard(request):
    """Delivery partner dashboard with analytics and quick actions"""
    if request.user.user_type != 'delivery':
        messages.error(request, 'Access denied. Delivery partner account required.')
        return redirect('accounts:login')
    
    # Get delivery partner statistics
    from delivery.models import DeliveryRequest, DeliveryAvailability
    from notifications.models import Notification
    
    recent_requests = DeliveryRequest.objects.filter(delivery_partner=request.user).order_by('-created_at')[:5]
    total_deliveries = DeliveryRequest.objects.filter(delivery_partner=request.user, status='completed').count()
    pending_requests = DeliveryRequest.objects.filter(delivery_partner=request.user, status='pending').count()
    recent_notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:5]
    
    # Get availability status
    try:
        availability = DeliveryAvailability.objects.get(delivery_partner=request.user)
    except DeliveryAvailability.DoesNotExist:
        availability = None
    
    context = {
        'recent_requests': recent_requests,
        'total_deliveries': total_deliveries,
        'pending_requests': pending_requests,
        'recent_notifications': recent_notifications,
        'availability': availability,
    }
    return render(request, 'delivery/dashboard.html', context)

def popup_demo(request):
    """Demo page for themed popup system"""
    return render(request, 'popup-demo.html')

def contact_us(request):
    """Contact Us page"""
    if request.method == 'POST':
        # Handle contact form submission
        # For now, we'll just show a success message
        # In a real implementation, you'd save to database or send email
        messages.success(request, 'Thank you for your message! We will get back to you within 2-4 hours.')
        return redirect('core:contact_us')
    
    return render(request, 'contactus.html')

def about_us(request):
    """About Us page"""
    return render(request, 'aboutus.html')
