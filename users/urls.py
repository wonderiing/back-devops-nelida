# urls.py
from django.urls import path
from .views import register, LoginView, update_balance, get_balance, CheckSuperUserByCredentialsAPIView

urlpatterns = [
    path('register/', register, name='register'),
     path('login/', LoginView.as_view(), name='login'),
     path('balance/', update_balance, name='balance'),
     path('my/', get_balance, name='get_balance'),
     path('super/', CheckSuperUserByCredentialsAPIView.as_view(), name='super'),
]
