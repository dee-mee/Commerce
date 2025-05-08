from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('sales/', views.sales_analytics, name='sales'),
    path('products/', views.product_management, name='products'),
    path('orders/', views.order_management, name='orders'),
    path('customers/', views.customer_management, name='customers'),
]
