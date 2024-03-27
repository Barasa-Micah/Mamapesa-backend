from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=20, write_only=True, required=True)
    first_name = serializers.CharField(max_length=50, required=True)
    last_name = serializers.CharField(max_length=50, required=True)
    email = serializers.EmailField(max_length=50, required=True)

    def create(self, validated_data):
        user=CustomUser.objects.create_user(**validated_data)
        return user
    class Meta: 
        model = CustomUser
        fields = ['phone_number','email', 'password', "first_name", "last_name"]
        extra_kwargs = {
            'password': {'write_only': True}
        }
        
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['phone_number','username', 'email', 'first_name', 'last_name']
        
