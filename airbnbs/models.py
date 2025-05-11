from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Airbnb(models.Model):
    AVAILABLE = 'available'
    UNAVAILABLE = 'unavailable'
    STATUS_CHOICES = [
        (AVAILABLE, 'Available'),
        (UNAVAILABLE, 'Unavailable'),
    ]
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='airbnb_images/', null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=AVAILABLE,
    )
    
    def __str__(self):
        return self.title

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    airbnb = models.ForeignKey(Airbnb, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    def calculate_price(self):
        if self.start_date and self.end_date and self.airbnb:
            days = (self.end_date - self.start_date).days
            if days > 0:
                return (Decimal(str(days)) * self.airbnb.price_per_night).quantize(Decimal('0.01'))
        return Decimal('0.00')
    
    def __str__(self):
        return f'Reservation for {self.user.username} at {self.airbnb.title}'

class Transaction(models.Model):
    DEPOSIT = 'deposit'
    WITHDRAWAL = 'withdrawal'
    TRANSACTION_TYPES = [
        (DEPOSIT, 'Deposit'),
        (WITHDRAWAL, 'Withdrawal'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Transaction for {self.user.username}: {self.amount} {self.transaction_type}'