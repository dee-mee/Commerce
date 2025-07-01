from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('sales/', views.sales_analytics, name='sales'),
    path('products/', views.product_management, name='products'),
    path('orders/', views.order_management, name='orders'),
    path('customers/', views.customer_management, name='customers'),
    path('flash-sales/', views.flash_sales_management, name='flash_sales'),
    path('flash-sales/<int:sale_id>/', views.flash_sale_detail_admin, name='flash_sale_detail'),
    path('flash-sales/update-stock/<int:item_id>/', views.update_flash_sale_stock, name='update_flash_sale_stock'),
]
