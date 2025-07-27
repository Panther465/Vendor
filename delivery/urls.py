from django.urls import path
from . import views

app_name = 'delivery'

urlpatterns = [
    path('requests/', views.delivery_requests, name='requests'),
    path('requests/<int:request_id>/', views.delivery_request_detail, name='request_detail'),
    path('add-availability/', views.add_availability, name='add_availability'),
    path('accept-request/<int:request_id>/', views.accept_request, name='accept_request'),
    path('reject-request/<int:request_id>/', views.reject_request, name='reject_request'),
    path('update-location/', views.update_location, name='update_location'),
    path('toggle-availability/', views.toggle_availability, name='toggle_availability'),
    path('get-requests/', views.get_requests, name='get_requests'),
]