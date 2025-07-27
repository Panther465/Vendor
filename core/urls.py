from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'core'

def redirect_to_login(request):
    if request.user.is_authenticated:
        if request.user.user_type == 'vendor':
            return redirect('core:vendor_home')
        elif request.user.user_type == 'delivery':
            return redirect('core:delivery_home')
    return redirect('accounts:login')

urlpatterns = [
    path('', redirect_to_login, name='home'),
    path('vendor/', views.vendor_home, name='vendor_home'),
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('delivery/', views.delivery_home, name='delivery_home'),
    path('delivery/dashboard/', views.delivery_dashboard, name='delivery_dashboard'),
    path('popup-demo/', views.popup_demo, name='popup_demo'),
    path('contact/', views.contact_us, name='contact_us'),
    path('about/', views.about_us, name='about_us'),
]