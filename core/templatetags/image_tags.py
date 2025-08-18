from django import template
from core.constants import DEFAULT_CATEGORY_IMAGE
from core.models import Image

register = template.Library()

@register.filter(name='default_image')
def default_image(value):
    """Trả về ảnh mặc định nếu value là None hoặc rỗng"""
    if value:
        return value
    return DEFAULT_CATEGORY_IMAGE

@register.filter
def primary_image_url(obj, object_type):
    """Get primary image URL for any object"""
    try:
        if hasattr(obj, 'cid'):
            object_id = obj.cid
        elif hasattr(obj, 'vid'):
            object_id = obj.vid
        elif hasattr(obj, 'pid'):
            object_id = obj.pid
        else:
            return None
            
        img = Image.objects.filter(
            object_type=object_type,
            object_id=object_id,
            is_primary=True
        ).first()
        
        if img:
            return img.image.url
        return None
    except Exception:
        return None
