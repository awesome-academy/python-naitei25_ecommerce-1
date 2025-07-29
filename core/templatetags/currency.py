from django import template

register = template.Library()

@register.filter()
def currency(value):
    try:
        value = float(value)
        return "${:,.2f}".format(value)  # Kết quả ví dụ: $123,456.78
    except (ValueError, TypeError):
        return value
def mul(value, arg):
    """Multiply value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ""