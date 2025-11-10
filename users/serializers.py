from rest_framework import serializers
from .models import CustomUser

class UserRegistrationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    repeated_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser

        fields = ('fullname', 'email', 'password', 'repeated_password')

    def validate(self, attrs):
        
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):

        validated_data.pop('repeated_password')

        user = CustomUser.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            fullname=validated_data['fullname'],
            password=validated_data['password']
        )
        return user