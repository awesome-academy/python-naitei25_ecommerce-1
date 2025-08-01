from django.shortcuts import render
from django.http import HttpResponse
from .fake_data import *

# Create your views here.
def index (request):
    return render(request, 'core/index.html')

def product_list_view(request):
    return render(request, 'core/product-list.html')

def about_us(request):
    return render(request, "core/about_us.html")

def customer_dashboard(request):
    return render(request, 'core/dashboard.html')

def search_view(request):
    return render(request, "core/search.html")

def checkout(request):
    context = {}
    return render(request, "core/checkout.html", context)

def payment_completed_view(request):
    context = {
        "order": get_sample_order(),
    }
    return render(request, 'core/payment-completed.html', context)

def payment_failed_view(request):
    return render(request, 'core/payment-failed.html')

def order_detail(request, id):
    context = {"order_items": get_order_items()}
    return render(request, 'core/order-detail.html', context)

def category_list_view(request):
    context = {"categories": get_categories()}
    return render(request, 'core/category-list.html', context)

def category_product_list__view(request, cid):
    products = get_products_by_category(cid)
    
    # Add reviews count to each product
    for product in products:
        product['reviews_count'] = product['reviews']['all']['count']
    
    context = {
        "category": get_category_by_id(cid),
        "products": products,
    }
    return render(request, "core/category-product-list.html", context)
