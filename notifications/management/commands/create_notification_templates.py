from django.core.management.base import BaseCommand
from notifications.models import NotificationTemplate

class Command(BaseCommand):
    help = 'Create default notification templates'

    def handle(self, *args, **options):
        templates = [
            {
                'notification_type': 'order_placed',
                'title_template': 'Order Placed Successfully',
                'message_template': 'Your order #{{ order_number }} has been placed successfully. Total amount: ₹{{ amount }}',
                'variables_help': 'Available variables: order_number, amount, recipient_name'
            },
            {
                'notification_type': 'order_confirmed',
                'title_template': 'Order Confirmed',
                'message_template': 'Great news! Your order #{{ order_number }} has been confirmed and is being processed.',
                'variables_help': 'Available variables: order_number, recipient_name'
            },
            {
                'notification_type': 'order_shipped',
                'title_template': 'Order Shipped',
                'message_template': 'Your order #{{ order_number }} has been shipped and is on its way to you!',
                'variables_help': 'Available variables: order_number, recipient_name'
            },
            {
                'notification_type': 'order_delivered',
                'title_template': 'Order Delivered',
                'message_template': 'Your order #{{ order_number }} has been delivered successfully. Thank you for choosing StreetEats Connect!',
                'variables_help': 'Available variables: order_number, recipient_name'
            },
            {
                'notification_type': 'order_cancelled',
                'title_template': 'Order Cancelled',
                'message_template': 'Your order #{{ order_number }} has been cancelled. If you have any questions, please contact support.',
                'variables_help': 'Available variables: order_number, recipient_name'
            },
            {
                'notification_type': 'delivery_request',
                'title_template': 'New Delivery Request',
                'message_template': 'You have a new delivery request from {{ sender_name }}. Please check the details and respond.',
                'variables_help': 'Available variables: sender_name, recipient_name, object_id'
            },
            {
                'notification_type': 'delivery_accepted',
                'title_template': 'Delivery Request Accepted',
                'message_template': '{{ sender_name }} has accepted your delivery request. Your order will be delivered soon!',
                'variables_help': 'Available variables: sender_name, recipient_name'
            },
            {
                'notification_type': 'delivery_rejected',
                'title_template': 'Delivery Request Declined',
                'message_template': '{{ sender_name }} has declined your delivery request. Please try another delivery partner.',
                'variables_help': 'Available variables: sender_name, recipient_name'
            },
            {
                'notification_type': 'delivery_completed',
                'title_template': 'Delivery Completed',
                'message_template': 'Your delivery has been completed successfully by {{ sender_name }}.',
                'variables_help': 'Available variables: sender_name, recipient_name'
            },
            {
                'notification_type': 'availability_update',
                'title_template': 'Delivery Partner Available',
                'message_template': '{{ sender_name }} is now available for delivery in your area. Book now for fast delivery!',
                'variables_help': 'Available variables: sender_name, recipient_name'
            },
            {
                'notification_type': 'payment_received',
                'title_template': 'Payment Received',
                'message_template': 'We have received your payment of ₹{{ amount }}. Thank you!',
                'variables_help': 'Available variables: amount, recipient_name'
            },
            {
                'notification_type': 'payment_failed',
                'title_template': 'Payment Failed',
                'message_template': 'Your payment of ₹{{ amount }} could not be processed. Please try again or use a different payment method.',
                'variables_help': 'Available variables: amount, recipient_name'
            },
            {
                'notification_type': 'group_buying_started',
                'title_template': 'Group Buying Session Started',
                'message_template': 'A new group buying session has started. Join now to get better prices!',
                'variables_help': 'Available variables: recipient_name'
            },
            {
                'notification_type': 'group_buying_joined',
                'title_template': 'Someone Joined Your Group',
                'message_template': '{{ sender_name }} has joined your group buying session. More participants mean better prices!',
                'variables_help': 'Available variables: sender_name, recipient_name'
            },
            {
                'notification_type': 'group_buying_completed',
                'title_template': 'Group Buying Completed',
                'message_template': 'Your group buying session has been completed successfully. Check your orders for details.',
                'variables_help': 'Available variables: recipient_name'
            },
            {
                'notification_type': 'system_announcement',
                'title_template': 'System Announcement',
                'message_template': 'Important update from StreetEats Connect team.',
                'variables_help': 'Available variables: recipient_name'
            },
            {
                'notification_type': 'profile_update',
                'title_template': 'Profile Update Required',
                'message_template': 'Please update your profile information to continue using our services.',
                'variables_help': 'Available variables: recipient_name'
            },
            {
                'notification_type': 'verification_complete',
                'title_template': 'Account Verified',
                'message_template': 'Congratulations! Your account has been successfully verified. You can now access all features.',
                'variables_help': 'Available variables: recipient_name'
            },
        ]

        created_count = 0
        updated_count = 0

        for template_data in templates:
            template, created = NotificationTemplate.objects.get_or_create(
                notification_type=template_data['notification_type'],
                defaults={
                    'title_template': template_data['title_template'],
                    'message_template': template_data['message_template'],
                    'variables_help': template_data['variables_help'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created template: {template_data["notification_type"]}')
                )
            else:
                # Update existing template
                template.title_template = template_data['title_template']
                template.message_template = template_data['message_template']
                template.variables_help = template_data['variables_help']
                template.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated template: {template_data["notification_type"]}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {created_count + updated_count} templates '
                f'({created_count} created, {updated_count} updated)'
            )
        )