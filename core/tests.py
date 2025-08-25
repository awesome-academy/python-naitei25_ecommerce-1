from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Product, Vendor, Category

User = get_user_model()


class TagListTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Tạo user và vendor
        self.user = User.objects.create_user(
            email="vendor@example.com",
            username="vendor",
            password="testpass",
        )
        self.vendor = Vendor.objects.create(
            vid="v1",
            title="Vendor 1",
            description="Test vendor",
            address="HN",
            contact="0123456789",
            chat_resp_time=10,
            shipping_on_time=95,
            authentic_rating=4.5,
            days_return=7,
            warranty_period=12,
            user=self.user,
            vendor_active=True,
        )
        self.category = Category.objects.create(cid="cat1", title="Category 1")

        # Products
        self.prod1 = Product.objects.create(
            title="Product1",
            vendor=self.vendor,
            category=self.category,
            amount=100,
            stock_count=10,
            product_status="published",
        )
        self.prod2 = Product.objects.create(
            title="Product2",
            vendor=self.vendor,
            category=self.category,
            amount=200,
            stock_count=5,
            product_status="published",
        )
        self.prod3 = Product.objects.create(
            title="Product3",
            vendor=self.vendor,
            category=self.category,
            amount=300,
            stock_count=5,
            product_status="draft",
        )

        self.prod1.tags.add("tagA")
        self.prod2.tags.add("tagB")

    def test_list_products_by_tag(self):
        url = reverse("core:tags", args=["taga"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Product1")
        self.assertNotContains(response, "Product2")

    def test_tag_not_found_returns_404(self):
        url = reverse("core:tags", args=["notfound"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_tag_filter_is_case_insensitive(self):
        url = reverse("core:tags", args=["TaGa"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Product1")
