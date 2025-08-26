from django.urls import path
from userauths import views

app_name = "userauths"

urlpatterns = [
    path("sign-up/", views.register_view, name="sign-up"),
    path("sign-in/", views.login_view, name="sign-in"),
    path("sign-out/", views.logout_view, name="sign-out"),
    path("activate/<uidb64>/<token>/", views.activate_account, name="activate"),
    path("vendor-register/", views.vendor_register_view, name="vendor-register"),

    path("profile/update/", views.profile_update, name="profile-update"),
    path("forgot-password/", views.forgot_password_view, name="forgot-password"),
    path("reset-password/<uidb64>/<token>/", views.reset_password_view, name="reset-password"),
]
