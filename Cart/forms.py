from django import forms
from .models import Coupon


class ApplyCouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ('code',)
        widget = forms.TextInput(attrs={
            'class': 'form-control border-0 p-4',
            'placeholder': 'Coupon Code'
        })
