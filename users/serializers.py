from rest_framework import serializers, exceptions
from django.contrib.auth import authenticate 
from .models import CustomUser


class UserRegistrationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    repeated_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ('fullname', 'email', 'password', 'repeated_password')

    def create(self, validated_data):

        user = CustomUser.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        user.fullname = validated_data['fullname']
        user.save()
        return user

# -------------------------------------------------------------------
# Eigener LoginSerializer
# -------------------------------------------------------------------
class LoginSerializer(serializers.Serializer):
    """
    Dieser Serializer validiert 'email' und 'password' (anstelle von 'username').
    """
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            # Wir rufen authenticate() auf. Da wir USERNAME_FIELD = 'email'
            # in models.py gesetzt haben, weiß Django, dass es 
            # das 'email'-Feld für die Authentifizierung verwenden soll.
            user = authenticate(request=self.context.get('request'),
                                username=email, password=password)

            if not user:
                # Wenn authenticate fehlschlägt, geben wir den Fehler aus
                msg = 'Unable to log in with provided credentials.'
                raise exceptions.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "email" and "password".'
            raise exceptions.ValidationError(msg, code='authorization')

        data['user'] = user
        return data