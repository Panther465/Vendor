from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Cart, CartItem, Product, Supplier, Order, OrderItem, DeliveryAddress
import json
from decimal import Decimal
import razorpay
from django.conf import settings
import hmac
import hashlib

def get_or_create_cart(request):
    """Get or create cart for user or session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart

def order_list(request):
    """Orders listing page - shows all orders for admin or user's orders"""
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            # Admin can see all orders
            orders = Order.objects.all().order_by('-created_at')
        else:
            # Regular users see only their orders
            orders = Order.objects.filter(user=request.user).order_by('-created_at')
        
        has_orders = orders.exists()
    else:
        orders = []
        has_orders = False
    
    context = {
        'orders': orders,
        'has_orders': has_orders,
    }
    return render(request, 'orders.html', context)

def create_order(request):
    """Create new order"""
    if request.method == 'POST':
        # Handle order creation logic
        pass
    return render(request, 'create_order.html')

@login_required
def order_detail(request, order_id):
    """Individual order detail page"""
    try:
        order = get_object_or_404(Order, id=order_id)
        
        # Check if user has permission to view this order
        if order.user != request.user and not request.user.is_staff:
            messages.error(request, 'You do not have permission to view this order.')
            return redirect('core:home')
        
        order_items = order.items.select_related('product', 'supplier').all()
        
        context = {
            'order': order,
            'order_items': order_items,
        }
        return render(request, 'orders/order_detail.html', context)
        
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('core:home')

def cart_view(request):
    """Shopping cart page"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product', 'product__supplier').all()
    
    # Get available delivery partners
    from delivery.models import DeliveryAvailability
    available_partners = DeliveryAvailability.objects.filter(
        is_available=True,
        delivery_partner__user_type='delivery'
    ).select_related('delivery_partner', 'delivery_partner__delivery_profile')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_items': cart.total_items,
        'subtotal': cart.subtotal,
        'available_partners': available_partners,
    }
    return render(request, 'cart.html', context)

@csrf_exempt
def add_to_cart(request):
    """Add item to cart via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Get or create supplier
            supplier_data = data.get('supplier', {})
            supplier, created = Supplier.objects.get_or_create(
                place_id=supplier_data.get('place_id', f"temp_{supplier_data.get('name', 'unknown')}"),
                defaults={
                    'name': supplier_data.get('name', 'Unknown Supplier'),
                    'address': supplier_data.get('address', ''),
                    'phone': supplier_data.get('phone', ''),
                    'rating': float(supplier_data.get('rating', 0)),
                    'latitude': float(supplier_data.get('latitude', 0)),
                    'longitude': float(supplier_data.get('longitude', 0)),
                }
            )
            
            # Get or create product
            product_data = data.get('product', {})
            product, created = Product.objects.get_or_create(
                supplier=supplier,
                name=product_data.get('name'),
                defaults={
                    'price': Decimal(str(product_data.get('price', 0))),
                    'unit': product_data.get('unit', 'kg'),
                    'category': product_data.get('category', 'general'),
                    'description': product_data.get('description', ''),
                    'image_url': product_data.get('image_url', ''),
                }
            )
            
            # Get or create cart
            cart = get_or_create_cart(request)
            
            # Add or update cart item
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': int(data.get('quantity', 1))}
            )
            
            if not created:
                cart_item.quantity += int(data.get('quantity', 1))
                cart_item.save()
            
            return JsonResponse({
                'success': True,
                'message': f'{product.name} added to cart!',
                'cart_count': cart.total_items,
                'item_total': float(cart_item.total_price)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error adding to cart: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def update_cart_item(request):
    """Update cart item quantity"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart = get_or_create_cart(request)
            
            cart_item = get_object_or_404(CartItem, 
                cart=cart, 
                id=data.get('item_id')
            )
            
            new_quantity = int(data.get('quantity', 1))
            if new_quantity <= 0:
                cart_item.delete()
                message = 'Item removed from cart'
            else:
                cart_item.quantity = new_quantity
                cart_item.save()
                message = 'Cart updated'
            
            return JsonResponse({
                'success': True,
                'message': message,
                'cart_count': cart.total_items,
                'subtotal': float(cart.subtotal)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating cart: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def remove_from_cart(request):
    """Remove item from cart"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart = get_or_create_cart(request)
            
            cart_item = get_object_or_404(CartItem, 
                cart=cart, 
                id=data.get('item_id')
            )
            
            product_name = cart_item.product.name
            cart_item.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'{product_name} removed from cart',
                'cart_count': cart.total_items,
                'subtotal': float(cart.subtotal)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error removing from cart: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def get_cart_count(request):
    """Get current cart count"""
    cart = get_or_create_cart(request)
    return JsonResponse({
        'cart_count': cart.total_items,
        'subtotal': float(cart.subtotal)
    })

@login_required
@csrf_exempt
def checkout_view(request):
    """Checkout page with payment options"""
    # Get address_id from URL parameter
    address_id = request.GET.get('address_id')
    if not address_id:
        messages.error(request, 'Please select a delivery address')
        return redirect('orders:delivery_address')
    
    try:
        address = DeliveryAddress.objects.get(id=address_id, user=request.user)
    except DeliveryAddress.DoesNotExist:
        messages.error(request, 'Invalid delivery address')
        return redirect('orders:delivery_address')
    
    cart = get_or_create_cart(request)
    if not cart.items.exists():
        messages.error(request, 'Your cart is empty')
        return redirect('orders:cart')
    
    # Calculate totals
    subtotal = cart.subtotal
    delivery_fee = Decimal('50.00')  # Fixed delivery fee for now
    gst_amount = (subtotal + delivery_fee) * Decimal('0.18')  # 18% GST
    total_amount = subtotal + delivery_fee + gst_amount
    
    from django.conf import settings
    
    context = {
        'address': address,
        'cart_items': cart.items.all(),
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'gst_amount': gst_amount,
        'total_amount': total_amount,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    }
    
    return render(request, 'orders/payment.html', context)

def process_old_checkout(request):
    """Handle old checkout flow - keeping for backward compatibility"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart = get_or_create_cart(request)
            
            if not cart.items.exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Cart is empty'
                })
            
            # Get delivery partner
            delivery_partner_id = data.get('delivery_partner_id')
            container_type = data.get('container_type', 'normal')
            delivery_address = data.get('delivery_address', '')
            
            if not delivery_partner_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Please select a delivery partner'
                })
            
            from delivery.models import DeliveryAvailability
            from accounts.models import User
            
            try:
                delivery_availability = DeliveryAvailability.objects.get(
                    id=delivery_partner_id,
                    is_available=True
                )
                delivery_partner = delivery_availability.delivery_partner
            except DeliveryAvailability.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Selected delivery partner is not available'
                })
            
            # Calculate totals
            subtotal = cart.subtotal
            container_extra = 0
            if container_type == 'cold' and delivery_availability.cold_container_available:
                container_extra = delivery_availability.cold_container_extra_charge
            
            # Calculate delivery fee based on total weight
            total_weight = sum(item.quantity for item in cart.items.all())  # Assuming quantity is in kg
            delivery_fee = (delivery_availability.price_per_kg * total_weight) + container_extra
            
            gst = subtotal * Decimal('0.18')  # 18% GST
            total_amount = subtotal + delivery_fee + gst
            
            with transaction.atomic():
                # Create order
                order = Order.objects.create(
                    user=request.user,
                    customer_name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                    customer_email=request.user.email,
                    customer_phone=getattr(request.user, 'phone', ''),
                    delivery_address=delivery_address or f"Lat: {request.user.latitude}, Lng: {request.user.longitude}",
                    delivery_partner=f"{delivery_partner.first_name} {delivery_partner.last_name}".strip() or delivery_partner.username,
                    delivery_fee=delivery_fee,
                    container_type=container_type,
                    subtotal=subtotal,
                    gst=gst,
                    total_amount=total_amount,
                    status='pending'
                )
                
                # Create order items
                for cart_item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        supplier=cart_item.product.supplier,
                        quantity=cart_item.quantity,
                        unit_price=cart_item.product.price,
                        total_price=cart_item.total_price
                    )
                
                # Create delivery request
                from delivery.models import DeliveryRequest
                
                delivery_request = DeliveryRequest.objects.create(
                    order=order,
                    delivery_partner=delivery_partner,
                    vendor=request.user,
                    pickup_address=f"Vendor Location - {request.user.username}",
                    delivery_address=delivery_address or "Customer Location",
                    pickup_latitude=request.user.latitude,
                    pickup_longitude=request.user.longitude,
                    delivery_latitude=request.user.latitude,  # For now, same as pickup
                    delivery_longitude=request.user.longitude,
                    delivery_fee=delivery_fee,
                    notes=f"Container type: {container_type}, Total weight: {total_weight}kg",
                    status='pending'
                )
                
                # Clear cart
                cart.items.all().delete()
                
                # Create notifications
                try:
                    from notifications.services import NotificationService
                    
                    # Notification for the vendor (order placed)
                    NotificationService.create_notification(
                        recipient=request.user,
                        notification_type='order_placed',
                        content_object=order,
                        priority='medium',
                        action_url=f'/orders/{order.id}/'
                    )
                    
                    # Notification for the delivery partner (new delivery request)
                    NotificationService.create_notification(
                        recipient=delivery_partner,
                        sender=request.user,
                        notification_type='delivery_request',
                        content_object=delivery_request,
                        priority='high',
                        action_url=f'/delivery/requests/{delivery_request.id}/'
                    )
                    
                except Exception as e:
                    # Don't fail the order if notification creation fails
                    print(f"Failed to create notifications: {e}")
                
                return JsonResponse({
                    'success': True,
                    'message': 'Order placed successfully!',
                    'order_id': order.id,
                    'order_number': order.order_number,
                    'delivery_request_id': delivery_request.id
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error processing order: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def delivery_address_view(request):
    """Delivery address selection/creation page"""
    saved_addresses = DeliveryAddress.objects.filter(user=request.user)
    
    context = {
        'saved_addresses': saved_addresses,
    }
    
    return render(request, 'orders/delivery_address.html', context)

@login_required
def save_address(request):
    """Save new delivery address"""
    if request.method == 'POST':
        try:
            address = DeliveryAddress.objects.create(
                user=request.user,
                address_type=request.POST.get('address_type', 'home'),
                full_name=request.POST.get('full_name'),
                phone=request.POST.get('phone'),
                address_line_1=request.POST.get('address_line_1'),
                address_line_2=request.POST.get('address_line_2', ''),
                city=request.POST.get('city'),
                state=request.POST.get('state'),
                pincode=request.POST.get('pincode'),
                landmark=request.POST.get('landmark', ''),
                delivery_instructions=request.POST.get('delivery_instructions', ''),
                is_default=not DeliveryAddress.objects.filter(user=request.user).exists()  # First address is default
            )
            
            messages.success(request, 'Address saved successfully!')
            return redirect(f'/orders/checkout/?address_id={address.id}')
            
        except Exception as e:
            messages.error(request, f'Error saving address: {str(e)}')
            return redirect('orders:delivery_address')
    
    return redirect('orders:delivery_address')

@login_required
def edit_address(request, address_id):
    """Edit delivery address"""
    address = get_object_or_404(DeliveryAddress, id=address_id, user=request.user)
    
    if request.method == 'POST':
        try:
            address.address_type = request.POST.get('address_type', address.address_type)
            address.full_name = request.POST.get('full_name', address.full_name)
            address.phone = request.POST.get('phone', address.phone)
            address.address_line_1 = request.POST.get('address_line_1', address.address_line_1)
            address.address_line_2 = request.POST.get('address_line_2', address.address_line_2)
            address.city = request.POST.get('city', address.city)
            address.state = request.POST.get('state', address.state)
            address.pincode = request.POST.get('pincode', address.pincode)
            address.landmark = request.POST.get('landmark', address.landmark)
            address.delivery_instructions = request.POST.get('delivery_instructions', address.delivery_instructions)
            address.save()
            
            messages.success(request, 'Address updated successfully!')
            return redirect('orders:delivery_address')
            
        except Exception as e:
            messages.error(request, f'Error updating address: {str(e)}')
    
    context = {
        'address': address,
        'is_edit': True,
    }
    
    return render(request, 'orders/delivery_address.html', context)

@login_required
def delete_address(request, address_id):
    """Delete delivery address"""
    if request.method == 'POST':
        try:
            address = get_object_or_404(DeliveryAddress, id=address_id, user=request.user)
            address.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
@csrf_exempt
def create_razorpay_order(request):
    """Create Razorpay order"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = float(data.get('amount'))
            address_id = data.get('address_id')
            
            # Initialize Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            # Create Razorpay order
            razorpay_order = client.order.create({
                'amount': int(amount * 100),  # Amount in paise
                'currency': 'INR',
                'payment_capture': 1
            })
            
            return JsonResponse({
                'success': True,
                'order_id': razorpay_order['id'],
                'amount': amount
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
@csrf_exempt
def verify_payment(request):
    """Verify Razorpay payment and create order"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            razorpay_order_id = data.get('razorpay_order_id')
            razorpay_payment_id = data.get('razorpay_payment_id')
            razorpay_signature = data.get('razorpay_signature')
            address_id = data.get('address_id')
            
            # Verify signature
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            # Verify signature
            try:
                client.utility.verify_payment_signature(params_dict)
            except:
                return JsonResponse({
                    'success': False,
                    'message': 'Payment signature verification failed'
                })
            
            # Create order
            order = create_order_from_cart(request, address_id, 'razorpay', {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
            
            return JsonResponse({
                'success': True,
                'order_id': order.id,
                'order_number': order.order_number
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
@csrf_exempt
def process_payment(request):
    """Process COD payment"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            payment_method = data.get('payment_method')
            address_id = data.get('address_id')
            
            if payment_method == 'cod':
                order = create_order_from_cart(request, address_id, 'cod')
                
                return JsonResponse({
                    'success': True,
                    'order_id': order.id,
                    'order_number': order.order_number
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid payment method'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def create_order_from_cart(request, address_id, payment_method, payment_data=None):
    """Helper function to create order from cart"""
    cart = get_or_create_cart(request)
    address = DeliveryAddress.objects.get(id=address_id, user=request.user)
    
    # Calculate totals
    subtotal = cart.subtotal
    delivery_fee = Decimal('50.00')
    gst_amount = (subtotal + delivery_fee) * Decimal('0.18')
    total_amount = subtotal + delivery_fee + gst_amount
    
    with transaction.atomic():
        # Create order
        order = Order.objects.create(
            user=request.user,
            customer_name=address.full_name,
            customer_email=request.user.email,
            customer_phone=address.phone,
            delivery_address=f"{address.address_line_1}, {address.address_line_2}, {address.city}, {address.state} {address.pincode}",
            delivery_partner="To be assigned",
            delivery_fee=delivery_fee,
            subtotal=subtotal,
            gst=gst_amount,
            total_amount=total_amount,
            payment_method=payment_method,
            payment_status='paid' if payment_method == 'razorpay' else 'pending'
        )
        
        # Add payment data if provided
        if payment_data:
            order.razorpay_order_id = payment_data.get('razorpay_order_id')
            order.razorpay_payment_id = payment_data.get('razorpay_payment_id')
            order.razorpay_signature = payment_data.get('razorpay_signature')
            order.save()
        
        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
        
        # Clear cart
        cart.items.all().delete()
        
        return order

def order_success(request, order_id):
    """Order success page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    
    return render(request, 'orders/success.html', context)

@login_required
def my_orders_view(request):
    """Display user's order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
        'has_orders': orders.exists(),
    }
    
    return render(request, 'orders/my_orders.html', context)
