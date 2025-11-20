from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from user_auth_app.models import CustomUser
from .serializers import LoginSerializer, UserRegistrationSerializer


class UserRegistrationView(APIView):
    """
    API endpoint for user registration.
    Allows any user to sign up.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.save()
        token = Token.objects.create(user=user)
        return Response({
            'token': token.key,
            'fullname': user.fullname,
            'email': user.email,
            'user_id': user.pk,
        }, status=status.HTTP_201_CREATED)


class CustomAuthToken(ObtainAuthToken):
    """
    API endpoint for user login.
    Returns an auth token and user details.
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'fullname': user.fullname,
            'email': user.email,
            'user_id': user.pk,
        })


class EmailCheckView(APIView):
    """
    API endpoint to check if an email is already registered.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response(
                {"error": "Email required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = CustomUser.objects.get(email=email)
            return Response({
                "id": user.id,
                "email": user.email,
                "fullname": user.fullname
            })
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "Email not found."},
                status=status.HTTP_404_NOT_FOUND
            )