from django.urls import path
from . import views

urlpatterns = [
    # Main product management page
    path('', views.ProductPageView.as_view(), name='product_list'),
    # API endpoints for data operations
    path('api/product/', views.APIView.as_view(context='product_api'), name='product_api'),
    path('api/category/', views.APIView.as_view(context='category_api'), name='category_api'),
]