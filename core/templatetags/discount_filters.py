from django import template

register = template.Library()

@register.filter(name="get_discount_percentage")
def discount_percentage(product):
    if hasattr(product, "get_precentage"):
        percentage = product.get_precentage()
        if percentage > 0:
            return round(percentage, 0)
    return None
