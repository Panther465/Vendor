from django.contrib import admin
from .models import (
    GroupBuyingProfile, GroupBuyingItem, GroupBuyingRequest,
    GroupBuyingSession, GroupCart, GroupCartItem
)

@admin.register(GroupBuyingProfile)
class GroupBuyingProfileAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'vendor', 'is_enabled', 'created_at']
    list_filter = ['is_enabled', 'created_at']
    search_fields = ['business_name', 'vendor__username']

@admin.register(GroupBuyingItem)
class GroupBuyingItemAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'profile', 'category', 'priority', 'created_at']
    list_filter = ['category', 'priority', 'created_at']
    search_fields = ['item_name', 'profile__business_name']

@admin.register(GroupBuyingRequest)
class GroupBuyingRequestAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['sender__username', 'receiver__username']

@admin.register(GroupBuyingSession)
class GroupBuyingSessionAdmin(admin.ModelAdmin):
    list_display = ['session_name', 'creator', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['session_name', 'creator__username']

@admin.register(GroupCart)
class GroupCartAdmin(admin.ModelAdmin):
    list_display = ['session', 'total_items', 'subtotal', 'created_at']
    readonly_fields = ['total_items', 'subtotal', 'group_discount', 'total_after_discount']

@admin.register(GroupCartItem)
class GroupCartItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'added_by', 'cart', 'added_at']
    list_filter = ['added_at']
    search_fields = ['product__name', 'added_by__username']