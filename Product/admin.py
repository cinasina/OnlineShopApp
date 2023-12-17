from django.contrib import admin
from .models import *


# Reminder: Add Price After Discount Auto
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(MainCategory)
admin.site.register(SubCategory)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductComment)
admin.site.register(ProductRate)
