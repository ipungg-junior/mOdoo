from django.urls import path
from . import views

urlpatterns = [
    path('', views.Landing.as_view(), name='landing')
]