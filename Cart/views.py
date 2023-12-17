from Product.models import Product
from django.views.generic import View, FormView
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views.generic import TemplateView
from .forms import ApplyCouponForm
from django.utils import timezone
from django.contrib import messages
from .models import Coupon
from django.urls import reverse_lazy


def calculate_coupon_discount(total_items_price, coupon):
    return int((coupon.discount / 100) * total_items_price)


class CartView(FormView, TemplateView):
    template_name = 'cart/cart.html'
    form_class = ApplyCouponForm
    success_url = reverse_lazy('cart:cart')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.session.get('product_list', {})
        cart_items_info = []

        total_items_price = 0
        for product_id, cart_item in cart.items():
            product = get_object_or_404(Product, pk=int(product_id))
            subtotal = product.price_after_discount * cart_item['quantity']
            total_items_price += subtotal

            cart_items_info.append({
                'product': product,
                'quantity': cart_item['quantity'],
                'price': product.price,
                'subtotal': subtotal
            })

        context['form'] = self.get_form()
        context['cart_items_info'] = cart_items_info
        context['total_items_price'] = self.request.session.get(
            'total_items_price', total_items_price)
        return context

    def form_valid(self, form):
        coupon_code = form.cleaned_data['code']
        now = timezone.now()

        try:
            coupon = Coupon.objects.get(
                code=coupon_code,
                is_active=True,
                valid_from__lte=now,
                valid_to__gte=now
            )

            calculated_coupon_discount = calculate_coupon_discount(
                self.request.session['total_items_price'], coupon)
            self.request.session['total_items_price'] -= calculated_coupon_discount
            self.request.session.modified = True

            messages.success(
                self.request, f"Coupon '{coupon_code}' applied successfully!")

        except Coupon.DoesNotExist:
            messages.error(self.request, "Invalid coupon code. Please try again.")

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid form data. Please try again.")
        return super().form_invalid(form)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class AddToCartView(View):
    def get(self, request, *args, **kwargs):
        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, pk=product_id)
        cart = request.session.get('product_list', {})  # {}
        cart_item = cart.get(str(product.id), {'quantity': 0})  # cart_item = {'2': {'quantity': 0}} |
        # Return 0 If product_id Is Not Exist.
        cart_item['quantity'] += 1  # cart_item = {'2': {'quantity': 1}}
        cart[str(product.id)] = cart_item  # Update Cart To Be Like cart_item Which Is: cart = {'2': {'quantity': 1}}
        request.session['product_list'] = cart  # product_list = {'2': {'quantity': 1}}
        return redirect('cart:cart')


class RemoveToCartView(View):
    def get(self, request, *args, **kwargs):
        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, pk=product_id)
        cart = request.session.get('product_list', {})
        cart_item = cart.get(str(product.id), {'quantity': 0})
        if cart_item['quantity'] > 0:
            cart_item['quantity'] -= 1
        elif str(product.id) in cart:
            del cart[str(product.id)]
        request.session['product_list'] = cart
        return redirect('cart:cart')
