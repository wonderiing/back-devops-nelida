from django.contrib import admin
from .models import Reservation, Airbnb, Transaction
# Register your models here.

admin.site.register(Reservation)
admin.site.register(Airbnb)
admin.site.register(Transaction)