# views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import Airbnb, Reservation, Transaction
from .serializers import AirbnbSerializer, ReservationSerializer, TransactionSerializer, ReservationWithAirbnbSerializer
from datetime import datetime
from decimal import Decimal, InvalidOperation
from rest_framework import status
import logging
from django.contrib.auth.models import User
from rest_framework.views import APIView




class UserReservationsAPIView(APIView):
  permission_classes = [IsAuthenticated]

  def get(self, request):
        user = request.user  # obtenido del token automáticamente
        reservations = Reservation.objects.filter(user=user)
        serializer = ReservationWithAirbnbSerializer(reservations, many=True)
        return Response(serializer.data)


class AirbnbViewSet(viewsets.ModelViewSet):
    queryset = Airbnb.objects.all()
    serializer_class = AirbnbSerializer

logger = logging.getLogger(__name__)

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        try:
            # 1. Obtener datos de entrada
            airbnb_id = request.data.get('airbnb')
            start_date_str = request.data.get('start_date')
            end_date_str = request.data.get('end_date')
            
            if not all([airbnb_id, start_date_str, end_date_str]):
                return Response({'detail': 'Missing required fields'}, status=400)
            
            # 2. Convertir fechas
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                
                if end_date <= start_date:
                    return Response({'detail': 'End date must be after start date'}, status=400)
                
            except ValueError:
                return Response({'detail': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
            
            # 3. Obtener el Airbnb
            try:
                airbnb = Airbnb.objects.get(id=airbnb_id)
            except Airbnb.DoesNotExist:
                return Response({'detail': 'Airbnb not found'}, status=404)
            
            # 4. Verificar si el Airbnb está disponible
            if airbnb.status == Airbnb.UNAVAILABLE:
                return Response({'detail': 'This Airbnb is not available'}, status=400)
            
            # 5. Calcular precio total
            days = (end_date - start_date).days
            total_price = Decimal(str(days)) * airbnb.price_per_night
            total_price = total_price.quantize(Decimal('0.01'))
            
            # 6. Verificar si el usuario tiene suficiente balance
            user_profile = request.user.profile
            if total_price > user_profile.balance:
                return Response({'detail': 'Insufficient funds'}, status=400)
            
            # 7. Crear reserva
            reservation = Reservation.objects.create(
                user=request.user,
                airbnb=airbnb,
                start_date=start_date,
                end_date=end_date,
                total_price=total_price
            )
            
            # 8. Actualizar balance del usuario
            user_profile.balance -= total_price
            user_profile.save()
            
            Transaction.objects.create(
                user=request.user,
                amount=total_price,
                transaction_type=Transaction.WITHDRAWAL
            )
            
            return Response(ReservationSerializer(reservation).data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating reservation: {e}")
            return Response({'detail': 'An error occurred while processing your request'}, status=500)
    

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]  # Requiere que el usuario esté autenticado

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)
