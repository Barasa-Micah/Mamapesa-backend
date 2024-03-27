from rest_framework import serializers
from savingsandloans.models import Loan, Savings, SavingsItem, Item, Payment, Customer


class SavingsAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Savings
        fields = ["id", "amount_saved"]


class CustomerAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "account_number",
            "id_number",
            "county",
            "loan_owed",
            "loan_limit",
            "trust_score",
        ]


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "name", "description"]


class SavingsItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = SavingsItem
        fields = [
            "id",
            "item",
            "amount_saved",
            "target_amount",
            "start_date",
            "remaining_amount",
            "installment",
            "days_payment",
            "remaining_days",
            "due_date",
            "saving_period",
            "is_achieved",
            "in_progress",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    payment_name = serializers.SerializerMethodField()
    is_addition = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            "amount",
            "type",
            "payment_name",
            "status",
            "payment_date",
            "is_addition",
        ]

    def get_payment_name(self, obj):
        return obj.payment_method.name

    def get_is_addition(self, obj):
        if obj.type == "Loan Disbursement" or obj.type == "Savings Deposit":
            return True
        return False


# class SavingsTransactionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=SavingsTransaction
#         fields=["id", "type", "amount","timestamp"]
class LoanRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ["amount"]


# class LoanTransactionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = LoanTransaction
#         fields = '__all__'


#     def list(self, request, *args, **kwargs):
#         response = super().list(request, *args, **kwargs)
#         print(f"User: {self.request.user.username}")
#         print(response.data)
#         return response
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = [
            "id",
            "amount",
            "repaid_amount",
            "calculated_remaining_days",
            "default_days",
            "application_date",
            "due_date",
            "default_rate",
            "default_charges",
            "total_loan",
            "is_overdue",
        ]


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = [
            "id",
            "amount",
            "amount_disbursed",
            "application_date",
            "due_date",
            "is_active",
            "default_days",
            "default_rate",
            "calculated_remaining_days",
            "default_charges",
            "total_loan",
            "default_days_count",
            "is_overdue",
            "remaining_amount",
        ]
