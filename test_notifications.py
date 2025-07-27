#!/usr/bin/env python
"""
Test script to create sample notifications for testing the notification panel
Run this with: python test_notifications.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'streeteats_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from notifications.services import NotificationService

User = get_user_model()

def create_test_notifications():
    """Create test notifications for the first user"""
    try:
        # Get the first user (or create a test user)
        user = User.objects.first()
        if not user:
            print("No users found. Please create a user first.")
            return
        
        print(f"Creating test notifications for user: {user.username}")
        
        # Create various types of notifications
        test_notifications = [
            {
                'notification_type': 'order_placed',
                'title': 'New Order Placed',
                'message': 'Your order #ORD001 has been placed successfully.',
                'priority': 'medium'
            },
            {
                'notification_type': 'order_confirmed',
                'title': 'Order Confirmed',
                'message': 'Your order #ORD001 has been confirmed by the supplier.',
                'priority': 'high'
            },
            {
                'notification_type': 'delivery_request',
                'title': 'New Delivery Request',
                'message': 'You have a new delivery request from ABC Suppliers.',
                'priority': 'high'
            },
            {
                'notification_type': 'payment_received',
                'title': 'Payment Received',
                'message': 'Payment of ₹2,500 has been received for order #ORD001.',
                'priority': 'medium'
            },
            {
                'notification_type': 'system_announcement',
                'title': 'System Maintenance',
                'message': 'Scheduled maintenance will occur tonight from 2 AM to 4 AM.',
                'priority': 'low'
            },
            {
                'notification_type': 'group_buying_started',
                'title': 'Group Buying Session Started',
                'message': 'A new group buying session for organic vegetables has started.',
                'priority': 'medium'
            }
        ]
        
        created_count = 0
        for notification_data in test_notifications:
            notification = NotificationService.create_notification(
                recipient=user,
                **notification_data
            )
            if notification:
                created_count += 1
                print(f"✓ Created: {notification.title}")
        
        print(f"\nSuccessfully created {created_count} test notifications!")
        print(f"Total notifications for {user.username}: {user.notifications.count()}")
        print(f"Unread notifications: {user.notifications.filter(is_read=False).count()}")
        
    except Exception as e:
        print(f"Error creating test notifications: {e}")

if __name__ == '__main__':
    create_test_notifications()