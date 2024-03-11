from django.shortcuts import render
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from newmamapesa.models import Savings, CustomUser, SavingsItem, Item, LoanTransaction
# from .serializers import SavingsAccountSerializer, SavingsItemSerializer, LoanRequestSerializer, LoanRepaymentSerializer, LoanSerializer, TransactionSerializer
from .serializers import SavingsAccountSerializer, SavingsItemSerializer
from rest_framework import status
from django.http import JsonResponse
from rest_framework.response import Response
# from .serializers import LoanRequestSerializer, LoanRepaymentSerializer, LoanSerializer
# from newmamapesa.models import Loan, LoanRepayment
from rest_framework.permissions import IsAuthenticated
# Create your views here.
class SavingsAccountView(APIView):
    
    def get(self, request):
        user=CustomUser.objects.get(id=1)
        savings_account=get_object_or_404(Savings, user=user)
        
        serializer=SavingsAccountSerializer(savings_account)
        
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)

class SavingsItemsView(APIView):
    
    def get(self, request):
        user=CustomUser.objects.get(id=1)
        all_savings_items=SavingsItem.objects.filter(savings=user.savings_account)
        
        serializer=SavingsItemSerializer(all_savings_items, many=True)
        
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)

class SavingsItemView(APIView):
    
    def get(self, request, id):
        user=CustomUser.objects.get(id=1)
        condition1={'savings':user.savings_account}
        condition2={'id':id}
        all_savings_items=SavingsItem.objects.filter(**condition1, **condition2)
        
        serializer=SavingsItemSerializer(all_savings_items, many=True)
        
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
class DepositSavingsView(APIView):
    
    def post(self, request, saving_item_id):
        specific_save_item=get_object_or_404(SavingsItem, id=saving_item_id)
        
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
        
class CreateSavingsView(APIView):
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
            
            test_user=CustomUser.objects.get(id=1)
            
            new_savings_item=SavingsItem(item=new_item, savings=test_user.savings_account)
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
    
    def post(self, request, saving_item_id):
        new_savings_period=request.data.get("new_savings_period")
        
        if new_savings_period:
        
            specific_savings_item=get_object_or_404(SavingsItem, id=saving_item_id)
            
            previous_end_date=specific_savings_item.due_date
            specific_savings_item.saving_period=new_savings_period
            specific_savings_item.save()
            
            response_dict=dict(message="Successfully updated savings period")
            response_dict["item"]=dict(name=specific_savings_item.item.name, price=specific_savings_item.item.price)
            response_dict["previous_end_date"]=previous_end_date
            response_dict["new_end_date"]=specific_savings_item.due_date
            
            return JsonResponse(response_dict, status=status.HTTP_200_OK)
        else:
            response_dict=dict(message="Please provide the necessary data i.e new_savings_period ")
            
            return JsonResponse(response_dict, status=status.HTTP_400_BAD_REQUEST)
            
# views.py
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .serializers import LoanRequestSerializer, LoanRepaymentSerializer, LoanSerializer
# from newmamapesa.models import Loan, LoanRepayment
# from rest_framework.permissions import IsAuthenticated
# from rest_framework import generics


# class LoanRepaymentView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         serializer = LoanRepaymentSerializer(data=request.data, context={'request': request})

#         if serializer.is_valid():
#             loan = request.user.loans.filter(is_active=True, disbursed=True).first()

#             if not loan:
#                 return Response({'error': 'No active loan found for the user'}, status=status.HTTP_400_BAD_REQUEST)

#             amount_paid = serializer.validated_data['amount_paid']  # Correct field name
#             loan.make_repayment(amount_paid)

#             return Response({'success': 'Loan repayment successful', 'repayment_amount': amount_paid}, status=status.HTTP_201_CREATED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# class LoanDetailView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, loan_id, *args, **kwargs):
#         loan = Loan.objects.filter(user=request.user, id=loan_id).first()

#         if not loan:
#             return Response({'error': 'Loan not found'}, status=status.HTTP_404_NOT_FOUND)

#         serializer = LoanSerializer(loan)
#         return Response(serializer.data)


# class TransactionListView(generics.ListAPIView):
#     serializer_class = TransactionSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         loan_transactions = Transaction.objects.filter(user=user, loan__isnull=False)
#         savings_transactions = Transaction.objects.filter(user=user, savings__isnull=False)
                
#         queryset = loan_transactions | savings_transactions

#         print(f"User: {user.username}")
#         print(f"Number of transactions: {queryset.count()}")

#         return queryset

from newmamapesa.models import Loan, LoanRepayment, Savings, SavingsItem, Item, LoanTransaction
from .serializers import LoanRequestSerializer, LoanRepaymentSerializer, LoanTransactionSerializer, CustomUserSerializer
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics


class LoanRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = LoanRequestSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            user = request.user
            amount_requested = Decimal(serializer.validated_data['amount'])
            active_loan = Loan.objects.filter(user=user, is_active=True).first()

            # Check loan eligibility conditions
            eligibility_check = self.check_loan_eligibility(user, amount_requested, active_loan)

            if eligibility_check['is_eligible']:
                # Update loan_owed and loan_limit
                user.loan_owed += amount_requested
                user.loan_limit -= amount_requested
                user.save()

                # Create Loan instance
                loan = Loan(
                    user=user,
                    amount=amount_requested,
                    purpose=serializer.validated_data['purpose'],
                    loan_duration=90,
                    application_date=timezone.now().date(),
                    is_approved=True,
                    is_active=True,
                    disbursed=True,
                    grace_period=30,
                    late_payment_penalty_rate=5,
                )

                loan.save()

                return Response({"message": "Loan request successful.", 'amount': amount_requested}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": eligibility_check['error']}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def check_loan_eligibility(self, user, amount_requested, active_loan):
        # Business logic for checking loan eligibility
        condition_1 = user.loan_limit > 0
        condition_2 = user.loan_owed <= 8000
        condition_3 = amount_requested <= 8000 or (active_loan and user.loan_owed <= 8000)        
        if not condition_1:
            return {'is_eligible': False, 'error': "Loan limit exhausted."}
        elif not condition_2:
            return {'is_eligible': False, 'error': "Loan owed exceeds limit."}
        elif not condition_3:
            return {'is_eligible': False, 'error': "Additional loan exceeds limit."}        
        else:
            return {'is_eligible': True, 'error': None}

class LoanRepaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = LoanRepaymentSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            user = request.user
            loan = user.loans.filter(is_active=True, disbursed=True).first()

            if not loan:
                return Response({'error': 'No active loan found for the user. Kindly move to the savings page to start saving'}, status=status.HTTP_400_BAD_REQUEST)

            amount_paid = serializer.validated_data['amount_paid']
            remaining_loan_amount = loan.calculate_remaining_amount()

            if amount_paid > remaining_loan_amount:
                # Save the excess amount to the user's savings
                excess_amount = amount_paid - remaining_loan_amount

                # # Assuming you have a Savings model
                # savings = user.user_savings  # Access the related name
                # savings.amount_saved += excess_amount
                # savings.save()

                amount_paid = remaining_loan_amount

            # Update loan_owed and loan_limit
            user.loan_owed -= amount_paid
            user.loan_limit += amount_paid
            user.save()



            # Create LoanRepayment instance
            loan_repayment = LoanRepayment.objects.create(
                loan=loan,
                amount_paid=amount_paid
            )

            loan_repayment.save()

            return Response({"message": "Loan repayment successful.", 'repayment_amount': amount_paid}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  



class LoanTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        transactions = LoanTransaction.objects.filter(user=user)
        serializer = LoanTransactionSerializer(transactions, many=True)
        return Response(serializer.data)

class UserLoanInfoView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):        
        return self.request.user
