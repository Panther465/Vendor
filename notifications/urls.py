from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('<int:notification_id>/', views.notification_detail, name='detail'),
    path('<int:notification_id>/read/', views.mark_as_read, name='mark_as_read'),
    path('<int:notification_id>/delete/', views.delete_notification, name='delete'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_as_read'),
    path('delete-all/', views.delete_all_notifications, name='delete_all'),
    path('json/', views.get_notifications_json, name='json'),
    path('popup/', views.notification_popup, name='popup'),
    path('preferences/', views.notification_preferences, name='preferences'),
]