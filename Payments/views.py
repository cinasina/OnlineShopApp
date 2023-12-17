from django.views.generic import TemplateView, View
from Product.models import Product
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.conf import settings
import requests
import json
from django.shortcuts import HttpResponse, redirect


class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'payments/checkout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.session.get('product_list', {})
        cart_item_info = []
        total_items_price = 0
        for product_id, cart_item in cart.items():
            pk = int(product_id)
            product = get_object_or_404(Product, pk=pk)
            subtotal = product.price_after_discount * cart_item['quantity']
            cart_item_info.append({'product': product, "subtotal": subtotal, 'price': product.price,
                                   'quantity': cart_item['quantity']})
            total_items_price += subtotal
        context['cart_item_info'] = cart_item_info
        context['total_items_price'] = total_items_price

        # Sometimes For AnyReason, Something Can Be Wrong In Database And Give Us Alert,
        # We Use Transaction To Reset Everything.
        # We Use It, In A Limited Space Code When Something Is Going To Run.

        with transaction.atomic():
            order = Order.objects.create(user=self.request.user, total_price=total_items_price,
                                         status='pending')
            # We Use bulk_create to Save All Items Once. It Should Be A List.
            item_list = []
            for item in cart_item_info:
                item_list.append(OrderItem(order=order, product=item['product'], quantity=item['quantity'],
                                           price=item['price'], subtotal=item['subtotal']))
            OrderItem.objects.bulk_create(item_list)
            context['order_id'] = order.id
            return context


# ? sandbox merchant
if settings.SANDBOX:
    sandbox = 'sandbox'
else:
    sandbox = 'www'

ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
ZP_API_VERIFY = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"

description = "A Test For Paying"  # Required
phone = 9183682516  # Optional
# Important: need to edit for real server.
CallbackURL = 'http://127.0.0.1:8080/payment/verify/'


class PayingView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id, user=request.user,
                                  status='pending')
        request.session['order_id_pay'] = {'order_id': order.id}
        data = {
            "MerchantID": settings.MERCHANT,
            "Amount": order.total_price,
            "Description": description,
            "Phone": phone,
            "CallbackURL": CallbackURL,
        }
        # ZarinPal Needs Data As A Json. So We Change It To Json Format.
        data_as_json = json.dumps(data)
        print(f"Callback URL: {CallbackURL}")
        print(f"Data: {data_as_json}")
        # set content length by data
        headers = {'content-type': 'application/json', 'content-length': str(len(data_as_json))}
        try:
            response = requests.post(ZP_API_REQUEST, data=data_as_json, headers=headers)
            print(response)
            if response.status_code == 200:
                response = response.json()
                if response['Status'] == 100:
                    return redirect(ZP_API_STARTPAY + str(response['Authority']))
                else:
                    # Return an error message or a custom error page
                    print(response.json()['errors'])
                    return HttpResponse("Payment request failed")
            else:
                # Return an error message or a custom error page
                return HttpResponse("Payment request failed")

        except requests.exceptions.Timeout:
            # Return an error message or a custom error page
            return HttpResponse("Payment request timed out")
        except requests.exceptions.ConnectionError:
            # Return an error message or a custom error page
            return HttpResponse("Connection error")


class PaymentVerificationView(LoginRequiredMixin, View):
    def get(self, request):
        print("Payment verification view called")
        authority = request.GET.get('Authority')
        status = request.GET.get('Status')
        order_id = request.session['order_id_pay']['order_id']

        # Retrieve the Order instance from the database
        order = Order.objects.get(id=order_id)

        # Call the ZarinPal API to verify the payment
        data = {
            "MerchantID": settings.MERCHANT,
            "Authority": authority,
            "Amount": order.total_price,
        }
        headers = {'content-type': 'application/json'}
        response = requests.post(ZP_API_VERIFY, data=json.dumps(data), headers=headers)

        # Handle the payment verification response
        if response.status_code == 200:
            response_data = response.json()
            if response_data['Status'] == 100:
                # Payment was successful, update the order status to 'paid'
                order.status = 'paid'
                order.save()
                return HttpResponse('Payment was successful')
            else:
                # Payment failed, return an error message
                return HttpResponse('Payment failed')
        else:
            # Payment verification request failed, return an error message
            return HttpResponse('Payment verification request failed')