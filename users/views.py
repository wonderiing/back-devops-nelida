# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import UserSerializer
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .models import Profile
from django.contrib.auth.models import User


@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            # Crear el usuario
            user = serializer.save()

            # Crear el perfil para el usuario
            Profile.objects.create(user=user)

            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# views.py

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'detail': 'Invalid credentials'}, status=400)
    

@api_view(['POST'])
def update_balance(request):
    if not request.user.is_authenticated:
        return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
    
    user = request.user

    amount_to_add = request.data.get('balance')

    if amount_to_add is None:
        return Response({"detail": "No balance provided."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Convert to Decimal instead of float to match the profile.balance type
        from decimal import Decimal
        amount_to_add = Decimal(str(amount_to_add))
    except (ValueError, TypeError):
        return Response({"detail": "Invalid balance value."}, status=status.HTTP_400_BAD_REQUEST)
    
    profile = user.profile
    # Add to the existing balance instead of replacing it
    profile.balance += amount_to_add
    profile.save()

    return Response({
        "detail": f"Added {amount_to_add} to balance. New balance is {profile.balance}"
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_balance(request):
    if not request.user.is_authenticated:
        return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
    
    user = request.user  

    try:
        profile = user.profile  # Accede al perfil del usuario (suponiendo que tengas un perfil asociado)
        balance = profile.balance
    except AttributeError:
        return Response({"detail": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({"balance": balance}, status=status.HTTP_200_OK)

class CheckSuperUserByCredentialsAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"detail": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Autenticar al usuario con el nombre de usuario y la contraseña proporcionados
        user = authenticate(username=username, password=password)

        if user is not None:
            # Si la autenticación es exitosa, verificar si es un superusuario
            is_superuser = user.is_superuser

            # Generar un token para el usuario autenticado
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                "is_superuser": is_superuser,
                "token": token.key  # Devolver el token generado
            }, status=status.HTTP_200_OK)
        else:
            # Si la autenticación falla
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)