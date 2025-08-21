from django import template
from django.utils import timezone
from django.utils.translation import gettext as _
from datetime import datetime, date

register = template.Library()

@register.inclusion_tag('useradmin/components/coupon_status_badge.html')
def coupon_status_badge(coupon):
    """
    Hiển thị badge trạng thái của coupon
    """
    now = timezone.now()
    
    # Normalize expiry_date để so sánh
    if isinstance(coupon.expiry_date, datetime):
        expiry_datetime = coupon.expiry_date
    else:
        # Nếu là date, convert thành datetime với timezone
        expiry_datetime = timezone.make_aware(
            datetime.combine(coupon.expiry_date, datetime.min.time())
        )
    
    if coupon.active and expiry_datetime > now:
        status = 'active'
        status_text = _('Active')
        badge_class = 'bg-success'
    elif not coupon.active:
        status = 'inactive'
        status_text = _('Inactive')
        badge_class = 'bg-secondary'
    else:
        status = 'expired'
        status_text = _('Expired')
        badge_class = 'bg-danger'
    
    return {
        'status': status,
        'status_text': status_text,
        'badge_class': badge_class,
        'coupon': coupon
    }

@register.inclusion_tag('useradmin/components/coupon_actions_dropdown.html')
def coupon_actions_dropdown(coupon):
    """
    Hiển thị dropdown actions cho mỗi coupon
    """
    return {
        'coupon': coupon
    }

@register.inclusion_tag('useradmin/components/coupon_search_filter.html')
def coupon_search_filter(search_query='', status_filter=''):
    """
    Hiển thị form search và filter cho coupon
    """
    status_choices = [
        ('', _('All Status')),
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('expired', _('Expired')),
    ]
    
    return {
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': status_choices
    }

@register.inclusion_tag('useradmin/components/coupon_table_row.html')
def coupon_table_row(coupon):
    """
    Hiển thị một row trong bảng coupon
    """
    now = timezone.now()
    
    return {
        'coupon': coupon,
        'now': now
    }

@register.inclusion_tag('useradmin/components/coupon_pagination.html')
def coupon_pagination(coupons, search_query='', status_filter=''):
    """
    Hiển thị pagination cho danh sách coupon
    """
    return {
        'coupons': coupons,
        'search_query': search_query,
        'status_filter': status_filter
    }

@register.inclusion_tag('useradmin/components/coupon_empty_state.html')
def coupon_empty_state(search_query='', status_filter=''):
    """
    Hiển thị trạng thái empty cho bảng coupon
    """
    has_filters = bool(search_query or status_filter)
    
    return {
        'has_filters': has_filters,
        'search_query': search_query,
        'status_filter': status_filter
    }

@register.inclusion_tag('useradmin/components/coupon_filter_indicator.html')
def coupon_filter_indicator(search_query='', status_filter=''):
    """
    Hiển thị indicator khi có filter được áp dụng
    """
    has_filters = bool(search_query or status_filter)
    
    return {
        'has_filters': has_filters,
        'search_query': search_query,
        'status_filter': status_filter
    }

# Simple filters
@register.filter
def coupon_usage_count(coupon):
    """
    Trả về số lần sử dụng coupon
    """
    return getattr(coupon, 'usage_count', 0)

@register.filter
def is_coupon_expired(coupon):
    """
    Kiểm tra xem coupon đã hết hạn chưa
    SỬA LỖI: Handle cả datetime và date
    """
    now = timezone.now()
    
    # Normalize expiry_date để so sánh
    if isinstance(coupon.expiry_date, datetime):
        # Nếu là datetime
        if timezone.is_naive(coupon.expiry_date):
            # Nếu datetime naive, make it aware
            expiry_datetime = timezone.make_aware(coupon.expiry_date)
        else:
            # Nếu datetime đã có timezone
            expiry_datetime = coupon.expiry_date
    elif isinstance(coupon.expiry_date, date):
        # Nếu là date, convert thành datetime cuối ngày
        expiry_datetime = timezone.make_aware(
            datetime.combine(coupon.expiry_date, datetime.max.time())
        )
    else:
        # Fallback: không thể xác định type
        return False
    
    return expiry_datetime <= now

@register.filter
def coupon_status_class(coupon):
    """
    Trả về CSS class cho status coupon
    """
    now = timezone.now()
    
    # Normalize expiry_date để so sánh
    if isinstance(coupon.expiry_date, datetime):
        if timezone.is_naive(coupon.expiry_date):
            expiry_datetime = timezone.make_aware(coupon.expiry_date)
        else:
            expiry_datetime = coupon.expiry_date
    elif isinstance(coupon.expiry_date, date):
        expiry_datetime = timezone.make_aware(
            datetime.combine(coupon.expiry_date, datetime.max.time())
        )
    else:
        return 'text-secondary'
    
    if coupon.active and expiry_datetime > now:
        return 'text-success'
    elif not coupon.active:
        return 'text-secondary'
    else:
        return 'text-danger'

@register.filter
def days_until_expiry(coupon):
    """
    Trả về số ngày còn lại đến khi hết hạn
    """
    now = timezone.now()
    
    # Normalize expiry_date
    if isinstance(coupon.expiry_date, datetime):
        if timezone.is_naive(coupon.expiry_date):
            expiry_datetime = timezone.make_aware(coupon.expiry_date)
        else:
            expiry_datetime = coupon.expiry_date
    elif isinstance(coupon.expiry_date, date):
        expiry_datetime = timezone.make_aware(
            datetime.combine(coupon.expiry_date, datetime.max.time())
        )
    else:
        return 0
    
    delta = expiry_datetime - now
    return delta.days

@register.filter
def format_expiry_date(coupon):
    """
    Format expiry date với timezone handling
    """
    if isinstance(coupon.expiry_date, datetime):
        return coupon.expiry_date.strftime("%d %b %Y %H:%M")
    elif isinstance(coupon.expiry_date, date):
        return coupon.expiry_date.strftime("%d %b %Y")
    else:
        return "Invalid date"