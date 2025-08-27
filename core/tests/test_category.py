from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest import mock
# Thay 'core.models' bằng đường dẫn đúng đến models của bạn
from core.models import Category, Product, Image, Vendor

# Giả định các hằng số này đã được định nghĩa
# Nếu không, hãy thay thế bằng giá trị thực tế
PRODUCT_STATUS_PUBLISHED = 'published'
PRODUCT_STATUS_DRAFT = 'draft'
class CategoryTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Phương thức này chạy MỘT LẦN trước tất cả các test trong class.
        """
        super().setUpClass()
        # Đảm bảo chuỗi patch này là chính xác tuyệt đối
        cls.uploader_patcher = mock.patch('cloudinary.uploader.upload')
        cls.mock_upload = cls.uploader_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """
        Phương thức này chạy MỘT LẦN sau tất cả các test trong class.
        """
        super().tearDownClass()
        cls.uploader_patcher.stop()

    def setUp(self):
        """
        Phương thức này chạy trước mỗi test case.
        """
        self.mock_upload.return_value = {
            'public_id': 'dummy_id_123',
            'version': '1234567890',
            'secure_url': 'https://example.com/dummy_image.jpg',
            'type': 'upload',
            'resource_type': 'image'
        }
        self.client = Client()
        self.vendor = Vendor.objects.create(
            vid="test-vendor",
            title="Nhà cung cấp Test",
            description="Mô tả cho nhà cung cấp test.",
            address="123 Đường Test, Hà Nội",
            contact="0123456789",
            chat_resp_time=5,          # ví dụ: 5 phút
            shipping_on_time=98,       # ví dụ: 98%
            authentic_rating=4.8,      # ví dụ: 4.8 sao
            days_return=7,             # ví dụ: 7 ngày
            warranty_period=12         # ví dụ: 12 tháng
        )

        # 1. Tạo các Category
        self.category1 = Category.objects.create(cid="cat1", title="Điện tử")
        self.category2 = Category.objects.create(cid="cat2", title="Thời trang")

        # 2. Tạo các Product thuộc về Category
        self.product1_cat1 = Product.objects.create(
            category=self.category1, 
            vendor=self.vendor,
            title="Laptop ABC",
            product_status=PRODUCT_STATUS_PUBLISHED
        )
        self.product2_cat1_draft = Product.objects.create(
            category=self.category1,
            vendor=self.vendor,
            title="Điện thoại XYZ (Bản nháp)",
            product_status=PRODUCT_STATUS_DRAFT
        )
        self.product3_cat2 = Product.objects.create(
            category=self.category2,
            vendor=self.vendor,
            title="Áo thun",
            product_status=PRODUCT_STATUS_PUBLISHED
        )

        # 3. Tạo một ảnh giả để test
        # Đây là kỹ thuật tạo file giả trong bộ nhớ để test upload file/ImageField
        fake_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'some_file_content',
            content_type='image/jpeg'
        )

        # ĐOẠN CODE ĐÚNG ĐỂ TẠO IMAGE TRONG TEST
        Image.objects.create(
            object_type='Category',
            object_id=self.category1.cid,
            is_primary=True,
            image=fake_image,  # Sử dụng đúng tên trường 'image'
            alt_text="Hình ảnh danh mục điện tử"
        )    # bên trong class CategoryTestCase

    def test_category_list_view_success(self):
        """
        Kiểm tra trang danh sách category hoạt động chính xác.
        """
        # Gọi view bằng URL name
        response = self.client.get(reverse('core:category-list'))

        # 1. Kiểm tra request thành công (status code 200 OK)
        self.assertEqual(response.status_code, 200)

        # 2. Kiểm tra template được sử dụng là đúng
        self.assertTemplateUsed(response, 'core/category-list.html')

        # 3. Kiểm tra context có chứa danh sách 'categories'
        self.assertIn('categories', response.context)

        # 4. Kiểm tra số lượng category trong context có đúng là 2 không
        categories_in_context = response.context['categories']
        self.assertEqual(len(categories_in_context), 2)

        # 5. (Tùy chọn) Kiểm tra dữ liệu của một category cụ thể
        # Lấy dữ liệu của category1 từ context để kiểm tra
        cat1_data = next((cat for cat in categories_in_context if cat['cid'] == self.category1.cid), None)
        self.assertIsNotNone(cat1_data)
        self.assertEqual(cat1_data['title'], 'Điện tử')
        self.assertEqual(cat1_data['alt_text'], 'Hình ảnh danh mục điện tử')
    
    def test_category_product_list_view_success(self):
        """
        Kiểm tra trang chi tiết category hiển thị đúng sản phẩm.
        """
        # Gọi view với cid của category1
        response = self.client.get(reverse('core:category-product-list', kwargs={'cid': self.category1.cid}))

        # 1. Kiểm tra request thành công (status code 200 OK)
        self.assertEqual(response.status_code, 200)

        # 2. Kiểm tra template được sử dụng
        self.assertTemplateUsed(response, 'core/category-product-list.html')

        # 3. Kiểm tra category trong context có đúng là category1 không
        self.assertEqual(response.context['category'], self.category1)

        # 4. Kiểm tra danh sách sản phẩm trong context
        products_in_context = response.context['products']
        
        # Phải có đúng 1 sản phẩm (vì product2_cat1_draft không được published)
        self.assertEqual(len(products_in_context), 1)
        
        # Sản phẩm đó phải là product1_cat1
        self.assertIn(self.product1_cat1, products_in_context)
        
        # Sản phẩm nháp không được xuất hiện
        self.assertNotIn(self.product2_cat1_draft, products_in_context)

    def test_category_product_list_view_not_found(self):
        """
        Kiểm tra trang chi tiết category trả về 404 với cid không hợp lệ.
        """
        # Gọi view với một cid không tồn tại
        response = self.client.get(reverse('core:category-product-list', kwargs={'cid': 'invalid-cid'}))

        # View dùng get_object_or_404, nên phải trả về status code 404
        self.assertEqual(response.status_code, 404)