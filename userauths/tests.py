from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

User = get_user_model()

class ForgotPasswordViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_request_renders_form(self):
        url = reverse("userauths:forgot-password")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    @patch("userauths.views.is_valid_email", return_value=True)
    @patch("userauths.views.send_password_reset_email")
    def test_post_valid_email_existing_user(self, mock_send, mock_is_valid):
        user = User.objects.create_user(username="john", email="john@example.com", password="12345")

        url = reverse("userauths:forgot-password")
        response = self.client.post(url, {"email": "john@example.com"})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("userauths:sign-in"))

        mock_send.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Please check your email" in str(m) for m in messages))

    @patch("userauths.views.is_valid_email", return_value=True)
    def test_post_valid_email_not_existing_user(self, mock_is_valid):
        url = reverse("userauths:forgot-password")
        response = self.client.post(url, {"email": "nouser@example.com"})

        self.assertIn(response.status_code, [200, 302])
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("not registered" in str(m) for m in messages))

    
