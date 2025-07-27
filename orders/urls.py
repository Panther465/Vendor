from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='list'),
    path('create/', views.create_order, name='create'),
    path('<int:order_id>/', views.order_detail, name='detail'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('my-orders/', views.my_orders_view, name='my_orders'),
    
    # Address management
    path('delivery-address/', views.delivery_address_view, name='delivery_address'),
    path('save-address/', views.save_address, name='save_address'),
    path('edit-address/<int:address_id>/', views.edit_address, name='edit_address'),
    path('delete-address/<int:address_id>/', views.delete_address, name='delete_address'),
    
    # Payment processing
    path('create-razorpay-order/', views.create_razorpay_order, name='create_razorpay_order'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('success/<int:order_id>/', views.order_success, name='order_success'),
    
    # Cart API endpoints
    path('api/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('api/update-cart/', views.update_cart_item, name='update_cart'),
    path('api/remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('api/cart-count/', views.get_cart_count, name='cart_count'),
]