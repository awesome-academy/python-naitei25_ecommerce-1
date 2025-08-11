from django import template
from django.utils.translation import gettext as _

register = template.Library()

@register.inclusion_tag('useradmin/components/order_status_select.html')
def order_status_select(order):
    """Render order status selection dropdown"""
    return {
        'order': order,
        'status_choices': [
            ('pending', _('Pending')),
            ('processing', _('Processing')),
            ('shipped', _('Shipped')),
            ('delivered', _('Delivered')),
        ]
    }

@register.inclusion_tag('useradmin/components/order_info_card.html', takes_context=True)
def order_info_card(context, icon, title):
    """Render order info card with icon and title"""
    return {
        'icon': icon,
        'title': title,
        'order': context['order'],  # Pass order from context
    }

@register.inclusion_tag('useradmin/components/order_item_row.html')
def order_item_row(item):
    """Render order item table row"""
    return {
        'item': item,
    }

@register.inclusion_tag('useradmin/components/order_summary.html')
def order_summary(order):
    """Render order summary with totals"""
    return {
        'order': order,
    }
