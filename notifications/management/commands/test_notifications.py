from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from notifications.services import NotificationService

User = get_user_model()

class Command(BaseCommand):
    help = 'Create test notifications for all users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Username to create notifications for (optional)',
        )

    def handle(self, *args, **options):
        if options['user']:
            try:
                users = [User.objects.get(username=options['user'])]
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User "{options["user"]}" not found')
                )
                return
        else:
            users = User.objects.filter(is_active=True)[:5]  # Limit to 5 users for testing

        if not users:
            self.stdout.write(
                self.style.WARNING('No users found to create notifications for')
            )
            return

        test_notifications = [
            {
                'type': 'system_announcement',
                'title': 'Welcome to StreetEats Connect!',
                'message': 'Thank you for joining our platform. Explore our features and start connecting with suppliers and delivery partners.',
                'priority': 'medium'
            },
            {
                'type': 'availability_update',
                'title': 'New Delivery Partner Available',
                'message': 'A delivery partner is now available in your area. Book your delivery now for faster service!',
                'priority': 'low'
            },
            {
                'type': 'profile_update',
                'title': 'Complete Your Profile',
                'message': 'Please complete your profile to get the best experience on StreetEats Connect.',
                'priority': 'medium'
            }
        ]

        created_count = 0
        for user in users:
            for notif_data in test_notifications:
                notification = NotificationService.create_notification(
                    recipient=user,
                    notification_type=notif_data['type'],
                    title=notif_data['title'],
                    message=notif_data['message'],
                    priority=notif_data['priority']
                )
                if notification:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Created notification "{notif_data["title"]}" for {user.username}'
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} test notifications'
            )
        )