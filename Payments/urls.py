from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('pay/<int:order_id>/', views.PayingView.as_view(), name='paying'),
    path('verify/', views.PaymentVerificationView.as_view(), name='verify'),
]