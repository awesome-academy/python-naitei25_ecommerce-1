from django import views
from django.urls import path, include
from core.views import product_list_view, about_us, customer_dashboard, index, checkout, payment_completed_view, payment_failed_view,search_view,product_detail_view

app_name = "core"

urlpatterns = [
    path("", index, name="index"),
    path("dashboard/", customer_dashboard, name="dashboard"),
    path("checkout/", checkout, name="checkout"),
    path("payment-completed/", payment_completed_view, name="payment-completed"),
    path("payment-failed/", payment_failed_view, name="payment-failed"),
    path("products/", product_list_view, name="product-list"),
    path("search/", search_view, name="search"),
    path("product/<pid>/", product_detail_view, name="product-detail")
]
