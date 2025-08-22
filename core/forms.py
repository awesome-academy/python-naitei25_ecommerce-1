from django import forms
from core.models import ProductReview
from .models import Vendor
from django.utils.translation import gettext_lazy as _

class ProductReviewForm(forms.ModelForm):
    review = forms.CharField(widget=forms.Textarea(attrs={'placeholder': "Write review"}))
    
    class Meta:
        model = ProductReview
        fields = ['review', 'rating']


class VendorRegisterForm(forms.ModelForm):
    image = forms.ImageField(
        required=False,
        label=_("Shop Logo"),
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"})
    )

    class Meta:
        model = Vendor
        fields = [
            "title",
            "description",
            "address",
            "contact",
            "chat_resp_time",
            "shipping_on_time",
            "authentic_rating",
            "days_return",
            "warranty_period",
        ]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": _("Enter your shop name"),
                "required": True
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": _("Tell customers about your shop"),
                "rows": 4,
                "required": True
            }),
            "address": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": _("Your shop address"),
                "required": True
            }),
            "contact": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": _("Phone number"),
                "required": True
            }),
            "chat_resp_time": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "value": 60
            }),
            "shipping_on_time": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "max": 100,
                "value": 95
            }),
            "authentic_rating": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
                "max": 5,
                "step": 0.1,
                "value": 5.0
            }),
            "days_return": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
                "value": 7
            }),
            "warranty_period": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
                "value": 12
            }),
        }
