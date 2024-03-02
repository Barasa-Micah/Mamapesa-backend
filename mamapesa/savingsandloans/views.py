from django.shortcuts import render
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from newmamapesa.models import Savings, CustomUser, SavingsItem, Item, Loan
from .serializers import SavingsAccountSerializer, SavingsItemSerializer, LoanRequestSerializer, LoanRepaymentSerializer, LoanSerializer
from rest_framework import status
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

class SavingsAccountView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user=request.user
        savings_account=get_object_or_404(Savings, user=user)
        
        serializer=SavingsAccountSerializer(savings_account)
        
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)

class SavingsItemsView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user=request.user
        all_savings_items=SavingsItem.objects.filter(savings=user.savings_account)
        
        serializer=SavingsItemSerializer(all_savings_items, many=True)
        
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)

class SavingsItemView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id):
        user=request.user
        condition1={'savings':user.savings_account}
        condition2={'id':id}
        all_savings_items=SavingsItem.objects.filter(**condition1, **condition2)
        
        serializer=SavingsItemSerializer(all_savings_items, many=True)
        
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
class DepositSavingsView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, saving_item_id):
        user=request.user
        specific_save_item=get_object_or_404(SavingsItem, id=saving_item_id)
        if specific_save_item.savings.user==user:
            
            # {
            #     "deposit_amount":2000
            # }
            deposit_amount=request.data.get("deposit_amount")
            phone_number=request.data.get("phone_number")
            amount=request.data.get("amount")
            
            if phone_number and amount:
                pass
                # handle payment here
            
            if deposit_amount:
                specific_save_item.amount_saved+=deposit_amount
                specific_save_item.save()
                response_dict=dict(message="Deposit successful")
                return JsonResponse(response_dict, status=status.HTTP_202_ACCEPTED)
                
            else:
                response_dict=dict(error="Provide the deposit amount")
                return JsonResponse(response_dict, status=status.HTTP_400_BAD_REQUEST)
        else:
            response_dict=dict(error="Sorry the requested resource could not be found")
            return JsonResponse(response_dict, status=status.HTTP_404_NOT_FOUND)
class CreateSavingsView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        received_item_name=request.data.get("item_name")
        received_item_price=request.data.get("item_price")
        saving_period=request.data.get("saving_period")
        phone_number=request.data.get("phone_number")
        initial_deposit=request.data.get("initial_deposit")
        if phone_number and initial_deposit:
            pass
            # handle payment here
        
        if received_item_name and received_item_price:
            new_item=Item(name=received_item_name, price=received_item_price)
            new_item.description=f"An item called {received_item_name}"
            new_item.save()
            
            user=request.user
            
            new_savings_item=SavingsItem(item=new_item, savings=user.savings_account)
            new_savings_item.target_amount=received_item_price
            if saving_period:
                new_savings_item.saving_period=saving_period
            new_savings_item.save()

            response_dict=dict(message="Item added successfully to savings items!!")
            
            # serializer=SavingsItemSerializer(new_savings_item) 
            # response_dict["saving_item"]=dict(name=new_savings_item.item.name, start_date=new_savings_item.start_date,)
            response_dict["saving_item"]=dict(name=new_savings_item.item.name, start_date=new_savings_item.start_date, end_date=new_savings_item.due_date, duration=new_savings_item.saving_period)
            return JsonResponse(response_dict, status=status.HTTP_201_CREATED)
        
        else:
            response_dict=dict(message="Please provide the necessary data i.e item_name, item_price")
            
            return JsonResponse(response_dict, status=status.HTTP_400_BAD_REQUEST)
            
            
class ChangeSavingsPeriodView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, saving_item_id):
        new_savings_period=request.data.get("new_savings_period")
        # if savings period provided
        if new_savings_period:
            user=request.user
            
            specific_savings_item=get_object_or_404(SavingsItem, id=saving_item_id)
            
            # verify if savings item belongs to the current user
            if specific_savings_item.savings.user==user:
                previous_end_date=specific_savings_item.due_date
                specific_savings_item.saving_period=new_savings_period
                specific_savings_item.save()
                
                response_dict=dict(message="Successfully updated savings period")
                response_dict["item"]=dict(name=specific_savings_item.item.name, price=specific_savings_item.item.price)
                response_dict["previous_end_date"]=previous_end_date
                response_dict["new_end_date"]=specific_savings_item.due_date
                
                return JsonResponse(response_dict, status=status.HTTP_200_OK)
            # handle response if savings item does not belong to user
            else:
                response_dict=dict(message="The resource could not be found")
                
                return JsonResponse(response_dict, status=status.HTTP_404_NOT_FOUND)
        #if savings period not provided   
        else:
            response_dict=dict(message="Please provide the necessary data i.e new_savings_period ")
            
            return JsonResponse(response_dict, status=status.HTTP_400_BAD_REQUEST)
            
# views.py


class LoanRequestView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = LoanRequestSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            loan = serializer.save()
            return Response({'success': 'Loan request successful', 'loan_id': loan.id}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoanRepaymentView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = LoanRepaymentSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            loan = request.user.loans.filter(is_active=True, disbursed=True).first()

            if not loan:
                return Response({'error': 'No active loan found for the user'}, status=status.HTTP_400_BAD_REQUEST)

            amount_paid = serializer.validated_data['amount_paid']  # Correct field name
            loan.make_repayment(amount_paid)

            return Response({'success': 'Loan repayment successful', 'repayment_amount': amount_paid}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class LoanDetailView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, loan_id, *args, **kwargs):
        loan = Loan.objects.filter(user=request.user, id=loan_id).first()

        if not loan:
            return Response({'error': 'Loan not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = LoanSerializer(loan)
        return Response(serializer.data)
