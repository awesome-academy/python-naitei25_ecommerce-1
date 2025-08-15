import os
from django.core.mail import send_mail


def send_activation_email(email, username, uidb64, token):
    DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")
    SITE_URL = os.environ.get("SITE_URL")
    activation_link = f"{SITE_URL}/user/activate/{uidb64}/{token}/"
    subject = "Kích hoạt tài khoản của bạn"
    message = f"Xin chào {username},\n\nVui lòng nhấn vào liên kết sau để kích hoạt tài khoản:\n{activation_link}\n\nCảm ơn!"
    send_mail(subject, message, DEFAULT_FROM_EMAIL, [email])
    