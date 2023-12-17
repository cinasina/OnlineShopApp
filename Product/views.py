from django.urls import reverse_lazy
from .forms import AddCommentForm
from django.views.generic import ListView, DetailView, FormView
from .models import Product, ProductComment
from django.contrib.auth.mixins import LoginRequiredMixin


class ProductsListView(ListView):
    model = Product
    template_name = 'product/products_list.html'
    context_object_name = 'products'
    queryset = Product.objects.filter(is_available=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        products = context['object_list']
        for product in products:
            if product.quantity <= 5:
                product.quantity_is_low = True
        return context


class ProductDetailsView(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'product/product_details.html'


class AddCommentFormView(LoginRequiredMixin, FormView):
    form_class = AddCommentForm
    template_name = 'product/product_details.html'

    def form_valid(self, form):
        product_id = self.kwargs.get('product_id')
        user = self.request.user
        product = Product.objects.get(product_id)
        comment = form.cleaned_data.get('comment')
        ProductComment.objects.create(user=user, product=product, comment=comment)
        return super().form_valid(form)

    def get_success_url(self):
        product_id = self.kwargs.get('product_id')
        return reverse_lazy('products:product_details', args=[product_id])
