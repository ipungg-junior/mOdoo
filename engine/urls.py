from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('modules/', views.ModuleListView.as_view(), name='module_list'),
    path('install/<str:module_name>/', views.InstallModuleView.as_view(), name='install_module'),
    path('uninstall/<str:module_name>/', views.UninstallModuleView.as_view(), name='uninstall_module'),
    path('upgrade/<str:module_name>/', views.UpgradeModuleView.as_view(), name='upgrade_module'),
    path('api/engine/', views.APIView.as_view(context='engine_api'), name='engine_api'),
]