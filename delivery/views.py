from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@login_required
def delivery_requests(request):
    """View delivery requests"""
    if request.user.user_type != 'delivery':
        messages.error(request, 'Access denied. Delivery partner account required.')
        return redirect('accounts:login')
    
    from .models import DeliveryRequest
    
    # Get delivery requests for this delivery partner
    delivery_requests = DeliveryRequest.objects.filter(
        delivery_partner=request.user
    ).select_related(
        'order', 'vendor'
    ).prefetch_related(
        'order__items__product', 
        'order__items__supplier'
    ).order_by('-created_at')
    
    return render(request, 'delivery/requests.html', {
        'delivery_requests': delivery_requests
    })

@login_required
def delivery_request_detail(request, request_id):
    """View individual delivery request detail"""
    from .models import DeliveryRequest
    
    try:
        delivery_request = get_object_or_404(DeliveryRequest, id=request_id)
        
        # Check if user has permission to view this request
        if delivery_request.delivery_partner != request.user and delivery_request.vendor != request.user and not request.user.is_staff:
            messages.error(request, 'You do not have permission to view this delivery request.')
            return redirect('core:home')
        
        context = {
            'delivery_request': delivery_request,
            'order': delivery_request.order,
            'order_items': delivery_request.order.items.select_related('product', 'supplier').all(),
        }
        return render(request, 'delivery/request_detail.html', context)
        
    except DeliveryRequest.DoesNotExist:
        messages.error(request, 'Delivery request not found.')
        return redirect('delivery:requests')

@login_required
def add_availability(request):
    """Add delivery availability"""
    if request.user.user_type != 'delivery':
        messages.error(request, 'Access denied. Delivery partner account required.')
        return redirect('accounts:login')
    
    from .models import DeliveryAvailability
    
    # Get or create availability record
    availability, created = DeliveryAvailability.objects.get_or_create(
        delivery_partner=request.user
    )
    
    if request.method == 'POST':
        try:
            # Update availability data
            availability.current_latitude = request.POST.get('current_latitude')
            availability.current_longitude = request.POST.get('current_longitude')
            availability.price_per_kg = request.POST.get('price_per_kg', 0)
            availability.max_weight_capacity = request.POST.get('max_weight_capacity', 50)
            availability.availability_radius = request.POST.get('availability_radius', 10)
            availability.estimated_delivery_time = request.POST.get('estimated_delivery_time', '2-4 hours')
            availability.description = request.POST.get('description', '')
            availability.normal_container_available = 'normal_container_available' in request.POST
            availability.cold_container_available = 'cold_container_available' in request.POST
            availability.cold_container_extra_charge = request.POST.get('cold_container_extra_charge', 0)
            availability.is_available = 'is_available' in request.POST
            
            availability.save()
            
            # Also update delivery profile availability
            if hasattr(request.user, 'delivery_profile'):
                request.user.delivery_profile.is_available = availability.is_available
                request.user.delivery_profile.save()
            
            # Create notification for vendors in the area
            if availability.is_available:
                try:
                    from notifications.services import NotificationService
                    from accounts.models import User
                    
                    # Get all vendors in the area (simplified - you can add location-based filtering)
                    vendors = User.objects.filter(user_type='vendor', is_active=True)[:10]  # Limit to prevent spam
                    
                    for vendor in vendors:
                        NotificationService.create_notification(
                            recipient=vendor,
                            sender=request.user,
                            notification_type='availability_update',
                            title=f'{request.user.first_name or request.user.username} is now available',
                            message=f'Delivery partner {request.user.first_name} {request.user.last_name} is now available for deliveries in your area. Price: ₹{availability.price_per_kg}/kg',
                            priority='low'
                        )
                except Exception as e:
                    print(f"Failed to create availability notifications: {e}")
            
            messages.success(request, 'Delivery availability updated successfully!')
            return redirect('core:delivery_home')
            
        except Exception as e:
            messages.error(request, f'Error updating availability: {str(e)}')
    
    return render(request, 'delivery/add_availability.html', {
        'availability': availability
    })

@login_required
@csrf_exempt
def toggle_availability(request):
    """Toggle delivery partner availability"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            is_available = data.get('is_available', False)
            
            if hasattr(request.user, 'delivery_profile'):
                request.user.delivery_profile.is_available = is_available
                request.user.delivery_profile.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'message': 'Delivery profile not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def get_requests(request):
    """Get delivery requests for the partner"""
    if request.user.user_type != 'delivery':
        return JsonResponse({'success': False, 'message': 'Access denied'})
    
    # For now, return empty requests - this will be implemented with actual delivery request models
    return JsonResponse({
        'success': True,
        'requests': []
    })

@login_required
@csrf_exempt
def accept_request(request, request_id):
    """Accept a delivery request"""
    if request.method == 'POST':
        try:
            from .models import DeliveryRequest
            
            delivery_request = DeliveryRequest.objects.get(
                id=request_id,
                delivery_partner=request.user,
                status='pending'
            )
            
            delivery_request.status = 'accepted'
            delivery_request.save()
            
            # Update order status
            delivery_request.order.status = 'confirmed'
            delivery_request.order.save()
            
            # Create notifications
            try:
                from notifications.services import NotificationService
                
                # Notify vendor that delivery request was accepted
                NotificationService.create_notification(
                    recipient=delivery_request.vendor,
                    sender=request.user,
                    notification_type='delivery_accepted',
                    content_object=delivery_request,
                    priority='medium',
                    action_url=f'/delivery/requests/{delivery_request.id}/'
                )
                
                # Notify vendor that order was confirmed
                NotificationService.create_notification(
                    recipient=delivery_request.vendor,
                    notification_type='order_confirmed',
                    content_object=delivery_request.order,
                    priority='medium',
                    action_url=f'/orders/{delivery_request.order.id}/'
                )
                
            except Exception as e:
                print(f"Failed to create notifications: {e}")
            
            return JsonResponse({
                'success': True, 
                'message': f'Delivery request for Order #{delivery_request.order.order_number} accepted!'
            })
        except DeliveryRequest.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Delivery request not found or already processed'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
@csrf_exempt
def reject_request(request, request_id):
    """Reject a delivery request"""
    if request.method == 'POST':
        try:
            from .models import DeliveryRequest
            
            delivery_request = DeliveryRequest.objects.get(
                id=request_id,
                delivery_partner=request.user,
                status='pending'
            )
            
            delivery_request.status = 'rejected'
            delivery_request.save()
            
            # Update order status
            delivery_request.order.status = 'cancelled'
            delivery_request.order.save()
            
            # Create notifications
            try:
                from notifications.services import NotificationService
                
                # Notify vendor that delivery request was rejected
                NotificationService.create_notification(
                    recipient=delivery_request.vendor,
                    sender=request.user,
                    notification_type='delivery_rejected',
                    content_object=delivery_request,
                    priority='high',
                    action_url=f'/delivery/requests/{delivery_request.id}/'
                )
                
                # Notify vendor that order was cancelled
                NotificationService.create_notification(
                    recipient=delivery_request.vendor,
                    notification_type='order_cancelled',
                    content_object=delivery_request.order,
                    priority='high',
                    action_url=f'/orders/{delivery_request.order.id}/'
                )
                
            except Exception as e:
                print(f"Failed to create notifications: {e}")
            
            return JsonResponse({
                'success': True, 
                'message': f'Delivery request for Order #{delivery_request.order.order_number} rejected'
            })
        except DeliveryRequest.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Delivery request not found or already processed'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
@csrf_exempt
def update_location(request):
    """Update delivery partner location"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            
            if latitude and longitude:
                request.user.latitude = latitude
                request.user.longitude = longitude
                request.user.is_active_location = True
                request.user.save()
                
                if hasattr(request.user, 'delivery_profile'):
                    request.user.delivery_profile.current_latitude = latitude
                    request.user.delivery_profile.current_longitude = longitude
                    request.user.delivery_profile.save()
                
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid coordinates'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})
