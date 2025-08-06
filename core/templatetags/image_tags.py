from django import template
from core.constants import DEFAULT_CATEGORY_IMAGE

register = template.Library()

@register.filter(name='default_image')
def default_image(value):
    """Trả về ảnh mặc định nếu value là None hoặc rỗng"""
    if value:
        return value
    return DEFAULT_CATEGORY_IMAGE
