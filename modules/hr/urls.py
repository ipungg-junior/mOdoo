from django.urls import path
from . import views

urlpatterns = [
    # Main HR page
    path('', views.EmployeeIndex.as_view(), name='hr_index_page'),
    path('list-employee/', views.EmployeeListPage.as_view(), name='employee_list_page'),
    path('create-employee/', views.EmployeeCreatePage.as_view(), name='employee_create_page'),
    path('configuration/position/', views.EmployeePositionPage.as_view(), name='employee_position_page'),
    # API endpoints for data operations
    path('api/employee/', views.APIView.as_view(context='employee_api'), name='employee_api')
]