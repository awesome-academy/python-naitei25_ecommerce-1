from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.http import JsonResponse
from .models import Product
from django.template.loader import render_to_string
from django.db.models import Avg
from core.models import ProductReview

# Create your views here.
def index(request):
    # bannanas = Product.objects.all().order_by("-id")
    # products = Product.objects.filter(product_status="published", featured=True).order_by("-id")

    # context = {
    #     "products":products
    # }
    return render(request, 'core/index.html')

def cart_view(request):
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
        return render(request, "core/cart.html", {
            "cart_data": request.session['cart_data_obj'],
            'totalcartitems': len(request.session['cart_data_obj']),
            'cart_total_amount': cart_total_amount
        })
    else:
        messages.warning(request, "Your cart is empty")
        return redirect("core:index")
    
def add_to_cart(request):
    product_id = str(request.GET.get('id'))  # an toàn hơn
    title = request.GET.get('title')
    qty = int(request.GET.get('qty'))
    price = float(request.GET.get('price'))
    image = request.GET.get('image')
    pid = request.GET.get('pid')

    cart_product = {
        product_id: {
            'title': title,
            'qty': qty,
            'price': price,
            'image': image,
            'pid': pid,
        }
    }

    if 'cart_data_obj' in request.session:
        cart_data = request.session['cart_data_obj']
        if product_id in cart_data:
            cart_data[product_id]['qty'] = int(cart_data[product_id]['qty']) + qty

        else:
            cart_data.update(cart_product)

        request.session['cart_data_obj'] = cart_data
    else:
        request.session['cart_data_obj'] = cart_product

    return JsonResponse({
        "data": request.session['cart_data_obj'],
        "totalcartitems": len(request.session['cart_data_obj'])
    })
def delete_item_from_cart(request):
    product_id = str(request.GET.get('id'))

    cart_data = request.session.get('cart_data_obj', {})

    if product_id in cart_data:
        del cart_data[product_id]
        request.session['cart_data_obj'] = cart_data

    cart_total_amount = sum(
        int(item['qty']) * float(item['price'])
        for item in cart_data.values()
    )

    context_html = render_to_string("core/async/cart-list.html", {
        "cart_data": cart_data,
        "totalcartitems": len(cart_data),
        "cart_total_amount": cart_total_amount
    })
    return HttpResponse(context_html)

from django.template.loader import render_to_string
from django.http import HttpResponse

def update_cart(request):
    product_id = str(request.GET.get('id'))
    product_qty = request.GET.get('qty')

    cart_data = request.session.get('cart_data_obj', {})

    if product_id in cart_data:
        cart_data[product_id]['qty'] = int(product_qty)
        request.session['cart_data_obj'] = cart_data

    # Tính lại tổng tiền
    cart_total_amount = sum(int(item['qty']) * float(item['price']) for item in cart_data.values())

    # Render lại HTML
    context_html = render_to_string("core/async/cart-list.html", {
        "cart_data": cart_data,
        "totalcartitems": len(cart_data),
        "cart_total_amount": cart_total_amount
    })

    return HttpResponse(context_html)

def ajax_add_review(request, pid):
    product = Product.objects.get(pk=pid)
    user = request.user 

    review = ProductReview.objects.create(
        user=user,
        product=product,
        review = request.POST['review'],
        rating = request.POST['rating'],
    )

    context = {
        'user': user.username,
        'review': request.POST['review'],
        'rating': request.POST['rating'],
    }

    average_reviews = ProductReview.objects.filter(product=product).aggregate(rating=Avg("rating"))

    return JsonResponse(
       {
         'bool': True,
        'context': context,
        'average_reviews': average_reviews
       }
    )
