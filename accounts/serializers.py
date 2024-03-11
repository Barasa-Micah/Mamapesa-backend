from rest_framework import serializers
from newmamapesa.models import CustomUser
from django.contrib.auth import authenticate
from newmamapesa.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=CustomUser
        fields=['username','email']

class UserRegisterSerializer(serializers.ModelSerializer):
    idnumber = serializers.CharField(max_length=10, write_only=True, required=True)
    phonenumber = serializers.CharField(max_length=20, write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'idnumber', 'phonenumber']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_id_number(self, value):
        # Check if the idnumber already exists
        if CustomUser.objects.filter(idnumber=value).exists():
            raise serializers.ValidationError("ID number must be unique.")
        return value


    def save(self):
        password = self.validated_data['password']
        idnumber = self.validated_data['idnumber']
        phonenumber = self.validated_data['phonenumber']


        account = CustomUser(
            email=self.validated_data.get('email'),
            username=self.validated_data['username'],
            idnumber=idnumber,
            phonenumber=phonenumber
        )
        account.set_password(password)
        account.save()

        return account
   