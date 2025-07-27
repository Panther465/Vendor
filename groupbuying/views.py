from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import json

from .models import (
    GroupBuyingProfile, GroupBuyingItem, GroupBuyingRequest,
    GroupBuyingSession, GroupCart, GroupCartItem
)
from accounts.models import User

@login_required
def group_buying_home(request):
    """Main group buying dashboard"""
    if request.user.user_type != 'vendor':
        messages.error(request, 'Access denied. Vendor account required.')
        return redirect('accounts:login')
    
    # Get or create group buying profile
    profile, created = GroupBuyingProfile.objects.get_or_create(
        vendor=request.user,
        defaults={
            'business_name': f"{request.user.first_name}'s Business",
            'business_phone': '',
            'business_address': '',
        }
    )
    
    # Get nearby vendors with group buying enabled
    nearby_vendors = GroupBuyingProfile.objects.filter(
        is_enabled=True
    ).exclude(vendor=request.user).select_related('vendor')
    
    # Get sent and received requests
    sent_requests = GroupBuyingRequest.objects.filter(
        sender=request.user
    ).select_related('receiver').order_by('-created_at')
    
    received_requests = GroupBuyingRequest.objects.filter(
        receiver=request.user
    ).select_related('sender').order_by('-created_at')
    
    context = {
        'profile': profile,
        'nearby_vendors': nearby_vendors,
        'sent_requests': sent_requests,
        'received_requests': received_requests,
    }
    
    return render(request, 'groupbuying/home.html', context)

@login_required
def setup_profile(request):
    """Setup or edit group buying profile"""
    if request.user.user_type != 'vendor':
        messages.error(request, 'Access denied. Vendor account required.')
        return redirect('accounts:login')
    
    profile, created = GroupBuyingProfile.objects.get_or_create(
        vendor=request.user,
        defaults={
            'business_name': f"{request.user.first_name}'s Business",
            'business_phone': '',
            'business_address': '',
        }
    )
    
    if request.method == 'POST':
        try:
            profile.is_enabled = 'is_enabled' in request.POST
            profile.business_name = request.POST.get('business_name', '')
            profile.business_phone = request.POST.get('business_phone', '')
            profile.business_address = request.POST.get('business_address', '')
            profile.max_group_size = int(request.POST.get('max_group_size', 5))
            profile.preferred_radius = int(request.POST.get('preferred_radius', 10))
            profile.discrete_delivery_enabled = 'discrete_delivery_enabled' in request.POST
            
            profile.save()
            
            messages.success(request, 'Group buying profile updated successfully!')
            return redirect('groupbuying:home')
            
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
    
    return render(request, 'groupbuying/setup_profile.html', {'profile': profile})

@login_required
def manage_items(request):
    """Manage group buying items"""
    if request.user.user_type != 'vendor':
        messages.error(request, 'Access denied. Vendor account required.')
        return redirect('accounts:login')
    
    profile = get_object_or_404(GroupBuyingProfile, vendor=request.user)
    items = GroupBuyingItem.objects.filter(profile=profile).order_by('-created_at')
    
    if request.method == 'POST':
        try:
            action = request.POST.get('action')
            
            if action == 'delete':
                item_id = request.POST.get('item_id')
                item = get_object_or_404(GroupBuyingItem, id=item_id, profile=profile)
                item.delete()
                messages.success(request, 'Item deleted successfully!')
            else:
                GroupBuyingItem.objects.create(
                    profile=profile,
                    item_name=request.POST.get('item_name', ''),
                    category=request.POST.get('category', ''),
                    estimated_quantity=request.POST.get('estimated_quantity', ''),
                    description=request.POST.get('description', ''),
                    priority=request.POST.get('priority', 'medium')
                )
                messages.success(request, 'Item added successfully!')
            
            return redirect('groupbuying:manage_items')
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'groupbuying/manage_items.html', {
        'profile': profile,
        'items': items
    })

@login_required
@csrf_exempt
def send_request(request, vendor_id):
    """Send group buying request to another vendor"""
    if request.method == 'POST':
        try:
            receiver = get_object_or_404(User, id=vendor_id, user_type='vendor')
            
            # Check if request already exists
            existing_request = GroupBuyingRequest.objects.filter(
                sender=request.user,
                receiver=receiver
            ).first()
            
            if existing_request:
                return JsonResponse({
                    'success': False,
                    'message': 'Request already sent to this vendor'
                })
            
            # Create new request
            group_request = GroupBuyingRequest.objects.create(
                sender=request.user,
                receiver=receiver,
                message=request.POST.get('message', '')
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Group buying request sent to {receiver.first_name}!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
@csrf_exempt
def handle_request(request, request_id, action):
    """Accept or decline group buying request"""
    if request.method == 'POST':
        try:
            group_request = get_object_or_404(
                GroupBuyingRequest,
                id=request_id,
                receiver=request.user,
                status='pending'
            )
            
            if action == 'accept':
                group_request.status = 'accepted'
                message = f'Group buying request from {group_request.sender.first_name} accepted!'
            elif action == 'decline':
                group_request.status = 'declined'
                message = f'Group buying request from {group_request.sender.first_name} declined.'
            else:
                return JsonResponse({'success': False, 'message': 'Invalid action'})
            
            group_request.save()
            
            return JsonResponse({
                'success': True,
                'message': message
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def start_group_session(request):
    """Start a new group buying session"""
    if request.user.user_type != 'vendor':
        messages.error(request, 'Access denied. Vendor account required.')
        return redirect('accounts:login')
    
    if request.method == 'POST':
        try:
            # Get accepted partners
            partner_ids = request.POST.getlist('partners')
            partners = User.objects.filter(id__in=partner_ids, user_type='vendor')
            
            # Create group session
            session = GroupBuyingSession.objects.create(
                creator=request.user,
                session_name=request.POST.get('session_name', f"Group Session {request.user.first_name}"),
                use_discrete_delivery='use_discrete_delivery' in request.POST,
                main_delivery_address=request.POST.get('main_delivery_address', '')
            )
            
            # Add participants
            session.participants.add(request.user)
            session.participants.add(*partners)
            
            # Create group cart
            GroupCart.objects.create(session=session)
            
            messages.success(request, 'Group buying session started!')
            return redirect('groupbuying:group_suppliers', session_id=session.id)
            
        except Exception as e:
            messages.error(request, f'Error starting session: {str(e)}')
    
    # Get accepted requests for partner selection
    accepted_requests = GroupBuyingRequest.objects.filter(
        Q(sender=request.user, status='accepted') |
        Q(receiver=request.user, status='accepted')
    ).select_related('sender', 'receiver')
    
    return render(request, 'groupbuying/start_session.html', {
        'accepted_requests': accepted_requests
    })

@login_required
def group_suppliers(request, session_id):
    """Group buying suppliers page"""
    session = get_object_or_404(GroupBuyingSession, id=session_id)
    
    # Check if user is participant
    if not session.participants.filter(id=request.user.id).exists():
        messages.error(request, 'You are not a participant in this group session.')
        return redirect('groupbuying:home')
    
    # This will redirect to suppliers list with group buying mode
    return redirect(f'/suppliers/?group_session={session_id}')

@login_required
def group_cart(request, session_id):
    """Group buying cart"""
    session = get_object_or_404(GroupBuyingSession, id=session_id)
    
    # Check if user is participant
    if not session.participants.filter(id=request.user.id).exists():
        messages.error(request, 'You are not a participant in this group session.')
        return redirect('groupbuying:home')
    
    cart = get_object_or_404(GroupCart, session=session)
    
    context = {
        'session': session,
        'cart': cart,
        'is_group_buying': True,
    }
    
    return render(request, 'groupbuying/cart.html', context)

@login_required
def vendor_details(request, vendor_id):
    """Get vendor details for modal display"""
    try:
        vendor = get_object_or_404(User, id=vendor_id, user_type='vendor')
        profile = get_object_or_404(GroupBuyingProfile, vendor=vendor, is_enabled=True)
        
        # Get vendor's buying items
        items = GroupBuyingItem.objects.filter(profile=profile)
        
        vendor_data = {
            'success': True,
            'vendor': {
                'business_name': profile.business_name,
                'owner_name': f"{vendor.first_name} {vendor.last_name}",
                'business_phone': profile.business_phone,
                'email': vendor.email,
                'business_address': profile.business_address,
                'max_group_size': profile.max_group_size,
                'preferred_radius': profile.preferred_radius,
                'discrete_delivery_enabled': profile.discrete_delivery_enabled,
                'items': [
                    {
                        'name': item.item_name,
                        'quantity': item.estimated_quantity,
                        'category': item.category,
                        'priority': item.get_priority_display()
                    }
                    for item in items
                ]
            }
        }
        
        return JsonResponse(vendor_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })