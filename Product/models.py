from django.db import models
from django.core.validators import MaxValueValidator
from taggit.managers import TaggableManager
from django.db.models.aggregates import Avg
from django.contrib.auth import get_user_model

MyUser = get_user_model()


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MainCategory(BaseModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class SubCategory(BaseModel):
    name = models.CharField(max_length=100)
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name='subcategories')

    def __str__(self):
        return self.name


class Product(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='products')
    price = models.PositiveSmallIntegerField()
    discount = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)], default=0)
    price_after_discount = models.PositiveSmallIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    quantity = models.PositiveIntegerField()
    quantity_is_low = models.BooleanField(default=False)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    rate_average = models.DecimalField(max_digits=2, decimal_places=1, default=0)  # Rank field initialized to 0
    tags = TaggableManager()

    def __str__(self):
        return self.name

    def get_discounted_price(self):
        result = self.price - (self.price * self.discount / 100)
        self.price_after_discount = result
        return int(result)

    def get_rate_average(self):
        result = self.rate_average
        return result

    def get_approved_comments(self):
        return self.comments.filter(is_approved=True).prefetch_related('user').order_by('-created_date')

    def save(self, *args, **kwargs):
        self.price_after_discount = self.get_discounted_price()
        super().save(*args, **kwargs)  # Saving Price After Discount


class ProductRate(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='rates')
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    rate = models.PositiveSmallIntegerField(choices=[(x, x) for x in range(1, 11)])

    class Meta:
        unique_together = ('product', 'user',)  # Each user can rate a product only once.

    def __str__(self):
        return f'{self.user} Rated {self.product} a {self.rate}.'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.rate_average = self.product.rates.aggregate(Avg('rate'))['rate__avg']
        self.product.save()


class ProductComment(BaseModel):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    reply = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True, related_name='replies')
    is_reply = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} Comment {self.comment} For {self.product}.'
