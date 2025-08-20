from django.shortcuts import render, redirect
from django.db.models import Sum, F, DecimalField, Case, When, Value, Avg
from django.db.models.functions import Cast, Coalesce
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from userauths.models import User
from core.models import CartOrder, CartOrderProducts, Product, Category, ProductReview, Image, Vendor
from useradmin.forms import AddProductForm
from .constants import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db import transaction
from django.utils.translation import gettext as _
import datetime
from .decorators import vendor_required, vendor_profile_required, vendor_auth_required

@login_required
def dashboard(request):
    has_vendor = False
    try:
        vendor = Vendor.objects.get(user=request.user)
        has_vendor = True
    except Vendor.DoesNotExist:
        vendor = None

    if request.user.role == "vendor":
        if not has_vendor:
            return render(request, "useradmin/dashboard.html", {
                "has_vendor": False,
                "need_vendor": True,
                "message": _("Bạn cần tạo hồ sơ vendor để tiếp tục.")
            })
        else:
            pass
    else:
        return render(request, "useradmin/not_vendor.html", {
            "error_message": _("Bạn cần đăng nhập dưới quyền vendor.")
        })

    revenue = CartOrder.objects.filter(vendor=vendor).aggregate(price=Sum(AMOUNT))
    total_orders_count = CartOrder.objects.filter(vendor=vendor).count()
    all_products = Product.objects.filter(vendor=vendor)
    all_categories = Category.objects.all()
    new_customers = User.objects.all().order_by("-id")[:6]
    latest_orders = CartOrder.objects.filter(vendor=vendor).select_related(
        'user',
        'user__profile'
    ).annotate(
        display_id=F(DISPLAY_ID),
        full_name=F(FULL_NAME),
        email=F(EMAIL),
        phone=F(PHONE),
        total=Cast(
            Coalesce(F(AMOUNT), Value(0)),
            output_field=DecimalField(max_digits=MAX_DIGITS_DECIMAL, decimal_places=DECIMAL_PLACES)
        )
    ).order_by('-order_date')[:10]

    this_month = datetime.datetime.now().month
    monthly_revenue = CartOrder.objects.filter(vendor=vendor, order_date__month=this_month).aggregate(price=Sum(AMOUNT))

    context = {
        "monthly_revenue": monthly_revenue,
        "revenue": revenue,
        "all_products": all_products,
        "all_categories": all_categories,
        "new_customers": new_customers,
        "latest_orders": latest_orders,
        "total_orders_count": total_orders_count,
        "has_vendor": has_vendor,
        "vendor": vendor,
    }
    return render(request, "useradmin/dashboard.html", context)

@login_required
@vendor_auth_required()
def products(request, vendor):
    sort_by = request.GET.get('sort', 'title')
    order = request.GET.get('order', 'asc')

    if order == 'desc':
        sort_by = '-' + sort_by

    all_products = Product.objects.filter(vendor=vendor).annotate(
        display_price=Cast(
            Coalesce('amount', Value(0)),
            output_field=DecimalField(max_digits=MAX_DIGITS_DECIMAL, decimal_places=DECIMAL_PLACES)
        ),
        display_old_price=Cast(
            Coalesce('old_price', Value(0)),
            output_field=DecimalField(max_digits=MAX_DIGITS_DECIMAL, decimal_places=DECIMAL_PLACES)
        ),
        discount_percent=Case(
            When(
                old_price__gt=0,
                then=Cast(
                    (Cast(Coalesce(F('old_price'), Value(0)), DecimalField(max_digits=MAX_DIGITS_DECIMAL, decimal_places=DECIMAL_PLACES)) -
                     Cast(Coalesce(F('amount'), Value(0)), DecimalField(max_digits=MAX_DIGITS_DECIMAL, decimal_places=DECIMAL_PLACES))) * 100.0 /
                    Cast(Coalesce(F('old_price'), Value(1)), DecimalField(max_digits=MAX_DIGITS_DECIMAL, decimal_places=DECIMAL_PLACES)),
                    output_field=DecimalField(max_digits=MAX_DIGITS_DECIMAL, decimal_places=DECIMAL_PLACES)
                )
            ),
            default=Value(0),
            output_field=DecimalField(max_digits=MAX_DIGITS_DECIMAL, decimal_places=DECIMAL_PLACES)
        )
    ).order_by(sort_by)

    all_categories = Category.objects.all()

    context = {
        "all_products": all_products,
        "all_categories": all_categories,
        'sort_by': request.GET.get('sort', 'title'),
        'order': request.GET.get('order', 'asc'),
        'vendor': vendor,
    }
    return render(request, "useradmin/products.html", context)

@login_required
@vendor_auth_required()
def add_product(request, vendor):
    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                product = form.save(commit=False)
                product.vendor = vendor
                product.save()
                form.save_m2m()

                if 'image' in request.FILES:
                    Image.objects.create(
                        image=request.FILES['image'],
                        alt_text=product.title,
                        object_type='product',
                        object_id=product.pid,
                        is_primary=True
                    )

            messages.success(request, f"Product '{product.title}' added successfully")
            return redirect("useradmin:dashboard-products")
    else:
        form = AddProductForm()

    context = {
        'form': form,
        'vendor': vendor,
    }
    return render(request, "useradmin/add-products.html", context)

@login_required
@vendor_auth_required()
def edit_product(request, pid, vendor):
    try:
        product = Product.objects.get(pid=pid)
        if product.vendor != vendor:
            messages.error(request, _("Bạn không có quyền chỉnh sửa sản phẩm này."))
            return redirect("useradmin:dashboard-products")
    except Product.DoesNotExist:
        messages.error(request, _("Không tìm thấy sản phẩm."))
        return redirect("useradmin:dashboard-products")

    primary_image = Image.objects.filter(
        object_type='product',
        object_id=product.pid,
        is_primary=True
    ).first()

    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            with transaction.atomic():
                new_form = form.save(commit=False)
                new_form.vendor = vendor
                new_form.save()
                form.save_m2m()

                if 'image' in request.FILES:
                    if primary_image:
                        primary_image.delete()

                    Image.objects.create(
                        image=request.FILES['image'],
                        alt_text=product.title,
                        object_type='product',
                        object_id=product.pid,
                        is_primary=True
                    )

            messages.success(request, f"Product '{product.title}' updated successfully")
            return redirect("useradmin:dashboard-products")
    else:
        form = AddProductForm(instance=product)

    context = {
        'form': form,
        'product': product,
        'primary_image': primary_image,
        'vendor': vendor,
    }
    return render(request, "useradmin/edit-products.html", context)

@login_required
@vendor_auth_required()
def delete_product(request, pid, vendor):
    try:
        product = Product.objects.get(pid=pid)

        if product.vendor != vendor:
            messages.error(request, _("Bạn không có quyền xóa sản phẩm này."))
            return redirect("useradmin:dashboard-products")

        product.status = False
        product.in_stock = False
        product.product_status = "deleted"
        product.save()

        messages.success(request, f"Product '{product.title}' has been marked as deleted")
        return redirect("useradmin:dashboard-products")

    except Product.DoesNotExist:
        messages.error(request, "Product not found")
        return redirect("useradmin:dashboard-products")

@login_required
@vendor_auth_required()
def orders(request, vendor):
    orders = CartOrder.objects.filter(vendor=vendor).select_related(
        'user',
        'user__profile'
    ).annotate(
        display_id=F(DISPLAY_ID),
        full_name=F(FULL_NAME),
        email=F(EMAIL),
        phone=F(PHONE),
    ).order_by(f'-{ORDER_DATE}')

    context = {
        'orders': orders,
        'vendor': vendor,
    }
    return render(request, "useradmin/orders.html", context)

@login_required
@vendor_auth_required()
def order_detail(request, id, vendor):
    try:
        order = CartOrder.objects.select_related(
            'user',
            'user__profile'
        ).annotate(
            display_id=F(DISPLAY_ID),
            full_name=F(FULL_NAME),
            email=F(EMAIL),
            phone=F(PHONE),
        ).get(id=id)

        if order.vendor != vendor:
            messages.error(request, _("Bạn không có quyền xem đơn hàng này."))
            return redirect("useradmin:orders")

        order_items = CartOrderProducts.objects.filter(order=order)

        context = {
            'order': order,
            'order_items': order_items,
            'vendor': vendor,
            'status_choices': [
                ('pending', _('Pending')),
                ('processing', _('Processing')),
                ('shipped', _('Shipped')),
                ('delivered', _('Delivered')),
            ]
        }
        return render(request, "useradmin/order_detail.html", context)

    except CartOrder.DoesNotExist:
        messages.error(request, _("Không tìm thấy đơn hàng."))
        return redirect("useradmin:orders")

@login_required
@vendor_auth_required()
@csrf_exempt
def change_order_status(request, oid, vendor):
    try:
        order = CartOrder.objects.get(id=oid)

        if order.vendor != vendor:
            messages.error(request, _("Bạn không có quyền thay đổi trạng thái đơn hàng này."))
            return redirect("useradmin:orders")

        if request.method == "POST":
            new_status = request.POST.get("status")
            current_status = order.order_status

            status_order = {
                'pending': 1,
                'processing': 2,
                'shipped': 3,
                'delivered': 4
            }

            if current_status == 'delivered' and new_status != 'delivered':
                messages.error(
                    request,
                    _("Không thể thay đổi trạng thái đơn hàng đã giao. Vui lòng tạo yêu cầu hoàn trả/đổi hàng.")
                )
            elif status_order.get(current_status, 0) > status_order.get(new_status, 0):
                messages.error(
                    request,
                    _("Không thể thay đổi trạng thái đơn hàng từ '{}' thành '{}'. Chỉ cho phép tiến trình tiến tới.").format(
                        current_status, new_status
                    )
                )
            else:
                order.order_status = new_status
                order.save()
                messages.success(request, _("Trạng thái đơn hàng đã được thay đổi từ '{}' thành '{}'").format(
                    current_status, new_status
                ))

        return redirect("useradmin:order_detail", order.id)
    except CartOrder.DoesNotExist:
        messages.error(request, _("Không tìm thấy đơn hàng."))
        return redirect("useradmin:orders")

@login_required
def shop_page(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
        has_vendor = True

        try:
            vendor_image = Image.objects.get(
                object_type='vendor',
                object_id=vendor.vid,
                is_primary=True
            )
            vendor_image_url = vendor_image.image.url
        except Image.DoesNotExist:
            vendor_image_url = None

        products = Product.objects.filter(vendor=vendor)

        revenue = CartOrder.objects.filter(
            vendor=vendor,
            paid_status=True
        ).aggregate(price=Sum(AMOUNT))

        total_sales = CartOrderProducts.objects.filter(
            order__vendor=vendor,
            order__paid_status=True
        ).aggregate(qty=Sum("qty"))

        vendor_ratings = ProductReview.objects.filter(
            product__vendor=vendor
        ).aggregate(
            avg_rating=Coalesce(Avg('rating'), Value(0.0))
        )

    except Vendor.DoesNotExist:
        vendor = None
        has_vendor = False
        vendor_image_url = None
        products = []
        revenue = {'price': 0}
        total_sales = {'qty': 0}
        vendor_ratings = {'avg_rating': 0}

    context = {
        'vendor': vendor,
        'vendor_image_url': vendor_image_url,
        'products': products,
        'revenue': revenue,
        'total_sales': total_sales,
        'vendor_ratings': vendor_ratings,
        'has_vendor': has_vendor,
    }

    return render(request, "useradmin/shop_page.html", context)

@login_required
@vendor_auth_required()
def reviews(request, vendor):
    vendor_products = Product.objects.filter(vendor=vendor).values_list('pid', flat=True)
    reviews = ProductReview.objects.filter(product__pid__in=vendor_products)

    context = {
        'reviews': reviews,
        'vendor': vendor,
    }
    return render(request, "useradmin/reviews.html", context)

@login_required
@vendor_required(redirect_url="core:index")
def create_vendor(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
        messages.info(request, _("Bạn đã có tài khoản vendor"))
        return redirect('useradmin:dashboard')
    except Vendor.DoesNotExist:
        pass

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        address = request.POST.get('address')
        contact = request.POST.get('contact')
        chat_resp_time = int(request.POST.get('chat_resp_time', 60))
        shipping_on_time = int(request.POST.get('shipping_on_time', 95))
        authentic_rating = float(request.POST.get('authentic_rating', 5.0))
        days_return = int(request.POST.get('days_return', 7))
        warranty_period = int(request.POST.get('warranty_period', 12))

        with transaction.atomic():
            import shortuuid
            vid = f"v-{shortuuid.uuid()[:10]}"

            vendor = Vendor.objects.create(
                vid=vid,
                title=title,
                description=description,
                address=address,
                contact=contact,
                chat_resp_time=chat_resp_time,
                shipping_on_time=shipping_on_time,
                authentic_rating=authentic_rating,
                days_return=days_return,
                warranty_period=warranty_period,
                user=request.user
            )

            if 'image' in request.FILES:
                Image.objects.create(
                    image=request.FILES['image'],
                    alt_text=title,
                    object_type='vendor',
                    object_id=vid,
                    is_primary=True
                )

        messages.success(request, _("Tài khoản vendor của bạn đã được tạo thành công"))
        return redirect('useradmin:dashboard')

    return render(request, 'useradmin/create_vendor.html')
