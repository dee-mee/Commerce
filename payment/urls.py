from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('process/<int:order_id>/', views.payment_process, name='process'),
    path('completed/', views.payment_completed, name='completed'),
    path('cancelled/', views.payment_cancelled, name='cancelled'),
    path('callback/', views.payment_callback, name='callback'),
]
