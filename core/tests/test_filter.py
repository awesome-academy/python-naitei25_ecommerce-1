from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal

# Thay thế bằng đường dẫn import đúng của bạn
from core.models import Product, Category, Vendor

PRODUCT_STATUS_PUBLISHED = 'published'
PRODUCT_STATUS_DRAFT = 'draft'

class FilterTestCase(TestCase):
    def setUp(self):
        """
        Tạo dữ liệu mẫu đa dạng để test chức năng filter.
        """
        self.client = Client()

        # Tạo 2 Category
        self.cat_dientu = Category.objects.create(cid="dientu", title="Điện tử")
        self.cat_sach = Category.objects.create(cid="sach", title="Sách")

        # Tạo 2 Vendor
        self.vendor_a = Vendor.objects.create(
            vid="vendor-a",
            title="Nhà cung cấp A",
            description="Mô tả cho nhà cung cấp A.",
            address="123 Đường A, Hà Nội",
            contact="0123456789",
            chat_resp_time=5,
            shipping_on_time=98,
            authentic_rating=4.8,
            days_return=7,
            warranty_period=12
        )
        self.vendor_b = Vendor.objects.create(
            vid="vendor-b",
            title="Nhà cung cấp B",
            description="Mô tả cho nhà cung cấp B.",
            address="456 Đường B, TP.HCM",
            contact="0987654321",
            chat_resp_time=10,
            shipping_on_time=95,
            authentic_rating=4.5,
            days_return=14,
            warranty_period=6
        )
        # Tạo các sản phẩm
        # Lưu ý: Cần điền đủ các trường bắt buộc cho Vendor và Product
        
        # Sản phẩm 1: Điện tử, Vendor A, Giá 1500
        self.prod1 = Product.objects.create(
            title="Laptop", category=self.cat_dientu, vendor=self.vendor_a,
            amount=Decimal("1500.00"), product_status=PRODUCT_STATUS_PUBLISHED
        )
        # Sản phẩm 2: Điện tử, Vendor B, Giá 2500
        self.prod2 = Product.objects.create(
            title="Smartphone", category=self.cat_dientu, vendor=self.vendor_b,
            amount=Decimal("2500.00"), product_status=PRODUCT_STATUS_PUBLISHED
        )
        # Sản phẩm 3: Sách, Vendor A, Giá 50
        self.prod3 = Product.objects.create(
            title="Tiểu thuyết", category=self.cat_sach, vendor=self.vendor_a,
            amount=Decimal("50.00"), product_status=PRODUCT_STATUS_PUBLISHED
        )
        # Sản phẩm 4: Sách, Vendor B, Giá 150
        self.prod4 = Product.objects.create(
            title="Sách kỹ năng", category=self.cat_sach, vendor=self.vendor_b,
            amount=Decimal("150.00"), product_status=PRODUCT_STATUS_PUBLISHED
        )
        # Sản phẩm 5: Điện tử, Vendor A, Giá 1000 (chưa published)
        self.prod5_draft = Product.objects.create(
            title="Máy tính bảng (nháp)", category=self.cat_dientu, vendor=self.vendor_a,
            amount=Decimal("1000.00"), product_status=PRODUCT_STATUS_DRAFT
        )

    def test_no_filters(self):
        """Kiểm tra không có filter nào được áp dụng, trả về tất cả sản phẩm published."""
        response = self.client.get(reverse('core:filter-product'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Phải có 4 sản phẩm đã published
        self.assertEqual(data['count'], 4)

    def test_filter_by_single_category(self):
        """Kiểm tra filter theo một category."""
        params = {'category': self.cat_dientu.cid}
        response = self.client.get(reverse('core:filter-product'), params)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Có 2 sản phẩm thuộc danh mục Điện tử
        self.assertEqual(data['count'], 2)

    def test_filter_by_multiple_vendors(self):
        """Kiểm tra filter theo nhiều vendor."""
        # Django's test client xử lý list param bằng cách truyền vào một list
        params = {'vendor': [self.vendor_a.vid, self.vendor_b.vid]}
        response = self.client.get(reverse('core:filter-product'), params)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Tất cả 4 sản phẩm published đều thuộc 2 vendor này
        self.assertEqual(data['count'], 4)

    def test_filter_by_min_price(self):
        """Kiểm tra filter theo giá tối thiểu."""
        params = {'min_price': '1000'}
        response = self.client.get(reverse('core:filter-product'), params)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Có 2 sản phẩm giá >= 1000 (prod1 và prod2)
        self.assertEqual(data['count'], 2)

    def test_filter_by_max_price(self):
        """Kiểm tra filter theo giá tối đa."""
        params = {'max_price': '200'}
        response = self.client.get(reverse('core:filter-product'), params)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Có 2 sản phẩm giá <= 200 (prod3 và prod4)
        self.assertEqual(data['count'], 2)

    def test_filter_by_price_range(self):
        """Kiểm tra filter theo khoảng giá."""
        params = {'min_price': '100', 'max_price': '2000'}
        response = self.client.get(reverse('core:filter-product'), params)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Có 3 sản phẩm trong khoảng giá này (prod1, prod3, prod4)
        self.assertEqual(data['count'], 2)
    
    def test_filter_combination(self):
        """Kiểm tra filter kết hợp category và vendor."""
        params = {
            'category': self.cat_sach.cid,
            'vendor': self.vendor_a.vid
        }
        response = self.client.get(reverse('core:filter-product'), params)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Chỉ có 1 sản phẩm là sách của vendor A (prod3)
        self.assertEqual(data['count'], 1)

    def test_filter_no_results(self):
        """Kiểm tra trường hợp filter không trả về kết quả nào."""
        params = {'min_price': '9999'}
        response = self.client.get(reverse('core:filter-product'), params)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 0)