from rest_framework import serializers
from newmamapesa.models import Loan, LoanRepayment,Savings, SavingsItem,SavingsTransaction, Item, LoanTransaction
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
        
# class SavingsItemSerializer2(serializers.ModelSerializer):
#     item=ItemSerializer()
#     # start_date = serializers.DateField(format='%Y-%m-%d')
#     # due_date = serializers.DateField(format='%Y-%m-%d')
#     class Meta:
#         model=SavingsItem
#         # fields=["id","item","amount_saved","target_amount","start_date","remaining_amount","daily_payment","remaining_days", "due_date","achieved","in_progress"]
#         fields=["id","item","amount_saved","target_amount","start_date","end_date"]

class SavingsTransactionSerializer(serializers.ModelSerializer):
    # item=
    class Meta:
        model=SavingsTransaction
        fields=["id", "type", "amount","timestamp"]
        
class LoanRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Loan
        fields = ['amount', 'purpose']

class LoanRepaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoanRepayment
        fields = ['amount_paid']

class LoanTransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoanTransaction
        fields = ['amount']

        

    

    