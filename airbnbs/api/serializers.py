# serializers.py
from rest_framework import serializers
from ..models import Airbnb, Reservation, Transaction

class AirbnbSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airbnb
        fields = ['id', 'title', 'description', 'price_per_night', 'location', 'image']

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'user', 'airbnb', 'start_date', 'end_date', 'total_price']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'amount', 'transaction_type', 'date']

class ReservationWithAirbnbSerializer(serializers.ModelSerializer):
    airbnb = AirbnbSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = ['id', 'start_date', 'end_date', 'total_price', 'created_at', 'airbnb']
