from django.shortcuts import render, redirect
from django.db.models import Sum, F, DecimalField, Case, When, Value
from django.db.models.functions import Cast, Coalesce
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from userauths.models import User
from core.models import CartOrder, CartOrderProducts, Product, Category, ProductReview, Image, Vendor
from useradmin.forms import AddProductForm
from .constants import *
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db import transaction

import datetime

# Create your views here.
@login_required
def dashboard(request):
    revenue = CartOrder.objects.aggregate(price=Sum(AMOUNT))
    total_orders_count = CartOrder.objects.all()
    all_products = Product.objects.all()
    all_categories = Category.objects.all()
    new_customers = User.objects.all().order_by("-id")[:6]
    latest_orders = CartOrder.objects.select_related(
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
    monthly_revenue = CartOrder.objects.filter(order_date__month=this_month).aggregate(price=Sum(AMOUNT))

    context = {
        "monthly_revenue": monthly_revenue,
        "revenue": revenue,
        "all_products": all_products,
        "all_categories": all_categories,
        "new_customers": new_customers,
        "latest_orders": latest_orders,
        "total_orders_count": total_orders_count,
    }
    return render(request, "useradmin/dashboard.html", context)

@login_required
def products(request):
    sort_by = request.GET.get('sort', 'title')
    order = request.GET.get('order', 'asc')

    if order == 'desc':
        sort_by = '-' + sort_by

    all_products = Product.objects.all().annotate(
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
    }
    return render(request, "useradmin/products.html", context)

@login_required
def add_product(request):
    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                product = form.save()
                
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
        'form': form
    }
    return render(request, "useradmin/add-products.html", context)

@login_required
def edit_product(request, pid):
    product = Product.objects.get(pid=pid)
    
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
    }
    return render(request, "useradmin/edit-products.html", context)

@login_required
def delete_product(request, pid):
    try:
        product = Product.objects.get(pid=pid)
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
def orders(request):
    orders = CartOrder.objects.select_related(
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
    }
    return render(request, "useradmin/orders.html", context)

@login_required
def order_detail(request, id):
    order = CartOrder.objects.select_related(
        'user', 
        'user__profile'
    ).annotate(
        display_id=F(DISPLAY_ID),
        full_name=F(FULL_NAME),
        email=F(EMAIL),
        phone=F(PHONE),
    ).get(id=id)
    
    order_items = CartOrderProducts.objects.filter(order=order)
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, "useradmin/order_detail.html", context)

@login_required
@csrf_exempt
def change_order_status(request, oid):
    try:
        order = CartOrder.objects.get(id=oid)
        
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
                    "Cannot change status of delivered orders. Please create a return/exchange request instead."
                )
            elif status_order.get(current_status, 0) > status_order.get(new_status, 0):
                messages.error(
                    request, 
                    f"Cannot change order status from '{current_status}' to '{new_status}'. Only forward progress is allowed."
                )
            else:
                order.order_status = new_status
                order.save()
                messages.success(request, f"Order status changed from '{current_status}' to '{new_status}'")
        
        return redirect("useradmin:order_detail", order.id)
    except CartOrder.DoesNotExist:
        messages.error(request, "Order not found")
        return redirect("useradmin:orders")

@login_required
def shop_page(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
        products = Product.objects.filter(vendor=vendor)
    except Vendor.DoesNotExist:
        products = Product.objects.none()
        messages.warning(request, "You are not registered as a vendor.")
    
    revenue = CartOrder.objects.filter(
        vendor=vendor if 'vendor' in locals() else None,
        paid_status=True
    ).aggregate(price=Sum(AMOUNT))
    
    total_sales = CartOrderProducts.objects.filter(
        order__vendor=vendor if 'vendor' in locals() else None,
        order__paid_status=True
    ).aggregate(qty=Sum("qty"))

    context = {
        'products': products,
        'revenue': revenue,
        'total_sales': total_sales,
    }
    return render(request, "useradmin/shop_page.html", context)

@login_required
def reviews(request):
    reviews = ProductReview.objects.all()
    context = {
        'reviews':reviews,
    }
    return render(request, "useradmin/reviews.html", context)
