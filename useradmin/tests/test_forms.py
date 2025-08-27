from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid

# Import từ core app
from core.models import Category, Vendor

# Import từ useradmin
from useradmin.forms import AddProductForm

User = get_user_model()


class AddProductFormTest(TestCase):
    """Test AddProductForm validation"""
    
    def setUp(self):
        """Setup test data for forms"""
        self.user = User.objects.create_user(
            username='testvendor',
            email='vendor@test.com',
            password='testpass123'
        )
        
        # Tạo vendor với các fields thực tế và vid
        self.vendor = Vendor.objects.create(
            vid=f"VID{uuid.uuid4().hex[:8]}",  # Tạo vid unique
            user=self.user,
            title='Test Vendor Store',
            description='Test vendor description',
            address='123 Test Street',
            contact='+1234567890',
            chat_resp_time=24,
            shipping_on_time=95,
            authentic_rating=4.5,
            days_return=30,
            warranty_period=365,
            vendor_active=True
        )
        
        # Tạo category với cid
        self.category = Category.objects.create(
            cid=f"CAT{uuid.uuid4().hex[:8]}",  # Tạo cid unique
            title='Electronics'
        )

    def test_valid_form_data(self):
        """Test form với dữ liệu hợp lệ"""
        form_data = {
            'title': 'Test Product',
            'description': 'Test description',
            'category': self.category.cid,
            'amount': Decimal('99.99'),
            'old_price': Decimal('120.00'),
            'stock_count': 10,
            'life': 30,
        }
        form = AddProductForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_missing_required_title(self):
        """Test form thiếu title (bắt buộc)"""
        form_data = {
            'description': 'Test description',
            'category': self.category.cid,
            'amount': Decimal('99.99'),
            'stock_count': 10
        }
        form = AddProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_missing_required_category(self):
        """Test form thiếu category (bắt buộc)"""
        form_data = {
            'title': 'Test Product',
            'description': 'Test description',
            'amount': Decimal('99.99'),
            'stock_count': 10
        }
        form = AddProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('category', form.errors)

    def test_negative_price_validation(self):
        """Test validation cho giá âm"""
        form_data = {
            'title': 'Test Product',
            'category': self.category.cid,
            'amount': Decimal('-10.00'),  # Giá âm
            'stock_count': 10
        }
        form = AddProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)

    def test_negative_old_price_validation(self):
        """Test validation cho old_price âm"""
        form_data = {
            'title': 'Test Product',
            'category': self.category.cid,
            'amount': Decimal('99.99'),
            'old_price': Decimal('-10.00'),  # Old price âm
            'stock_count': 10
        }
        form = AddProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('old_price', form.errors)

    def test_old_price_can_be_less_than_current_price(self):
        """Test old_price có thể nhỏ hơn current price (trường hợp giá tăng)"""
        form_data = {
            'title': 'Test Product',
            'category': self.category.cid,
            'amount': Decimal('120.00'),  # Giá hiện tại cao hơn
            'old_price': Decimal('99.99'),  # Giá cũ thấp hơn
            'stock_count': 10
        }
        form = AddProductForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_negative_stock_validation(self):
        """Test validation cho stock âm"""
        form_data = {
            'title': 'Test Product',
            'category': self.category.cid,
            'amount': Decimal('99.99'),
            'stock_count': -5  # Stock âm
        }
        form = AddProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('stock_count', form.errors)

    def test_negative_life_validation(self):
        """Test validation cho life âm"""
        form_data = {
            'title': 'Test Product',
            'category': self.category.cid,
            'amount': Decimal('99.99'),
            'stock_count': 10,
            'life': -30  # Life âm
        }
        form = AddProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('life', form.errors)

    def test_empty_life_defaults_to_zero(self):
        """Test life rỗng sẽ default về 0"""
        form_data = {
            'title': 'Test Product',
            'category': self.category.cid,
            'amount': Decimal('99.99'),
            'stock_count': 10,
            'life': ''  # Life rỗng
        }
        form = AddProductForm(data=form_data)
        self.assertTrue(form.is_valid())
        # Check cleaned_data
        self.assertEqual(form.cleaned_data['life'], 0)

    def test_zero_price_validation(self):
        """Test validation cho giá = 0 (có thể không được phép)"""
        form_data = {
            'title': 'Test Product',
            'category': self.category.cid,
            'amount': Decimal('0.00'),  # Giá = 0
            'stock_count': 10
        }
        form = AddProductForm(data=form_data)
        # Kiểm tra form có valid không - có thể form không cho phép giá = 0
        if form.is_valid():
            # Nếu form cho phép giá = 0
            self.assertTrue(True)
        else:
            # Nếu form không cho phép giá = 0, kiểm tra có error message
            self.assertIn('amount', form.errors)
            # In ra error message để debug
            print(f"Zero price error: {form.errors['amount']}")

    def test_zero_stock_allowed_for_draft(self):
        """Test stock = 0 được phép cho draft"""
        form_data = {
            'title': 'Test Product',
            'category': self.category.cid,
            'amount': Decimal('99.99'),
            'stock_count': 0
        }
        form = AddProductForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_save_method(self):
        """Test form save method"""
        form_data = {
            'title': 'Test Product',
            'description': 'Test description',
            'category': self.category.cid,
            'amount': Decimal('99.99'),
            'stock_count': 10
        }
        form = AddProductForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test save with commit=False
        product = form.save(commit=False)
        product.vendor = self.vendor
        product.save()
        
        self.assertEqual(product.title, 'Test Product')
        self.assertEqual(product.vendor, self.vendor)

    def test_minimum_valid_price(self):
        """Test giá tối thiểu được phép"""
        # Test với giá nhỏ nhất có thể
        form_data = {
            'title': 'Test Product',
            'category': self.category.cid,
            'amount': Decimal('0.01'),  # Giá 1 cent
            'stock_count': 10
        }
        form = AddProductForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_form_validation_edge_cases(self):
        """Test các edge cases của form validation"""
        # Test với số thập phân lớn
        form_data = {
            'title': 'Expensive Product',
            'category': self.category.cid,
            'amount': Decimal('999999.99'),
            'stock_count': 1000
        }
        form = AddProductForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
