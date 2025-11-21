from django.contrib.auth import authenticate
from rest_framework import serializers, exceptions

from user_auth_app.models import CustomUser


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    repeated_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = CustomUser
        fields = ['fullname', 'email', 'password', 'repeated_password']

    def create(self, validated_data):
        """
        Creates a new user instance.

        Steps:
        1. Use create_user helper to handle password hashing correctly.
        2. Set the username to the email (as they are identical in this system).
        3. Assign the fullname explicitly.
        4. Save and return the user object.
        """
        user = CustomUser.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        user.fullname = validated_data['fullname']
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login authentication.
    """
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        """
        Validates credentials and authenticates the user.

        Steps:
        1. Check if both email and password are provided.
        2. Use Django's authenticate() function to verify credentials.
        3. If authentication fails (user is None), raise a ValidationError.
        4. If successful, attach the user object to the validated data.
        """
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise exceptions.ValidationError(
                'Must include "email" and "password".'
            )

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            raise exceptions.ValidationError(
                'Unable to log in with provided credentials.'
            )

        data['user'] = user
        return data