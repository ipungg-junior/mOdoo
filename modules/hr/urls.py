from django.urls import path
from . import views

urlpatterns = [
    # Main HR page
    path('', views.EmployeeListView.as_view(), name='list_view'),
    # API endpoints for data operations
    path('api/employee/', views.APIView.as_view(context='employee_api'), name='employee_api')
]