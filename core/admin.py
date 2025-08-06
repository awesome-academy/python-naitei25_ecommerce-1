from django.contrib import admin
from cloudinary.models import CloudinaryField
from core.models import Category, Product, Vendor, CartOrder, CartOrderProducts, ProductReview, Address, Image
from django.contrib import admin
from .models import (
    Address, Image, Vendor, Coupon, CouponUser,
    Category, Product, ProductReview, ReturnRequest,
    CartOrder, CartOrderProducts
)
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'mobile', 'status')
    list_filter = ('status',)
    search_fields = ('user__username', 'address', 'mobile')


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('object_type', 'object_id', 'image', 'is_primary', 'uploaded_at')
    list_filter = ('object_type', 'is_primary')
    search_fields = ('object_id',)


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('vid', 'title', 'user', 'shipping_on_time', 'authentic_rating', 'warranty_period')
    list_filter = ('shipping_on_time',)
    search_fields = ('title', 'vid', 'user__username')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'vendor', 'discount', 'expiry_date', 'active')
    list_filter = ('active', 'expiry_date')
    search_fields = ('code', 'vendor__title')


@admin.register(CouponUser)
class CouponUserAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'user')
    search_fields = ('coupon__code', 'user__username')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('cid', 'title', 'parent')
    search_fields = ('cid', 'title')
    list_filter = ('parent',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('pid', 'title', 'category', 'vendor', 'amount', 'product_status', 'in_stock', 'featured')
    list_filter = ('product_status', 'in_stock', 'featured')
    search_fields = ('title', 'pid', 'category__title', 'vendor__title')
    autocomplete_fields = ['category', 'vendor']


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'date')
    list_filter = ('rating', 'date')
    search_fields = ('user__username', 'product__title')


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'order_product', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'order_product__item')


@admin.register(CartOrder)
class CartOrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'vendor', 'amount', 'paid_status', 'order_status', 'order_date')
    list_filter = ('paid_status', 'order_status')
    search_fields = ('user__username', 'vendor__title')


@admin.register(CartOrderProducts)
class CartOrderProductsAdmin(admin.ModelAdmin):
    list_display = ('order', 'item', 'qty', 'price', 'total')
    search_fields = ('order__user__username', 'item')
# Register your models here.

