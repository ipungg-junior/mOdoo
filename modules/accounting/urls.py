from django.urls import path
from . import views

urlpatterns = [
    # Main accounting management page
    path('', views.AccountingPageView.as_view(), name='accounting_index_page'),
    path('report-payable/', views.AccountingPayablePage.as_view(), name='accounting_payable_page'),
    path('report-receivable/', views.AccountingReceivablePage.as_view(), name='accounting_receivable_page'),
    # Create receivable page
    path('create-ar/', views.AccountingCreateARPageView.as_view(), name='accounting_create_ar_page'),
    # API endpoints
    path('api/master-data/', views.APIView.as_view(context='master_data_api'), name='master_data_api'),
    path('api/receivable/', views.APIView.as_view(context='receivable_api'), name='receivable_api')
]