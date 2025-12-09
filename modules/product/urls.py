from django.urls import path
from . import views

urlpatterns = [
    # Main product management page
    path('', views.ProductPageView.as_view(), name='product_list'),
    # Create product page
    path('create-product/', views.ProductCreatePageView.as_view(), name='product_create_page'),
    path('transaction/', views.ProductTransactionPageView.as_view(), name='product_transaction_page'),
    # API endpoints for data operations
    path('api/product/', views.APIView.as_view(context='product_api'), name='product_api'),
    path('api/category/', views.APIView.as_view(context='category_api'), name='category_api'),
    path('api/transaction/', views.APIView.as_view(context='product_transaction_api'), name='product_transaction_api'),
]