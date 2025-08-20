from core.models import Product, Coupon
from django import forms
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .constants import (
    MAX_DIGITS_DECIMAL, DECIMAL_PLACES, MIN_PRODUCT_PRICE, MIN_PRICE_STEP,
    MIN_COUPON_CODE_LENGTH, MIN_DISCOUNT_PERCENTAGE, MAX_DISCOUNT_PERCENTAGE,
    DISCOUNT_STEP, MIN_AMOUNT_VALUE, AMOUNT_STEP, FORM_CONTROL_CLASS,
    FORM_CHECK_INPUT_CLASS, DATETIME_LOCAL_TYPE, TEXT_TRANSFORM_UPPERCASE
)

class AddProductForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _("Product Title"), "class": FORM_CONTROL_CLASS}))
    description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': _("Product Description"), "class": FORM_CONTROL_CLASS}))
    amount = forms.DecimalField(
        required=True,
        min_value=Decimal(str(MIN_PRODUCT_PRICE)),
        widget=forms.NumberInput(attrs={
            'placeholder': _("Sale Price"), 
            'class': FORM_CONTROL_CLASS,
            'step': str(MIN_PRICE_STEP)
        })
    )
    old_price = forms.DecimalField(
        decimal_places=DECIMAL_PLACES,
        max_digits=MAX_DIGITS_DECIMAL,
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': _("Old Price"),
            'class': FORM_CONTROL_CLASS,
            'step': str(MIN_PRICE_STEP),
            'min': str(MIN_AMOUNT_VALUE)
        })
    )
    type = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _("Type (e.g., Organic Cream)"), "class": FORM_CONTROL_CLASS}))
    stock_count = forms.CharField(widget=forms.NumberInput(attrs={'placeholder': _("Stock Count"), "class": FORM_CONTROL_CLASS}))
    life = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _("Product Shelf Life"), "class": FORM_CONTROL_CLASS}))
    mfd = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'placeholder': _("Manufacture Date (YYYY-MM-DD)"), "class": FORM_CONTROL_CLASS}))
    tags = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _("Tags (comma-separated)"), "class": FORM_CONTROL_CLASS}))
    image = forms.ImageField(widget=forms.FileInput(attrs={"class": FORM_CONTROL_CLASS}))

    class Meta:
        model = Product
        fields = [
            'title',
            'image',
            'description',
            'amount',
            'old_price',
            'specifications',
            'type',
            'stock_count',
            'life',
            'mfd',
            'tags',
            'digital',
            'category'
        ]

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None or amount <= MIN_AMOUNT_VALUE:
            raise forms.ValidationError(_("Price must be greater than {}").format(MIN_AMOUNT_VALUE))
        return amount

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        exclude = ['vendor']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': FORM_CONTROL_CLASS,
                'placeholder': _('Enter coupon code (e.g., DISCOUNT20)'),
                'style': TEXT_TRANSFORM_UPPERCASE
            }),
            'discount': forms.NumberInput(attrs={
                'class': FORM_CONTROL_CLASS,
                'placeholder': _('10.0'),
                'min': str(MIN_DISCOUNT_PERCENTAGE),
                'max': str(MAX_DISCOUNT_PERCENTAGE),
                'step': str(DISCOUNT_STEP)
            }),
            'expiry_date': forms.DateTimeInput(attrs={
                'class': FORM_CONTROL_CLASS,
                'type': DATETIME_LOCAL_TYPE
            }),
            'min_order_amount': forms.NumberInput(attrs={
                'class': FORM_CONTROL_CLASS,
                'placeholder': _('0.00'),
                'min': str(MIN_AMOUNT_VALUE),
                'step': str(AMOUNT_STEP)
            }),
            'max_discount_amount': forms.NumberInput(attrs={
                'class': FORM_CONTROL_CLASS,
                'placeholder': _('100.00'),
                'min': str(MIN_AMOUNT_VALUE),
                'step': str(AMOUNT_STEP)
            }),
            'active': forms.CheckboxInput(attrs={
                'class': FORM_CHECK_INPUT_CLASS
            }),
            'apply_once_per_user': forms.CheckboxInput(attrs={
                'class': FORM_CHECK_INPUT_CLASS
            })
        }
    
    def clean_code(self):
        code = self.cleaned_data['code'].upper().strip()
        if not code:
            raise forms.ValidationError(_("Coupon code cannot be empty."))
        
        if len(code) < MIN_COUPON_CODE_LENGTH:
            raise forms.ValidationError(_("Coupon code must be at least {} characters long.").format(MIN_COUPON_CODE_LENGTH))
        
        # Check for duplicate code
        if self.instance.pk:
            # Editing existing coupon
            if Coupon.objects.filter(code=code).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError(_("This coupon code already exists."))
        else:
            # Creating new coupon
            if Coupon.objects.filter(code=code).exists():
                raise forms.ValidationError(_("This coupon code already exists."))
        return code
    
    def clean_expiry_date(self):
        expiry_date = self.cleaned_data['expiry_date']
        if expiry_date <= timezone.now():
            raise forms.ValidationError(_("Expiry date must be in the future."))
        return expiry_date
    
    def clean_discount(self):
        discount = self.cleaned_data.get('discount')
        if discount is None:
            raise forms.ValidationError(_("Discount percentage cannot be empty."))
        if discount < MIN_DISCOUNT_PERCENTAGE:
            raise forms.ValidationError(_("Discount percentage cannot be negative."))
        if discount > MAX_DISCOUNT_PERCENTAGE:
            raise forms.ValidationError(_("Discount percentage cannot exceed {}%.").format(MAX_DISCOUNT_PERCENTAGE))
        return discount
    
    def clean(self):
        cleaned_data = super().clean()
        discount = cleaned_data.get('discount')
        max_discount = cleaned_data.get('max_discount_amount')
        min_order = cleaned_data.get('min_order_amount')
        
        if max_discount and min_order and max_discount > min_order:
            raise forms.ValidationError(_("Maximum discount amount cannot be greater than the minimum order amount."))
        
        return cleaned_data
