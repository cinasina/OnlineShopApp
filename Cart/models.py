from django.db import models
from django.core.validators import MaxValueValidator


class Coupon(models.Model):
    code = models.CharField(max_length=50)
    discount = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)], default=0)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code
