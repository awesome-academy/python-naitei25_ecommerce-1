from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from django.conf import settings
from taggit.managers import TaggableManager
from django_ckeditor_5.fields import CKEditor5Field
from django.utils import timezone
from userauths.models import User
# Create your models here.
STATUS_CHOICE = (
    ("processing", "Processing"),
    ("shipped", "Shipped"),
    ("delivered", "Delivered"),
)


STATUS = (
    ("draft", "Draft"),
    ("disabled", "Disabled"),
    ("rejected", "Rejected"),
    ("in_review", "In Review"),
    ("published", "Published"),
)


RATING = (
    (1,  "★☆☆☆☆"),
    (2,  "★★☆☆☆"),
    (3,  "★★★☆☆"),
    (4,  "★★★★☆"),
    (5,  "★★★★★"),
)
ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('admin', 'Admin'),
    )
def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    mobile = models.CharField(max_length=300, null=True)
    address = models.CharField(max_length=100, null=True)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Address"

class Image(models.Model):
    url = models.URLField(max_length=500)
    alt_text = models.CharField(max_length=255, null=True, blank=True)
    object_type = models.CharField(max_length=50)  # e.g., 'Product', 'Category', 'Vendor'
    object_id = models.CharField(max_length=50)    # e.g., pid, cid, vid
    is_primary = models.BooleanField(default=False)
    image_type = models.CharField(max_length=50, null=True, blank=True)  # thumbnail, cover, etc.
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.object_type} - {self.object_id}"

class Vendor(models.Model):
    vid = models.CharField(max_length=100, primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    address = models.CharField(max_length=500)
    contact = models.CharField(max_length=100)
    chat_resp_time = models.CharField(max_length=50)
    shipping_on_time = models.CharField(max_length=50)
    authentic_rating = models.CharField(max_length=50)
    days_return = models.CharField(max_length=50)
    warranty_period = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'vendor'

class Coupon(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    code = models.CharField(max_length=50, unique=True)
    discount = models.FloatField()
    active = models.BooleanField(default=True)
    expiry_date = models.DateTimeField()
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    apply_once_per_user = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    class Meta:
        db_table = 'coupon'

class CouponUser(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = 'coupon_user'
        unique_together = ('coupon', 'user')
        
class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=20,
                        prefix="cat", alphabet="abcdefgh12345")
    title = models.CharField(max_length=100, default="Food")
    image = models.ImageField(upload_to="category", default="category.jpg")

    class Meta:
        verbose_name_plural = "Categories"
    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def product_count(self):
        return Product.objects.filter(category=self).count()

    def __str__(self):
        return self.title

class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefgh12345", primary_key=True)

    category = models.ForeignKey(
        'Category', on_delete=models.SET_NULL, null=True, related_name="products"
    )
    vendor = models.ForeignKey(
        'Vendor', on_delete=models.SET_NULL, null=True, related_name="products"
    )

    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    old_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    specifications = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    stock_count = models.CharField(max_length=100, null=True, blank=True)
    life = models.CharField(max_length=100, null=True, blank=True)
    mfd = models.DateTimeField(null=True, blank=True)

    product_status = models.CharField(max_length=50, default="in_review")
    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    digital = models.BooleanField(default=False)

    sku = ShortUUIDField(unique=True, length=4, max_length=10, prefix="sku", alphabet="1234567890")

    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)

    rating_avg = models.FloatField(default=0.0)

    class Meta:
        verbose_name_plural = "Products"

class ProductReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name="reviews")
    review = models.TextField()
    rating = models.IntegerField(choices=RATING, default=None)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Reviews"

from django.db import models
from django.contrib.auth.models import User

class ReturnRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='return_requests')
    order_product = models.ForeignKey('CartOrderProducts', on_delete=models.CASCADE, related_name='return_requests')
    reason = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ReturnRequest #{self.pk} by {self.user.username}"
    
class CartOrder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)

    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)

    price = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")
    saved = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")
    coupons = models.ManyToManyField("core.Coupon", blank=True)
    
    shipping_method = models.CharField(max_length=100, null=True, blank=True)
    tracking_id = models.CharField(max_length=100, null=True, blank=True)
    tracking_website_address = models.CharField(max_length=100, null=True, blank=True)


    paid_status = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    product_status = models.CharField(choices=STATUS_CHOICE, max_length=30, default="processing")
    sku = ShortUUIDField(null=True, blank=True, length=5,prefix="SKU", max_length=20, alphabet="1234567890")
    oid = ShortUUIDField(null=True, blank=True, length=8, max_length=20, alphabet="1234567890")
    stripe_payment_intent = models.CharField(max_length=1000, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Cart Order"


class CartOrderProducts(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length=200)
    product_status = models.CharField(max_length=200)
    item = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    qty = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")
    total = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")

    class Meta:
        verbose_name_plural = "Cart Order Items"

    def order_img(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" />' % (self.image))

