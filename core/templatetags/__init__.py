from django import template

register = template.Library()

@register.filter
def discount_percentage(product):
    """Trả về phần trăm giảm giá của product, None nếu không có giảm giá."""
    if hasattr(product, "get_precentage") and product.get_precentage > 0:
        return round(product.get_precentage, 0)
    return None
