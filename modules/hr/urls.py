from django.urls import path
from . import views

urlpatterns = [
    path('', views.EmployeeListView.as_view(), name='list_view')
]