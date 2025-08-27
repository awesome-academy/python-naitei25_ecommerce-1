from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Product, wishlist_model, Category, Vendor # Thay 'core' bằng tên app của bạn

# Giả định bạn đã có model Category và Vendor
# Nếu không, bạn có thể bỏ qua việc tạo chúng nếu field là nullable
User = get_user_model()
class WishlistTestCase(TestCase):
    def setUp(self):
        """
        Phương thức này sẽ chạy trước mỗi test case.
        Chúng ta tạo ra các đối tượng cần thiết ở đây.
        """
        # 1. Tạo một Client để giả lập các request HTTP
        self.client = Client()

        # 2. Tạo một user để test
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='testpassword'
        )
        # 3. Tạo một vài sản phẩm để thêm vào wishlist
        # Giả sử Category và Vendor có thể là null, nếu không bạn cần tạo chúng trước
        self.product1 = Product.objects.create(
            title="Sản phẩm 1",
            amount=100.00,
        )
        self.product2 = Product.objects.create(
            title="Sản phẩm 2",
            amount=200.00,
        )
        
        # 4. (Tùy chọn) Tạo sẵn một item trong wishlist cho user
        self.wishlist_item = wishlist_model.objects.create(
            user=self.user,
            product=self.product2
        )
    def test_wishlist_view_authenticated(self):
        """Kiểm tra view wishlist khi người dùng đã đăng nhập."""
        # Đăng nhập user đã tạo trong setUp
        login_successful = self.client.login(email='test@example.com', password='testpassword')
                
        # Gọi view thông qua URL name
        response = self.client.get(reverse('core:wishlist'))

        # 1. Kiểm tra request thành công (status code 200 OK)
        self.assertEqual(response.status_code, 200)
        
        # 2. Kiểm tra template được sử dụng là đúng
        self.assertTemplateUsed(response, 'core/wishlist.html')
        
        # 3. Kiểm tra context có chứa danh sách wishlist ('w')
        self.assertIn('w', response.context)
        
        # 4. Kiểm tra số lượng item trong wishlist là đúng (1 item đã tạo trong setUp)
        self.assertEqual(len(response.context['w']), 1)
        
        # 5. Kiểm tra item trong context có đúng là sản phẩm 2 không
        self.assertEqual(response.context['w'][0].product, self.product2)

    def test_wishlist_view_unauthenticated(self):
        """Kiểm tra view wishlist khi người dùng chưa đăng nhập."""
        response = self.client.get(reverse('core:wishlist'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/user/sign-in/?next=/wishlist/')
    def test_add_to_wishlist_new_item(self):
        """Kiểm tra thêm sản phẩm mới vào wishlist."""
        login_successful = self.client.login(email='test@example.com', password='testpassword')
        
        # Kiểm tra số lượng wishlist item trước khi thêm
        initial_count = wishlist_model.objects.filter(user=self.user).count()
        self.assertEqual(initial_count, 1) # Đã có 1 item từ setUp
        
        # Gọi API để thêm product1 (chưa có trong wishlist)
        response = self.client.get(reverse('core:add-to-wishlist'), {'id': self.product1.pid})

        # 1. Kiểm tra request thành công
        self.assertEqual(response.status_code, 200)
        
        # 2. Kiểm tra số lượng wishlist item đã tăng lên 1
        self.assertEqual(wishlist_model.objects.filter(user=self.user).count(), initial_count + 1)
        
        # 3. Kiểm tra nội dung JSON trả về
        data = response.json()
        self.assertTrue(data['bool'])
        self.assertEqual(data['status'], 'created')
        self.assertEqual(data['count'], 2)

    def test_add_to_wishlist_existing_item(self):
        """Kiểm tra thêm lại sản phẩm đã có trong wishlist."""
        login_successful = self.client.login(email='test@example.com', password='testpassword')
        
        initial_count = wishlist_model.objects.filter(user=self.user).count()
        
        # Gọi API để thêm product2 (đã có trong wishlist từ setUp)
        response = self.client.get(reverse('core:add-to-wishlist'), {'id': self.product2.pid})

        # 1. Kiểm tra request thành công
        self.assertEqual(response.status_code, 200)
        
        # 2. Kiểm tra số lượng wishlist item không thay đổi
        self.assertEqual(wishlist_model.objects.filter(user=self.user).count(), initial_count)
        
        # 3. Kiểm tra nội dung JSON trả về status là "exists"
        data = response.json()
        self.assertTrue(data['bool'])
        self.assertEqual(data['status'], 'exists')
        self.assertEqual(data['count'], 1)
    def test_remove_from_wishlist(self):
        """Kiểm tra xóa một item khỏi wishlist."""
        login_successful = self.client.login(email='test@example.com', password='testpassword')

        # Lấy ID của wishlist item đã tạo trong setUp
        wishlist_item_id = self.wishlist_item.id
        
        initial_count = wishlist_model.objects.filter(user=self.user).count()
        self.assertEqual(initial_count, 1)

        # Gọi API để xóa item này
        # Chú ý: URL param của bạn tên là 'pid' nhưng giá trị là ID của wishlist_model
        response = self.client.get(reverse('core:remove-from-wishlist'), {'pid': wishlist_item_id})

        # 1. Kiểm tra request thành công
        self.assertEqual(response.status_code, 200)

        # 2. Kiểm tra xem item đã thực sự bị xóa khỏi database chưa
        self.assertEqual(wishlist_model.objects.filter(user=self.user).count(), initial_count - 1)
        self.assertFalse(wishlist_model.objects.filter(id=wishlist_item_id).exists())

        # 3. Kiểm tra nội dung JSON trả về (tùy vào logic của bạn)
        data = response.json()
        self.assertIn('data', data)
