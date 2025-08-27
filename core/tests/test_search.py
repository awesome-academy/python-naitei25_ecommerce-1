from django.test import TestCase, Client
from django.urls import reverse

# Thay thế bằng đường dẫn import đúng của bạn
from core.models import Product, Category, Vendor

# Giả sử bạn có các hằng số này
PRODUCT_STATUS_PUBLISHED = 'published'
PRODUCT_STATUS_DRAFT = 'draft'

class SearchTestCase(TestCase):
    def setUp(self):
        """
        Tạo dữ liệu mẫu để test chức năng tìm kiếm.
        """
        self.client = Client()

        # Tạo các đối tượng phụ thuộc (Category, Vendor)
        self.category = Category.objects.create(cid="cat-test", title="Danh mục Test")
        self.vendor = Vendor.objects.create(
            vid="vendor-test",
            title="Nhà cung cấp Test",
            description="Mô tả.",
            address="123 Đường Test",
            contact="0123456789",
            chat_resp_time=5,
            shipping_on_time=98,
            authentic_rating=4.8,
            days_return=7,
            warranty_period=12
        )

        # Tạo các sản phẩm để test
        # 1. Sản phẩm có từ khóa "Laptop" trong tiêu đề, đã published
        self.product_match_title = Product.objects.create(
            title="Laptop Gaming ABC",
            category=self.category,
            vendor=self.vendor,
            product_status=PRODUCT_STATUS_PUBLISHED
        )

        # 2. Sản phẩm có từ khóa "mạnh mẽ" trong mô tả, đã published
        self.product_match_desc = Product.objects.create(
            title="PC Đồ họa",
            description="Một chiếc PC với bộ xử lý rất mạnh mẽ.",
            category=self.category,
            vendor=self.vendor,
            product_status=PRODUCT_STATUS_PUBLISHED
        )

        # 3. Sản phẩm không chứa từ khóa nào liên quan, đã published
        self.product_no_match = Product.objects.create(
            title="Bàn phím cơ",
            category=self.category,
            vendor=self.vendor,
            product_status=PRODUCT_STATUS_PUBLISHED
        )
        
        # 4. Sản phẩm có từ khóa "Laptop" nhưng chưa published (draft)
        self.product_unpublished_match = Product.objects.create(
            title="Laptop Văn phòng XYZ",
            category=self.category,
            vendor=self.vendor,
            product_status=PRODUCT_STATUS_DRAFT
        )
    def test_search_with_matching_query(self):
        """
        Kiểm tra tìm kiếm với từ khóa hợp lệ (`q=Laptop`).
        """
        # Thực hiện request GET tới trang search với tham số q
        response = self.client.get(reverse('core:search'), {'q': 'Laptop'})

        # 1. Kiểm tra request thành công
        self.assertEqual(response.status_code, 200)

        # 2. Kiểm tra template được sử dụng
        self.assertTemplateUsed(response, 'core/search.html')

        # 3. Kiểm tra các biến trong context
        self.assertEqual(response.context['query'], 'Laptop')
        self.assertEqual(response.context['result_count'], 1)

        # 4. Kiểm tra danh sách sản phẩm trả về
        products_in_context = response.context['products']
        self.assertIn(self.product_match_title, products_in_context)
        
        # 5. Đảm bảo các sản phẩm không liên quan không xuất hiện
        self.assertNotIn(self.product_match_desc, products_in_context)
        self.assertNotIn(self.product_no_match, products_in_context)
        self.assertNotIn(self.product_unpublished_match, products_in_context)

    def test_search_with_no_results(self):
        """
        Kiểm tra tìm kiếm với từ khóa không có kết quả.
        """
        response = self.client.get(reverse('core:search'), {'q': 'nonexistent_keyword'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['query'], 'nonexistent_keyword')
        self.assertEqual(response.context['result_count'], 0)
        self.assertEqual(len(response.context['products']), 0)

    def test_search_without_query(self):
        """
        Kiểm tra trang search khi không có tham số 'q'.
        """
        response = self.client.get(reverse('core:search'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['query'], '') # Query phải là chuỗi rỗng
        
        # Phải trả về tất cả sản phẩm đã published (3 sản phẩm)
        self.assertEqual(response.context['result_count'], 3)
        self.assertEqual(len(response.context['products']), 3)

    def test_search_case_insensitive(self):
        """
        Kiểm tra tìm kiếm không phân biệt chữ hoa/thường.
        """
        response = self.client.get(reverse('core:search'), {'q': 'laptop'}) # "laptop" chữ thường

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['result_count'], 1)
        self.assertIn(self.product_match_title, response.context['products'])