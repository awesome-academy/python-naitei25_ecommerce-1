from core.models import *
from django.db.models import Min, Max

def default(request):
    categories = Category.objects.all()
    vendors = Vendor.objects.all()
    min_max_price = Product.objects.aggregate(Min('amount'), Max('amount'))
    return {
        'categories': categories,
        'vendors': vendors,
        'min_max_price': min_max_price,
    }
def wishlist_count(request):
    if request.user.is_authenticated:
        count = wishlist_model.objects.filter(user=request.user).count()
    else:
        count = 0
    return {"wishlist_count": count}
