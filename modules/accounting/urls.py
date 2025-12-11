from django.urls import path
from . import views

urlpatterns = [
    # Main accounting management page
    path('', views.AccountingPageView.as_view(), name='accounting_index_page'),
    path('report-payable/', views.AccountingPayablePage.as_view(), name='accounting_payable_page'),
    path('report-receivable/', views.AccountingReceivablePage.as_view(), name='accounting_receivable_page'),
]