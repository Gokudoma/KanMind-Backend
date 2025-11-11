from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .serializers import UserRegistrationSerializer
from .models import CustomUser


class UserRegistrationView(APIView):
    """
    API-Endpunkt für die Benutzerregistrierung.
    Erlaubt POST-Anfragen ohne Authentifizierung.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.create(user=user)
            
            response_data = {
                'token': token.key,
                'user_id': user.pk,
                'email': user.email,
                'fullname': user.fullname
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomAuthToken(ObtainAuthToken):
    """
    Custom Login View.
    Erwartet 'email' (als username) und 'password'.
    Gibt Token, user_id, email und fullname zurück, gemäß API-Doku.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        request.data['username'] = request.data.get('email')
        
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        
        serializer.is_valid(raise_exception=True) 
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        response_data = {
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'fullname': user.fullname
        }
        
        return Response(response_data, status=status.HTTP_200_OK)



class EmailCheckView(APIView):
    """
    API-Endpunkt zur Überprüfung, ob eine E-Mail bereits registriert ist.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        email = request.query_params.get('email')
        
        if not email:
            return Response(
                {"error": "Email parameter is required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = CustomUser.objects.get(email=email)
            
            response_data = {
                "id": user.id,
                "email": user.email,
                "fullname": user.fullname
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "Email does not exist."}, 
                status=status.HTTP_404_NOT_FOUND
            )