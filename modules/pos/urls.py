from django.urls import path
from . import views

urlpatterns = [
    # Main PoS interface
    path('', views.PoSPageView.as_view(), name='pos_index'),

    # PoS API endpoints
    path('api/', views.PoSAPIView.as_view(), name='pos_api'),
]