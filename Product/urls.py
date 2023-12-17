from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductsListView.as_view(), name='products_list'),
    path('<int:pk>/details/', views.ProductDetailsView.as_view(), name='product_details'),
    path('<int:pk>/add_comment/', views.AddCommentFormView.as_view(), name='add_comment'),
]