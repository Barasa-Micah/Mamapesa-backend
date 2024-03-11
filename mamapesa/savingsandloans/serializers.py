from rest_framework import serializers
from newmamapesa.models import Loan, LoanRepayment,Savings, SavingsItem, Item, LoanTransaction, CustomUser
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

class SavingsAccountSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Savings
        fields=["id","amount_saved","start_date"]

class ItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Item
        fields=["id","name","description"]

class SavingsItemSerializer(serializers.ModelSerializer):
    item=ItemSerializer()
    # start_date = serializers.DateField(format='%Y-%m-%d')
    # due_date = serializers.DateField(format='%Y-%m-%d')
    class Meta:
        model=SavingsItem
        # fields=["id","item","amount_saved","target_amount","start_date","remaining_amount","daily_payment","remaining_days", "due_date","achieved","in_progress"]
        fields=["id","item","amount_saved","target_amount","start_date","remaining_amount","installment","days_payment","remaining_days", "due_date","saving_period","is_achieved","in_progress"]
# serializers.py

# class LoanRequestSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Loan
#         fields = ['amount', 'purpose']

#     def create(self, validated_data):
#         user = self.context['request'].user  
#         amount_requested = Decimal(validated_data['amount'])     
        
#         active_loan = Loan.objects.filter(user=user, is_active=True).first()

#         condition_1 = user.loan_limit > 0
#         condition_2 = user.loan_owed <= 8000
#         condition_3 = amount_requested <= 8000 or (active_loan and user.loan_owed <= 8000)#Amount requested should not be greater than 8000 if applying for the first time
#         # loan_total = 0
#         # loan_limit = 8000

#         if condition_1 and condition_2 and condition_3:
#             interest_rate = user.interest_rate
#             total_disbursed = amount_requested * (1 - interest_rate / 100)

#             # Retrieve existing values
#             loan_total = user.loan_owed
#             loan_limit = user.loan_limit

#             # Update values
#             loan_total += amount_requested
#             loan_limit -= amount_requested 

#             user.loan_owed = loan_total
#             user.loan_limit = loan_limit
#             user.save()       
            
#             amount_to_install = amount_requested / 90
#             loan = Loan(
#                 user=user,
#                 amount=amount_requested,
#                 amount_disbursed = total_disbursed,
#                 interest_rate=interest_rate,
#                 duration_months=3, 
#                 application_date=timezone.now().date(),
#                 is_approved=True,
#                 is_active=True,
#                 disbursed=True,
#                 purpose=validated_data['purpose'],
#                 due_date=timezone.now().date() + timedelta(days=90),  # Set your desired due date
#                 installment_amount=amount_to_install,
#                 loan_owed=loan_total,
#                 loan_limit = loan_limit,

#             )

#             loan.save()
#             Transaction.objects.create(                                         
#                 user=user,
#                 amount=amount_requested,
#                 description=f"Loan request for {amount_requested}",
#                 transaction_type='expense',
#                 loan=loan,
#                 is_successful=True
#             )           

#             print(f"Loan limit after request: {user.loan_limit}")

#             return loan
#         else:
#             error_message = "Cannot access a loan based on specified conditions."
#             # if user.loan_limit == 0 and active_loan:
#             #     error_message += " Repay your existing loan to access a new one."

#             print(f"Loan request conditions not met for user: {user.username}")
#             raise serializers.ValidationError({'error': error_message})
            

# class LoanRepaymentSerializer(serializers.ModelSerializer):
#     #new_loan_limit = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
#     class Meta:
#         model = LoanRepayment
#         fields = ['amount_paid']

#     def create(self, validated_data):
#         user = self.context['request'].user
#         loan = user.loans.filter(is_active=True, disbursed=True).first()


#         if not loan:
#             raise serializers.ValidationError({'error': 'No active loan found for the user. Kindly move to the savings page to and start saving'})

#         amount_paid = validated_data['amount_paid']  # Correct field name

#         remaining_loan_amount = loan.calculate_remaining_amount()

#         if amount_paid > remaining_loan_amount:
#             # Save the excess amount to the user's savings
#             excess_amount = amount_paid - remaining_loan_amount
                       

#             # Assuming you have a Savings model
#             savings = user.savings.create(
#                 amount_saved=excess_amount,
#                 start_date=timezone.now().date(),
#                 end_date=timezone.now().date() + timezone.timedelta(days=90),
#                 purpose="Excess loan payment savings"
#             )

#             amount_paid = remaining_loan_amount  # Set amount_paid to the remaining loan amount
#             #user.loan_limit += amount_paid
#             print(f"Loan limit after repayment: {user.loan_limit}")

#         loan_repayment = LoanRepayment.objects.create(
#             loan=loan,
#             amount_paid=amount_paid
#         )

#         # user.loan_owed -= amount_paid
#         # user.loan_limit += amount_paid
#         # user.save()
#          # Retrieve existing values
#         loan_total = user.loan_owed
#         loan_limit = user.loan_limit

#             # Update values
#         loan_total -= amount_paid
#         loan_limit += amount_paid 

#         # Save changes to user
#         user.loan_owed = loan_total
#         user.loan_limit = loan_limit
#         user.save()


#         loan.make_repayment(amount_paid)
        
#         Transaction.objects.create(
#                 user=user,
#                 amount=excess_amount,
#                 description=f"Excess payment to savings for loan {loan.id}",
#                 transaction_type='income',
#                 savings=savings,  
#                 is_successful=True
#             )

#         # Make repayment and handle loan status

#         return loan_repayment
# class LoanSerializer(serializers.ModelSerializer):
#     remaining_balance = serializers.SerializerMethodField()

#     class Meta:
#         model = Loan
#         fields = ['amount', 'repaid_amount', 'total_paid', 'remaining_balance']

#     def get_remaining_balance(self, obj):
#         return obj.get_remaining_balance()
    

# class TransactionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Transaction
#         fields = '__all__'


#     def list(self, request, *args, **kwargs):
#         response = super().list(request, *args, **kwargs)
#         print(f"User: {self.request.user.username}")
#         print(response.data)  # Print the response data in the Django console
#         return response
        

class LoanRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Loan
        fields = ['amount', 'purpose']

class LoanRepaymentSerializer(serializers.ModelSerializer):
    amount_paid = serializers.IntegerField()
    class Meta:
        model = LoanRepayment
        fields = ['amount_paid']

class LoanTransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoanTransaction
        fields = '__all__'
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        print(f"User: {self.request.user.username}")
        print(response.data) 
        return response

        
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['loan_owed', 'loan_limit']


    