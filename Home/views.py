from django.shortcuts import render
from django.views import View
from Product.models import Product


class HomeView(View):
    def get(self, request):
        products = Product.objects.filter(is_available=True)
        context = {'products': products}
        return render(request, 'home/home.html', context=context)
