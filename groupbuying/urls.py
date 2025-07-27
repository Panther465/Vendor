from django.urls import path
from . import views

app_name = 'groupbuying'

urlpatterns = [
    path('', views.group_buying_home, name='home'),
    path('setup-profile/', views.setup_profile, name='setup_profile'),
    path('manage-items/', views.manage_items, name='manage_items'),
    path('send-request/<int:vendor_id>/', views.send_request, name='send_request'),
    path('handle-request/<int:request_id>/<str:action>/', views.handle_request, name='handle_request'),
    path('start-session/', views.start_group_session, name='start_session'),
    path('suppliers/<int:session_id>/', views.group_suppliers, name='group_suppliers'),
    path('cart/<int:session_id>/', views.group_cart, name='group_cart'),
    path('vendor-details/<int:vendor_id>/', views.vendor_details, name='vendor_details'),
]