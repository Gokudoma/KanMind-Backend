from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
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