# Constants and Choices for E-commerce Models

# Order Status Choices
STATUS_CHOICE = (
    ("processing", "Processing"),
    ("shipped", "Shipped"),
    ("delivered", "Delivered"),
)

# Product Status Choices
STATUS = (
    ("draft", "Draft"),
    ("disabled", "Disabled"),
    ("rejected", "Rejected"),
    ("in_review", "In Review"),
    ("published", "Published"),
)

# Rating Choices
RATING = (
    (1,  "★☆☆☆☆"),
    (2,  "★★☆☆☆"),
    (3,  "★★★☆☆"),
    (4,  "★★★★☆"),
    (5,  "★★★★★"),
)

# User Role Choices
ROLE_CHOICES = (
    ('customer', 'Customer'),
    ('vendor', 'Vendor'),
    ('admin', 'Admin'),
)

# Return Request Status Choices
RETURN_STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('completed', 'Completed'),
) 

PRODUCT_STATUS_CHOICES = (
    ('draft', 'Draft'),
    ('in_review', 'In Review'),
    ('published', 'Published'),
)

OBJECT_TYPE_CHOICES = (
    ('product', 'Product'),
    ('category', 'Category'),
    ('vendor', 'Vendor'),
    ('vendor_banner', 'Vendor_Banner'),
)

ORDER_STATUS_CHOICES = (
    ('processing', 'Processing'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
    ('refunded', 'Refunded'),
)
# constants.py
MAX_LENGTH_MOBILE = 15
MAX_LENGTH_ADDRESS = 255
MAX_LENGTH_TEXT = 255
MAX_LENGTH_TITLE = 200
MAX_LENGTH_CONTACT = 100
MAX_LENGTH_IMAGE_URL = 500
MAX_LENGTH_OBJECT_TYPE = 50
MAX_LENGTH_OBJECT_ID = 50
MAX_LENGTH_IMAGE_TYPE = 50
MAX_LENGTH_TYPE=100
MAX_LENGTH_CODE = 50
MAX_LENGTH_PRODUCT_TYPE = 100
MAX_LENGTH_STOCK_COUNT = 100
MAX_LENGTH_LIFE = 100
MAX_LENGTH_PRODUCT_STATUS = 20
MAX_LENGTH_ORDER_STATUS = 50
MAX_DIGITS_AMOUNT = 10
MAX_LENGTH_CID=100
MAX_LENGTH_PID = 20
MAX_LENGTH_VID=100
MAX_LENGTH_SKU=10
MAX_LENGTH_RETRUNRQ_STATUS = 50
MAX_LENGTH_ITEM=255
MAX_LENGTH_DAY_TIME =100
WARRANTY_PERIOD_TIME_MONTH = 60
DAY_RETURN = 3
AUTHENTIC_RATING =5.0
MIN=0
SHIP_ON_TIME =100
