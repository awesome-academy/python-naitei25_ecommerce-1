from django.shortcuts import render
from django.http import HttpResponse

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
    # Mock data cho template testing
    sample_order = {
        'oid': 'ORD-12345',
        'total': 320.21,
        'paid_status': True,
        'created_date': '2024-01-15',
        'payment_method': 'Credit Card'
    }
    
    context = {
        "order": sample_order,
    }
    return render(request, 'core/payment-completed.html', context)

def payment_failed_view(request):
    return render(request, 'core/payment-failed.html')
    return render(request, 'partials/base.html')

def order_detail(request, id):
    #mock data
    order_items = [
        {
            "id": 1,
            "image": "/static/assets/imgs/shop/product-1-1.jpg",
            "item": "Food 1",
            "price": 10000,
            "qty": 2,
            "total": 20000,
        },
        {
            "id": 2,
            "image": "/static/assets/imgs/shop/product-2-1.jpg",
            "item": "Food 2",
            "price": 200000,
            "qty": 1,
            "total": 200000,
        },
    ]
    context = {"order_items": order_items}
    return render(request, 'core/order-detail.html', context)

def category_list_view(request):
    #mock data
    categories = [
        {
            "cid": "cat1",
            "title": "Vegetables",
            "image": {"url": "/static/assets/imgs/shop/cat-1.png"},
            "category": {"count": 12},
        },
        {
            "cid": "cat2",
            "title": "Meat",
            "image": {"url": "/static/assets/imgs/shop/cat-2.png"},
            "category": {"count": 8},
        },
        {
            "cid": "cat3",
            "title": "Others",
            "image": {"url": "/static/assets/imgs/shop/cat-3.png"},
            "category": {"count": 5},
        },
    ]
    context = {"categories": categories}
    return render(request, 'core/category-list.html', context)

def category_product_list__view(request, cid):
    # Mock category
    category = {"cid": cid, "title": "Vegetables" if cid == "cat1" else "Meat" if cid == "cat2" else "Others"}
    # Mock products
    products = [
        {
            "id": 1,
            "pid": "p1",
            "title": "Food 1",
            "image": {"url": "/static/assets/imgs/shop/product-1-1.jpg"},
            "category": {"title": category["title"]},
            "vendor": {"title": "FreshFarm"},
            "price": 10000,
            "old_price": 12000,
            "reviews": {"all": {"count": 5}},
            "get_precentage": 17,
        },
        {
            "id": 2,
            "pid": "p2",
            "title": "Food 2",
            "image": {"url": "/static/assets/imgs/shop/product-2-1.jpg"},
            "category": {"title": category["title"]},
            "vendor": {"title": "VeggieWorld"},
            "price": 12000,
            "old_price": 15000,
            "reviews": {"all": {"count": 2}},
            "get_precentage": 20,
        },
    ]
    context = {
        "category": category,
        "products": products,
    }
    return render(request, "core/category-product-list.html", context)