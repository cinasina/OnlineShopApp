from django import forms
from .models import ProductComment


class AddCommentForm(forms.ModelForm):
    comment = forms.CharField(widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}))

    class Meta:
        model = ProductComment
        fields = ['comment']
