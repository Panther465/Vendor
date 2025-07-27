from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from .models import User, VendorProfile, DeliveryPartnerProfile

def login_view(request):
    """Login page view"""
    if request.user.is_authenticated:
        if request.user.user_type == 'vendor':
            return redirect('core:vendor_home')
        elif request.user.user_type == 'delivery':
            return redirect('core:delivery_home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        if not latitude or not longitude:
            messages.error(request, 'Please capture your current location before logging in.')
            return render(request, 'login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.user_type == user_type:
                # Update user location
                user.latitude = latitude
                user.longitude = longitude
                user.is_active_location = True
                user.save()
                
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                
                if user_type == 'vendor':
                    return redirect('core:vendor_home')
                elif user_type == 'delivery':
                    return redirect('core:delivery_home')
            else:
                messages.error(request, f'This account is not registered as a {user_type}.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')

def signup_view(request):
    """Signup page view"""
    if request.user.is_authenticated:
        if request.user.user_type == 'vendor':
            return redirect('core:vendor_home')
        elif request.user.user_type == 'delivery':
            return redirect('core:delivery_home')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Basic user data
                username = request.POST.get('username')
                email = request.POST.get('email')
                password = request.POST.get('password')
                confirm_password = request.POST.get('confirm_password')
                first_name = request.POST.get('first_name')
                last_name = request.POST.get('last_name')
                phone_number = request.POST.get('phone_number')
                user_type = request.POST.get('user_type')
                latitude = request.POST.get('latitude')
                longitude = request.POST.get('longitude')
                
                # Validation
                if not latitude or not longitude:
                    messages.error(request, 'Please capture your current location before signing up.')
                    return render(request, 'signup.html')
                
                if password != confirm_password:
                    messages.error(request, 'Passwords do not match.')
                    return render(request, 'signup.html')
                
                if User.objects.filter(username=username).exists():
                    messages.error(request, 'Username already exists.')
                    return render(request, 'signup.html')
                
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'Email already exists.')
                    return render(request, 'signup.html')
                
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    user_type=user_type,
                    latitude=latitude,
                    longitude=longitude,
                    is_active_location=True
                )
                
                # Create profile based on user type
                if user_type == 'vendor':
                    business_name = request.POST.get('business_name')
                    business_type = request.POST.get('business_type')
                    business_address = request.POST.get('business_address')
                    business_phone = request.POST.get('business_phone')
                    business_email = request.POST.get('business_email')
                    
                    VendorProfile.objects.create(
                        user=user,
                        business_name=business_name,
                        business_type=business_type,
                        business_address=business_address,
                        business_phone=business_phone,
                        business_email=business_email
                    )
                
                elif user_type == 'delivery':
                    vehicle_type = request.POST.get('vehicle_type')
                    vehicle_number = request.POST.get('vehicle_number')
                    license_number = request.POST.get('license_number')
                    delivery_radius = request.POST.get('delivery_radius', 10)
                    
                    DeliveryPartnerProfile.objects.create(
                        user=user,
                        vehicle_type=vehicle_type,
                        vehicle_number=vehicle_number,
                        license_number=license_number,
                        delivery_radius=int(delivery_radius),
                        current_latitude=latitude,
                        current_longitude=longitude
                    )
                
                # Login the user
                login(request, user)
                messages.success(request, f'Account created successfully! Welcome to StreetEats Connect.')
                
                if user_type == 'vendor':
                    return redirect('core:vendor_home')
                elif user_type == 'delivery':
                    return redirect('core:delivery_home')
                    
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
    
    return render(request, 'signup.html')

@login_required
def profile_view(request):
    """Profile page view"""
    return render(request, 'profile.html')

@login_required
def update_profile_picture(request):
    """Update user profile picture"""
    if request.method == 'POST':
        try:
            if 'profile_picture' in request.FILES:
                request.user.profile_picture = request.FILES['profile_picture']
                request.user.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'message': 'No image file provided'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def update_location(request):
    """Update user location"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            
            if latitude and longitude:
                request.user.latitude = latitude
                request.user.longitude = longitude
                request.user.is_active_location = True
                request.user.save()
                
                # Update delivery partner location if applicable
                if request.user.user_type == 'delivery' and hasattr(request.user, 'delivery_profile'):
                    request.user.delivery_profile.current_latitude = latitude
                    request.user.delivery_profile.current_longitude = longitude
                    request.user.delivery_profile.save()
                
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid coordinates'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')
