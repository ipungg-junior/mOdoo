from django.urls import path
from . import views

urlpatterns = [
    # Main product management page
    path('', views.ProductPageView.as_view(), name='product_list'),
    # API endpoints for data operations
    path('api/product/', views.APIView.as_view(), name='product_api', context='product_api'),
    path('api/category/', views.APIView.as_view(), name='category_api', context='category_api'),
]