from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from django.http import JsonResponse
from .serializers import UserSerializer, UserRegisterSerializer
from django.shortcuts import get_object_or_404
from newmamapesa.models import CustomUser
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view


# Create your views here.

@method_decorator(csrf_exempt, name='dispatch')
class LoginWithToken(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username=request.data.get('username')
        password=request.data.get('password')
        
        user=authenticate(request, username=username, password=password)

        # if user exists in db = correct credentials
        if user is not None:

            login(request, user)
            # getting user token 
            token, created_token=Token.objects.get_or_create(user=user)
            user_instance=get_object_or_404(CustomUser, username=username)
            serializer=UserSerializer(user_instance)
            
            response_dict={"user":serializer.data}
            
            # using an existing token
            if token:
                response_dict["token"]=token.key
            # using a created token if not existed before  
            elif created_token:
                response_dict["token"]=created_token.key
                
            return JsonResponse(response_dict, status=status.HTTP_200_OK)
            
        # If user returns NONE = wrong credentials
        else:
            response_dict={"error": "Invalid credentials"}
            return JsonResponse(response_dict, status=status.HTTP_401_UNAUTHORIZED)
        
class TestView(APIView):
    # authentication_classes = [SessionAuthentication, TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    
    def get(self,request):
        response_dict=dict(message="The tokens work",message1="The tokens work",message2="The tokens work",message3="The tokens work")
        if request.user:
            response_dict["user"]=request.user.username
        return JsonResponse(response_dict, status=status.HTTP_200_OK)
    
# class LogoutView(APIView):
#     def
#     request.user.auth_token.delete()

# Create your views here.
@api_view(['POST'])
def user_registration(request):
    if request.method == 'POST':
        serializer = UserRegisterSerializer(data=request.data)

        if serializer.is_valid():
            account = serializer.save()

            data = {
                'response': 'Account has been successfully created',
                'username': account.username,
                'email': account.email,
            }

            return Response(data, status=status.HTTP_201_CREATED)
        else:
            data = {
                'error': 'Invalid data',
                'errors': serializer.errors
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)
# class UserLoginView(APIView):
#     def post(self, request):
#         serializer = UserLoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#         token, created = Token.objects.get_or_create(user=user)

#         if not created:
#             # Token already exists, no need to create a new one
#             # You can handle this situation if needed
#             pass

#         return Response({
#             'token': token.key,
#             'username': user.username,
#             'email': user.email
#         }, status=status.HTTP_200_OK)    

