from rest_framework import serializers
from savingsandloans.models import Group, GroupMember, Loan, Savings, SavingsItem, Item, Payment, Customer


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

class GroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMember
        fields = ['id', 'group', 'name', 'total_contributed', 'is_admin', 'joined_at', 'contribution_percentage']
    def get_contribution_percentage(self, obj):
        """
        Calculate the member's contribution as a percentage of the group's target amount.
        """
        if obj.group.target_amount and obj.group.target_amount > 0:
            return (obj.total_contributed / obj.group.target_amount) * 100
        return 0.0

    def validate_total_contributed(self, value):
        """
        Ensure that the total contributed by a member is a non-negative number.
        """
        if value < 0:
            raise serializers.ValidationError("Total contributed cannot be negative.")
        return value

    def validate(self, data):
        """
        Ensure that a member cannot join the same group twice.
        """
        group = data.get('group')
        name = data.get('name')

        if GroupMember.objects.filter(group=group, name=name).exists():
            raise serializers.ValidationError(f"Member with name {name} is already part of this group.")
        
        return data

    def create(self, validated_data):
        """
        Custom create method to automatically assign the first member of the group as an admin.
        """
        group = validated_data['group']

        # Automatically assign the first member of the group as an admin
        if not GroupMember.objects.filter(group=group).exists():
            validated_data['is_admin'] = True

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Custom update method to adjust total contribution dynamically.
        """
        # Update total contributed if provided
        if 'total_contributed' in validated_data:
            instance.total_contributed = validated_data['total_contributed']

        # If the user is being promoted/demoted as admin, update accordingly
        if 'is_admin' in validated_data:
            instance.is_admin = validated_data['is_admin']

        instance.save()
        return instance


class GroupSerializer(serializers.ModelSerializer):
    members = GroupMemberSerializer(many=True, read_only=True)  # Nested serializer for group members
    due_date = serializers.ReadOnlyField()  # Using the calculated `due_date` property
    remaining_days = serializers.ReadOnlyField()  # Using the calculated `remaining_days` property

    class Meta:
        model = Group
        fields = [
            'unique_code',
            'group_name',
            'target_amount',
            'total_amount_saved',
            'description',
            'is_chama',
            'validity_months',
            'start_date',
            'installments',
            'due_date',
            'remaining_days',
            'members',  # Nested group members
        ]