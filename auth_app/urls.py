from django.urls import path
from .views import RegisterView

app_name = 'auth_app'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
]
