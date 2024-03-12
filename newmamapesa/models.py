from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from datetime import timedelta, date, datetime
from decimal import Decimal
from django.conf import settings
from django.db.models import Sum, F



class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table="Users"

    def __str__(self):
        return self.username
   
    

class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer')
    account_number = models.CharField(max_length=20)
    id_number = models.CharField(max_length=20, unique=True, null=False, blank=False)
    address = models.CharField(max_length=100)
    # trust_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    loan_owed = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount_paid  = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    loan_limit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('8000'))
    verified_identity = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def amount_borrowable(self):
        return max(self.loan_limit - self.loan_owed, Decimal('0.00'))    
    
    def update_customer_loan_owed(self):
        total_owed = Loan.objects.filter(user=self.user, is_active=True) \
                             .aggregate(total_owed=Sum(F('amount') - F('repaid_amount'),
                                                      output_field=models.DecimalField()))['total_owed'] or Decimal('0.00')
   
        self.loan_owed = total_owed
        self.save()

    
    def __str__(self):
        return f"Details for {self.user.username}'s Customer profile"
    
    class Meta:
        db_table = "Customer"



class Loan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loans')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_disbursed = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    deduction_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5)
    amount_deducted = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    loan_duration = models.IntegerField(default=90)
    application_date = models.DateField(default=timezone.now)
    approval_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    repaid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_disbursed = models.BooleanField(default=False)
    default_days = models.IntegerField(default=0)
    default_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return f"{self.user.username}'s loan {self.id} of Kshs.{self.amount}"

    class Meta:
        db_table = "Loans"
        ordering = ["-due_date"]

    def generate_amount_disbursed(self):
        interest_rate = Decimal(str(self.deduction_rate))
        self.amount_disbursed = self.amount * (1 - interest_rate / 100)

    def save(self, *args, **kwargs):
        self.due_date = self.application_date + timedelta(days=self.loan_duration)
        self.generate_amount_disbursed()

        # Check if the loan is active and the due date has passed
        if self.is_active and date.today() > self.due_date.date():
            remaining_amount = self.amount - self.repaid_amount
            increased_amount_due_to_late_payment = remaining_amount * (1 + self.default_rate / 100)
            self.amount = F('amount') + increased_amount_due_to_late_payment

        # Check if the loan is fully repaid
        if self.repaid_amount >= self.amount:
            self.is_active = False
            self.remaining_days = 0

        self.calculated_remaining_days
        super().save(*args, **kwargs)

    @property
    def amount_deducted(self):
        return self.amount - self.amount_disbursed

    @property
    def calculated_remaining_days(self):
        today = date.today()
        # today = today + timedelta(days=95)
        if isinstance(self.due_date, datetime):
            self.due_date = self.due_date.date()
        if today > self.due_date:
            self.default_days = (today - self.due_date).days
            return None
        else:
            self.default_days = 0
            return (self.due_date - today).days

    @property
    def late_payment_update(self):
        today = date.today()
        if today > self.due_date and self.is_active:
            remaining_amount = self.amount - self.repaid_amount
            increased_amount_due_to_late_payment = remaining_amount * (1 + self.default_rate / 100)
            self.amount_disbursed += increased_amount_due_to_late_payment
            self.save()
            self.user.customer.update_customer_loan_owed()
        return self.amount


    @property
    def remaining_amount(self):
        return self.amount - self.repaid_amount
    
# class Trust_Score(models.Model):
#     loan = models.ForeignKey(Loan, on_delete=models.SET_NULL, null=True, blank=True)
    






    
class Item(models.Model):
    name = models.CharField(max_length=255)
    loan_count = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)   
    description = models.TextField(blank=True, null=True)
    in_stock = models.BooleanField(default=True)
    image = models.ImageField(upload_to='item_images/', blank=True, null=True)

    def __str__(self):
        return self.name 
    class Meta:
        db_table="Items"  
class Savings(models.Model):
    user=models.OneToOneField(CustomUser , on_delete=models.CASCADE, related_name="savings_account")
    amount_saved = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    items=models.ManyToManyField(Item ,through="SavingsItem", related_name="savings")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # start_date = models.DateField(default=timezone.now)
    # is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount_saved} "

    class Meta:
        ordering = ['-created_at']
        db_table="Savings_Accounts"
class SavingsItem(models.Model):
    savings = models.ForeignKey('Savings', on_delete=models.CASCADE, related_name='savings_items')
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='savings_items')
    target_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_saved = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    start_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    achieved = models.BooleanField(default=False)
    in_progress = models.BooleanField(default=True)
    saving_period=models.IntegerField(default=90)
    is_suspended=models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.item.name} for {self.savings.user.username} - Target: {self.target_amount}"
    class Meta:
        unique_together = (('savings', 'item'),)
        ordering = ['due_date']
        db_table="Savings_Items"
        
    def save(self, *args, **kwargs):
        if self.amount_saved>=self.target_amount:
            self.achieved=True
        if self.start_date:
            self.due_date = self.start_date + timedelta(days=self.saving_period)
        super().save(*args, **kwargs)
    @property
    def is_target_amount_reached(self):
        return self.amount_saved>=self.target_amount
    @property
    def remaining_amount(self):
        return self.target_amount-self.amount_saved
    @property
    def installment(self):
        return round(self.target_amount/self.saving_period, 2)
    def amount_skipped(self):
        balance=self.target_amount-self.amount_saved
        remaining_amount_to_target=self.remaining_days*self.installment
        return balance-remaining_amount_to_target
    @property
    def days_payment(self):
        remaining_day=self.remaining_days-1
        cash=remaining_day*self.installment
        total=cash+self.amount_saved
        return round(self.target_amount-total, 2)
    @property
    def is_achieved(self):
        if self.amount_saved>=self.target_amount:
            self.achieved=True
            self.in_progress=False
            self.save()
            return True
        else:
            self.achieved=False
            self.in_progress=True
            self.save()
            return False
    @property
    def remaining_days(self):
        """Calculate the number of days remaining until the savings goal is reached."""
        if self.due_date:
            today = date.today()
            today = today + timedelta(days=10)
            remaining_days = (self.due_date - today).days
            return max(0, remaining_days)
        else:
            return None

class PaymentMethod(models.Model):
    CURRENCY_OPTIONS=[
        ('KES', 'Kenyan Shilling'),
        ('USD', 'US Dollar'),
        ('UGX', 'Ugandan Shilling'),
        ('TZS', 'Tanzanian Shilling'),
        ('RWF', 'Rwandan Franc'),
        ('ETB', 'Ethiopian Birr'),
    ]
    
    name=models.CharField(max_length=30)
    description=models.TextField(blank=True)
    icon=models.ImageField(upload_to='payment_icons/', null=True, blank=True)
    active=models.BooleanField(default=True)
    payment_gateway = models.CharField(max_length=50)
    currency = models.ManyToManyField("Currency", related_name='payment_methods')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table="Payment_Methods"
        
    def __str__(self):
        return f"{self.name} payment method"

class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table="Currencies"
        
    def __str__(self):
        return self.code
    
    
class Payment(models.Model):
    STATUS_CHOICES=[
        ("PENDING","pending"),
        ("COMPLETED","completed"),
        ("FAILED","failed"),
    ]
    
    TRANSACTION_TYPES = [
        ('LOAN_DISBURSEMENT', 'Loan Disbursement'),
        ('LOAN-REPAYMENT', 'Loan Repayment'),
        ('SAVINGS_DEPOSIT', 'Savings Deposit'),
        ('SUPPLIER_WITHDRAWAL', 'Supplier Withdrawal'),
        ('LOAN_SERVICE_CHARGE', 'Loan Service Charge'),
    ]
     
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type= models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, related_name="payments", null=True)
    payment_ref = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50,choices=STATUS_CHOICES, default='pending')
    payment_date = models.DateTimeField(auto_now_add=True)
    loan = models.ForeignKey(Loan, on_delete=models.SET_NULL, null=True, blank=True)
    savings = models.ForeignKey(Savings, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table="Payments"
        
    def __str__(self):
        return f"{self.customer.user.username}'s {self.type} payment_number {self.id}"
    
class Communication(models.Model):
    COMMUNICATION_TYPES = [
        ('loan_submission', 'Loan Submission'),
        ('loan_approval', 'Loan Approval'),
        ('loan_rejection', 'Loan Rejection'),
        ('loan_disbursement', 'Loan Disbursement'),
        ('loan_payment', 'Loan Payment'),
        ('savings_deposit', 'Savings Deposit'),
        ('savings_withdrawal', 'Savings Withdrawal'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    communication_type = models.CharField(max_length=20, choices=COMMUNICATION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    
    class Meta:
        db_table="Communications"

    def __str__(self):
        return f"{self.get_communication_type_display()} for {self.user.username} at {self.timestamp}"
    
    
    
    
    
    # @property
    # def amount_borrowable(self):
    #     return self.loan_limit-self.loan_owed
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # idnumber = models.CharField(max_length=20, unique=True, blank=True, null=True)
    # email=models.EmailField(null=True, blank=True)
    # groups = models.ManyToManyField(Group, related_name='customuser_set')
    # interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5)  # Add interest_rate field
    # user_permissions = models.ManyToManyField(Permission, related_name='customuser_set')
    # loan_owed = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # loan_limit = models.DecimalField(max_digits=10, decimal_places=2, default=8000)


    # @property
    # def is_eligible(self):
    #     return self.loan_limit>0



# class SavingsTransaction(models.Model):
#     TRANSACTION_TYPES=[
#         ("WITHDRAWAL", "withdrawal"),
#         ("DEPOSIT", "deposit"),
#     ]
#     type=models.CharField(max_length=25, choices=TRANSACTION_TYPES)
#     amount=models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
#     savings_item=models.ForeignKey(SavingsItem, on_delete=models.CASCADE, related_name="transactions")
#     payment_method=models.ForeignKey("PaymentMethod", on_delete=models.SET_NULL, null=True, blank=True)
#     timestamp=models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return f"{self.savings_item.savings.user.username}'s transaction of {self.amount} on {self.timestamp}"
#     class Meta:
#         db_table="Savings_Transactions"
#         ordering=['-timestamp',]
    
  
# class LoanTransaction(models.Model):
#     user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='loan_transactions')
#     type = models.CharField(max_length=20, choices=[('LOAN_REPAYMENT', 'loan_repayment'), ('LOAN_DISBURSEMENT', 'loan_disbursement')], default="")
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     description = models.TextField(blank=True, null=True, default="")
#     timestamp = models.DateTimeField(default=timezone.now)
#     loan = models.ForeignKey('Loan', on_delete=models.SET_NULL, null=True, blank=True, related_name='loan_transactions')
#     is_successful = models.BooleanField(default=True)
  
#     def __str__(self):
#         return f"{self.type} for {self.user.username} - Amount: {self.amount} for Loan {self.pk}"
#     class Meta:
#         ordering = ['-timestamp']
#         db_table="Loan_Transactions"
 

# collateral = models.FileField(upload_to='collaterals/', blank=True, null=True)
    # grace_period = models.IntegerField(default=30)
    # grace_period_end_date = models.DateField(null=True, blank=True)  # Add due_date field
    # late_payment_penalty_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5)
   
    # def is_fully_repaid(self):
    #     return self.repaid_amount == self.amount
    
    # def calculate_remaining_amount(self):
    #     return self.amount - self.repaid_amount
    # @property
    # def remaining_amount(self):
    #     return self.amount - self.repaid_amount
    # @property
    # def remaining_days(self):
    #     today=date.today()
    #     return self.due_date-today
    # @property
    # def grace_period_remaining_days(self):
    #     today=date.today()
    #     if self.grace_period_end_date:
    #         return self.grace_period_end_date-today
    #     else:
    #         return None
    # @property
    # def is_repayment_due(self):
    #     today = date.today()
    #     due_date = self.due_date  # Convert self.due_date to datetime.date
    #     return today >= due_date
    # # amount crossed over to the grace period
    # @property
    # def overdue_fee(self):
    #     if self.grace_period_end_date:
    #         overdue_fee=self.overdue_amount*(self.late_payment_penalty_rate/100)
    #     else:
    #         overdue_fee=0
    #     return overdue_fee
    
    