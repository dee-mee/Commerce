from django.urls import path
from . import views, api

app_name = 'store'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('brand/<slug:slug>/', views.brand_detail, name='brand_detail'),
    path('search/', views.search_products, name='search_products'),
    path('add-review/<int:product_id>/', views.add_review, name='add_review'),
    path('flash-sales/', views.flash_sale_list, name='flash_sale_list'),
    path('flash-sales/<int:sale_id>/', views.flash_sale_detail, name='flash_sale_detail'),
    path('api/flash-sale-stock/', api.get_flash_sale_stock, name='flash_sale_stock_api'),
    path('api/flash-sale-notification/', api.toggle_flash_sale_notification, name='flash_sale_notification_api'),
]
