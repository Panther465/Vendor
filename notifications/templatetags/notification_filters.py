from django import template

register = template.Library()

@register.filter(name='format_notification_type')
def format_notification_type(value):
    """Format notification type for display"""
    if not value:
        return value
    
    # Replace underscores with spaces and capitalize each word
    formatted = value.replace('_', ' ').title()
    return formatted