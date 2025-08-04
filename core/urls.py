from django import views
from django.urls import path, include
from core.views import index, cart_view, add_to_cart, delete_item_from_cart, update_cart, ajax_add_review
app_name = "core"

urlpatterns = [

    # Homepage
    path("", index, name="index"),
    path("cart/", cart_view, name="cart"),
    path("add-to-cart/", add_to_cart, name="add-to-cart"),
    path("delete-from-cart/", delete_item_from_cart, name="delete-from-cart"),
    path("update-cart/", update_cart, name="update-cart"),
    path("ajax-add-review/<int:pid>/", ajax_add_review, name="ajax-add-review"),

]