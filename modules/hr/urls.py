from django.urls import path
from . import views

urlpatterns = [
    # Main HR page
    path('', views.EmployeeIndex.as_view(), name='employee_index_page'),
    path('create/', views.EmployeeCreatePage.as_view(), name='employee_create_page'),
    # API endpoints for data operations
    path('api/employee/', views.APIView.as_view(context='employee_api'), name='employee_api')
]