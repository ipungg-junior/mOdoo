from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.module_list, name='module_list'),
    path('install/<str:module_name>/', views.install_module, name='install_module'),
    path('uninstall/<str:module_name>/', views.uninstall_module, name='uninstall_module'),
    path('upgrade/<str:module_name>/', views.upgrade_module, name='upgrade_module'),
]