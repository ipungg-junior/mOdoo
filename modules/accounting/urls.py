from django.urls import path
from . import views

urlpatterns = [
    # Main accounting management page
    path('', views.AccountingPageView.as_view(), name='accounting_index_page'),
    path('report-payable/', views.AccountingPayablePage.as_view(), name='accounting_payable_page'),
    path('report-receivable/', views.AccountingReceivablePage.as_view(), name='accounting_receivable_page'),
    # API endpoints for data operations
    path('api/accounting/', views.APIView.as_view(context='accounting_api'), name='accounting_api'),
    path('api/category/', views.APIView.as_view(context='category_api'), name='category_api'),
]