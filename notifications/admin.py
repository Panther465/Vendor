from django.contrib import admin
from .models import Notification, NotificationPreference, NotificationTemplate

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'notification_type', 'priority', 'is_read', 'created_at']
    list_filter = ['notification_type', 'priority', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'recipient__username', 'recipient__email']
    readonly_fields = ['created_at', 'updated_at', 'read_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('recipient', 'sender', 'notification_type', 'priority')
        }),
        ('Content', {
            'fields': ('title', 'message', 'action_url')
        }),
        ('Status', {
            'fields': ('is_read', 'is_sent', 'read_at')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_order_updates', 'email_delivery_updates', 'inapp_order_updates']
    search_fields = ['user__username', 'user__email']
    list_filter = ['email_order_updates', 'email_delivery_updates', 'inapp_order_updates']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Email Notifications', {
            'fields': ('email_order_updates', 'email_delivery_updates', 'email_payment_updates', 
                      'email_group_buying', 'email_system_announcements')
        }),
        ('Push Notifications', {
            'fields': ('push_order_updates', 'push_delivery_updates', 'push_payment_updates',
                      'push_group_buying', 'push_system_announcements')
        }),
        ('In-App Notifications', {
            'fields': ('inapp_order_updates', 'inapp_delivery_updates', 'inapp_payment_updates',
                      'inapp_group_buying', 'inapp_system_announcements')
        }),
    )

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['notification_type', 'title_template', 'is_active', 'created_at']
    list_filter = ['notification_type', 'is_active']
    search_fields = ['title_template', 'message_template']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('notification_type', 'is_active')
        }),
        ('Template Content', {
            'fields': ('title_template', 'message_template')
        }),
        ('Help', {
            'fields': ('variables_help',),
            'description': 'Available template variables for customization'
        }),
    )
