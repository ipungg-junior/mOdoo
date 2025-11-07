from django.urls import path
from . import views

urlpatterns = [
    path('', views.EmployeeListView.as_view(), name='list_view'),
    path('sync/', views.SyncEmployeesView.as_view(), name='sync_employees')
]