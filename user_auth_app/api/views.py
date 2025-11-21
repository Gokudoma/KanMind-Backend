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
        """
        Handles the registration process for a new user.

        Steps:
        1. Pass the incoming request data to the UserRegistrationSerializer.
        2. Validate the data (checks email format, password match, etc.).
        3. If invalid: Return 400 Bad Request with error details.
        4. If valid: Save the new user instance.
        5. Generate an authentication token for the new user.
        6. Return the token and user details in the response (201 Created).
        """
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
        """
        Handles user login and token generation.

        Steps:
        1. Initialize LoginSerializer with request data and context.
        2. Validate credentials (email & password) using Django's authenticate.
        3. If valid: Retrieve the authenticated user object.
        4. Get or create an auth token for this user.
        5. Return the token along with user ID, email, and fullname.
        """
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
        """
        Checks for the existence of a user with a specific email.

        Steps:
        1. Extract the 'email' parameter from the query string.
        2. If email is missing: Return 400 Bad Request.
        3. Attempt to find a user with this email in the database.
        4. If found: Return user details (200 OK).
        5. If not found: Return 404 Not Found error.
        """
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