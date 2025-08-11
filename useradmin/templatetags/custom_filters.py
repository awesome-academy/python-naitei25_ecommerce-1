from django import template
from django.utils.translation import gettext as _

register = template.Library()

@register.filter
def translate_field_name(key):
    """Translate field names to localized text"""
    translations = {
        'Name': _('Name'),
        'Email': _('Email'), 
        'Phone': _('Phone'),
        'Shipping Method': _('Shipping Method'),
        'Order Id': _('Order ID'),
        'Order Status': _('Order Status'),
        'Payment Status': _('Payment Status'),
        'Address': _('Address'),
        'City': _('City'),
        'State': _('State'),
        'Country': _('Country'),
        'Customer': _('Customer'),
        'Order info': _('Order info'),
        'Deliver to': _('Deliver to'),
    }
    return translations.get(str(key), str(key))

@register.filter
def format_field_value(value, field_name=""):
    """Format field values based on field type"""
    if not value or str(value).lower() in ['none', '', 'null']:
        return _("N/A")
    
    field_name_lower = str(field_name).lower()
    
    # Phone formatting
    if 'phone' in field_name_lower:
        cleaned = ''.join(filter(str.isdigit, str(value)))
        if len(cleaned) == 10:
            return f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
        elif len(cleaned) == 11 and cleaned[0] == '1':
            return f"+1 ({cleaned[1:4]}) {cleaned[4:7]}-{cleaned[7:]}"
        return str(value)
    
    # Email formatting  
    elif 'email' in field_name_lower:
        return str(value).lower() if '@' in str(value) else _("N/A")
    
    # Payment status formatting
    elif 'payment' in field_name_lower and 'status' in field_name_lower:
        return _("Paid") if str(value).lower() in ['paid', 'true', '1'] else _("Not Paid")
    
    # Order status formatting
    elif 'order' in field_name_lower and 'status' in field_name_lower:
        status_map = {
            'pending': _('Pending'),
            'processing': _('Processing'), 
            'shipped': _('Shipped'),
            'delivered': _('Delivered'),
            'cancelled': _('Cancelled')
        }
        return status_map.get(str(value).lower(), str(value).title())
    
    # Order ID formatting
    elif 'order' in field_name_lower and 'id' in field_name_lower:
        return f"#{value}"
    
    # Default formatting
    return str(value)

@register.filter
def display_field(value, field_name):
    """Combined filter for field name translation and value formatting"""
    translated_name = translate_field_name(field_name)
    formatted_value = format_field_value(value, field_name)
    return f"<strong>{translated_name}:</strong> {formatted_value}"
