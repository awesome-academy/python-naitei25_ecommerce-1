from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext as _
from functools import wraps
from core.models import Vendor

def vendor_required(redirect_url="useradmin:dashboard"):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role != "vendor":
                messages.error(request, _("Bạn cần có role vendor để truy cập tính năng này."))
                return redirect("core:index")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def vendor_profile_required(redirect_url="useradmin:dashboard"):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            try:
                vendor = Vendor.objects.get(user=request.user)
                kwargs['vendor'] = vendor
                return view_func(request, *args, **kwargs)
            except Vendor.DoesNotExist:
                messages.warning(request, _("Bạn cần tạo hồ sơ vendor trước."))
                return redirect(redirect_url)
        return _wrapped_view
    return decorator

def vendor_auth_required(redirect_to_create=False):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role != "vendor":
                messages.error(request, _("Bạn cần có role vendor để truy cập tính năng này."))
                return redirect("core:index")
            
            try:
                vendor = Vendor.objects.get(user=request.user)
                kwargs['vendor'] = vendor
                return view_func(request, *args, **kwargs)
            except Vendor.DoesNotExist:
                messages.warning(request, _("Bạn cần tạo hồ sơ vendor trước."))
                if redirect_to_create:
                    return redirect("useradmin:create-vendor")
                return redirect("useradmin:dashboard")
        return _wrapped_view
    return decorator