from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken  # Import für Login
from .serializers import UserRegistrationSerializer
from .models import CustomUser

# -------------------------------------------------------------------
# 1. REGISTRIERUNG
# -------------------------------------------------------------------
class UserRegistrationView(APIView):
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


# -------------------------------------------------------------------
# 2. LOGIN
# -------------------------------------------------------------------
class CustomAuthToken(ObtainAuthToken):
    """
    Custom Login View.
    Erwartet 'email' (als username) und 'password'.
    Gibt Token, user_id, email und fullname zurück, gemäß API-Doku.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        
        # --- KORREKTUR START ---
        # 1. Daten kopieren, um sie veränderbar zu machen
        data = request.data.copy()
        
        # 2. 'email' (vom Frontend) dem 'username'-Feld zuweisen,
        #    das der Standard-Serializer erwartet.
        data['username'] = data.get('email') 
        
        # 3. Den Serializer mit den modifizierten Daten aufrufen
        serializer = self.serializer_class(data=data,
                                           context={'request': request})
        
        # Löst bei Fehler automatisch 400 BAD REQUEST aus
        serializer.is_valid(raise_exception=True) 
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        # Antwort gemäß API-Doku
        response_data = {
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'fullname': user.fullname
        }
        
        # 200 OK bei Erfolg
        return Response(response_data, status=status.HTTP_200_OK)


# -------------------------------------------------------------------
# 3. EMAIL-CHECK
# -------------------------------------------------------------------
class EmailCheckView(APIView):
    """
    API-Endpunkt zur Überprüfung, ob eine E-Mail bereits registriert ist.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        # E-Mail aus den Query-Parametern holen (z.B. /api/email-check/?email=...)
        email = request.query_params.get('email')
        
        if not email:
            # 400, wenn der 'email'-Parameter fehlt
            return Response(
                {"error": "Email parameter is required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Versuchen, den Benutzer zu finden
            user = CustomUser.objects.get(email=email)
            
            # Antwort gemäß API-Doku, wenn E-Mail existiert
            response_data = {
                "id": user.id,
                "email": user.email,
                "fullname": user.fullname
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
        except CustomUser.DoesNotExist:
            # Gemäß API-Doku: 404, wenn E-Mail nicht existiert
            return Response(
                {"error": "Email does not exist."}, 
                status=status.HTTP_404_NOT_FOUND
            )