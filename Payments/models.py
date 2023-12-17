from django.db import models
from django.contrib.auth import get_user_model
from Product.models import Product
from Accounts.models import MyUser

User = get_user_model()


class Order(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('on_hold', 'On Hold'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    total_price = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"{self.user.username} ({self.user.email})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} of {self.product.name} ({self.order.user.username})"
