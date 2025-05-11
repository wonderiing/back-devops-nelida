# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from airbnbs.api.views import AirbnbViewSet, ReservationViewSet, TransactionViewSet, UserReservationsAPIView

router = DefaultRouter()
router.register(r'airbnbs', AirbnbViewSet)
router.register(r'reservations', ReservationViewSet)
router.register(r'transactions', TransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
     path('rsv/my/', UserReservationsAPIView.as_view(), name='reservations-by-user'),
]
