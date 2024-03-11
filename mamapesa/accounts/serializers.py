from rest_framework import serializers
from newmamapesa.models import CustomUser
from django.contrib.auth import authenticate
from newmamapesa.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=CustomUser
        fields=['username','email','phonenumber']

class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    idnumber = serializers.CharField(max_length=10, write_only=True, required=True)
    phonenumber = serializers.CharField(max_length=20, write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2', 'idnumber', 'phonenumber']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_id_number(self, value):
        # Check if the idnumber already exists
        if CustomUser.objects.filter(idnumber=value).exists():
            raise serializers.ValidationError("ID number must be unique.")
        return value

    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')

        if password != password2:
            raise serializers.ValidationError({'Error': 'Password mismatch'})

        return data

    def save(self):
        password = self.validated_data['password']
        idnumber = self.validated_data['idnumber']
        phonenumber = self.validated_data['phonenumber']

        # You may want to include additional validation for idnumber and phonenumber

        account = CustomUser(
            email=self.validated_data['email'],
            username=self.validated_data['username'],
            idnumber=idnumber,
            phonenumber=phonenumber
        )
        account.set_password(password)
        account.save()

        return account
    
# class UserLoginSerializer(serializers.Serializer):
#     username_or_email = serializers.CharField(max_length=255, required=True)
#     password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False, required=True)

#     def validate(self, data):
#         username_or_email = data.get('username_or_email')
#         password = data.get('password')

#         if username_or_email and password:
#             user = authenticate(username=username_or_email, password=password)

#             if user:
#                 if not user.is_active:
#                     raise serializers.ValidationError("CustomUser account is disabled.")
#             else:
#                 raise serializers.ValidationError("Unable to log in with provided credentials.")
#         else:
#             raise serializers.ValidationError("Must include 'username_or_email' and 'password'.")

#         data['user'] = user
#         return data

