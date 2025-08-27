import calendar
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

# Thay thế bằng đường dẫn import đúng của bạn
from core.models import User, Vendor, Address, CartOrder, CartOrderProducts
from userauths.models import *
class DashboardTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Dùng setUpTestData để tạo dữ liệu chỉ một lần cho cả class,
        giúp test chạy nhanh hơn vì không phải tạo lại dữ liệu cho mỗi test.
        """
        # Tạo 2 user để kiểm tra sự cô lập dữ liệu
        cls.user1 = User.objects.create_user(
            username="user1", 
            email="user1@example.com",  # Cung cấp email duy nhất
            password="password"
        )
        cls.user2 = User.objects.create_user(
            username="user2", 
            email="user2@example.com",  # Cung cấp email duy nhất
            password="password"
        )
        
        # Tạo Vendor
        cls.vendor = Vendor.objects.create(
            vid="vendor-dash",
            title="Vendor Dashboard",
            description="Mô tả cho vendor dashboard.",
            address="123 Dashboard St, Hanoi",
            contact="0123456789",
            chat_resp_time=10,
            shipping_on_time=95,
            authentic_rating=4.7,
            days_return=10,
            warranty_period=12
        )
        # Tạo địa chỉ cho user1
        cls.address1 = Address.objects.create(user=cls.user1, address="123 Main St", mobile="111", status=True) # Địa chỉ mặc định
        cls.address2 = Address.objects.create(user=cls.user1, address="456 Oak Ave", mobile="222", status=False)

        # Tạo các đơn hàng cho user1
        # 1. Đơn hàng đang xử lý (giỏ hàng)
        cls.cart = CartOrder.objects.create(user=cls.user1, vendor=cls.vendor, amount=100, order_status='processing')

        # 2. Đơn hàng đã chốt ở tháng trước
        last_month_date = timezone.now() - timedelta(days=30)
        cls.order1 = CartOrder.objects.create(user=cls.user1, vendor=cls.vendor, amount=200, order_status='shipped')
        CartOrder.objects.filter(pk=cls.order1.pk).update(order_date=last_month_date) # Cập nhật ngày để test thống kê

        # 3. Đơn hàng đã chốt ở tháng hiện tại
        cls.order2 = CartOrder.objects.create(user=cls.user1, vendor=cls.vendor, amount=300, order_status='delivered')

    def setUp(self):
        """Hàm này chạy trước mỗi test."""
        self.client = Client()
        login_success = self.client.login(username="user1@example.com", password="password")
        self.assertTrue(login_success, "Đăng nhập trong test setUp thất bại.")


    def test_dashboard_get_view(self):
        """Kiểm tra request GET tới dashboard hiển thị đúng dữ liệu."""
        response = self.client.get(reverse('core:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dashboard.html')

        context = response.context
        
        # Kiểm tra danh sách
        self.assertEqual(len(context['carts_list']), 1)
        self.assertEqual(context['carts_list'][0], self.cart)
        
        self.assertEqual(len(context['orders_list']), 2)
        self.assertIn(self.order1, context['orders_list'])
        self.assertIn(self.order2, context['orders_list'])

        self.assertEqual(len(context['address_list']), 2)
        
        # Kiểm tra thống kê tháng (chỉ có đơn hàng đã chốt)
        self.assertEqual(len(context['month']), 2) # Có đơn ở 2 tháng khác nhau
        self.assertEqual(len(context['total_orders']), 2)
        self.assertEqual(context['total_orders'][0], 1) # Đơn tháng trước
        self.assertEqual(context['total_orders'][1], 1) # Đơn tháng này
    
    def test_dashboard_post_add_address_success(self):
        """Kiểm tra thêm địa chỉ mới thành công."""
        address_count_before = Address.objects.filter(user=self.user1).count()
        
        new_address_data = {
            "address": "789 Pine Ln",
            "mobile": "333333"
        }
        response = self.client.post(reverse('core:dashboard'), new_address_data)

        # 1. Kiểm tra redirect về trang dashboard
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:dashboard'))

        # 2. Kiểm tra số lượng địa chỉ đã tăng lên 1
        self.assertEqual(Address.objects.filter(user=self.user1).count(), address_count_before + 1)
        
        # 3. Kiểm tra địa chỉ mới đã tồn tại
        self.assertTrue(Address.objects.filter(user=self.user1, address="789 Pine Ln").exists())

    def test_dashboard_post_add_address_fail(self):
        """Kiểm tra thêm địa chỉ mới thất bại do thiếu thông tin."""
        address_count_before = Address.objects.filter(user=self.user1).count()
        
        invalid_data = {"address": "Chỉ có địa chỉ"} # Thiếu mobile
        response = self.client.post(reverse('core:dashboard'), invalid_data)

        # Kiểm tra số lượng địa chỉ không thay đổi
        self.assertEqual(Address.objects.filter(user=self.user1).count(), address_count_before)
    
    def test_make_address_default_success(self):
        """Kiểm tra API đổi địa chỉ mặc định thành công."""
        # Ban đầu, address1 là mặc định, address2 không phải
        self.assertTrue(Address.objects.get(pk=self.address1.pk).status)
        self.assertFalse(Address.objects.get(pk=self.address2.pk).status)

        params = {'id': self.address2.id}
        response = self.client.post(reverse('core:make-default-address'), params)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['boolean'])

        # Kiểm tra trạng thái trong DB đã được cập nhật đúng
        self.assertFalse(Address.objects.get(pk=self.address1.pk).status)
        self.assertTrue(Address.objects.get(pk=self.address2.pk).status)

    def test_make_address_default_missing_id(self):
        """Kiểm tra API khi thiếu 'id'."""
        response = self.client.post(reverse('core:make-default-address'))
        self.assertEqual(response.status_code, 400) # Bad Request
        self.assertFalse(response.json()['boolean'])

    def test_make_address_default_not_found(self):
        """Kiểm tra API với 'id' không tồn tại."""
        params = {'id': 99999}
        response = self.client.post(reverse('core:make-default-address'), params)
        self.assertEqual(response.status_code, 404) # Not Found
        self.assertFalse(response.json()['boolean'])

    def test_make_address_default_wrong_user(self):
        """Kiểm tra user này không thể đổi địa chỉ của user khác."""
        # Đăng nhập user2
        login_success = self.client.login(username="user2@example.com", password="password")
        self.assertTrue(login_success, "Đăng nhập user2 trong test thất bại.")
                
        # Cố gắng đổi địa chỉ của user1
        params = {'id': self.address1.id}
        response = self.client.post(reverse('core:make-default-address'), params)

        # Phải trả về lỗi 404 vì không tìm thấy địa chỉ này cho user2
        self.assertEqual(response.status_code, 404)

        # Đảm bảo trạng thái mặc định của user1 không bị thay đổi
        self.assertTrue(Address.objects.get(pk=self.address1.pk).status)
