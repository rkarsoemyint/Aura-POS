from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default="fa-box")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0) 
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    transaction_id = models.CharField(max_length=50, unique=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.transaction_id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2) 

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class ShopSetting(models.Model):
    shop_name = models.CharField(max_length=200, default="My POS Shop")
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='shop_logo/', blank=True, null=True)
    footer_receipt = models.TextField(default="Thank You! Please come again.", help_text="ဘောက်ချာအောက်ဆုံးမှာ ပေါ်မယ့်စာ")
    
    currency = models.CharField(max_length=20, default="MMK")
    tax_rate = models.FloatField(default=0.0)
    low_stock_limit = models.IntegerField(default=5)

    def __str__(self):
        return self.shop_name

    class Meta:
        verbose_name = "Shop Setting"
        verbose_name_plural = "Shop Settings"