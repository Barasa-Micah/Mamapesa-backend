from django.db import models
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db.models import Sum, F
from datetime import timedelta, date, datetime
from decimal import Decimal
from django.conf import settings
# from .newSignals import owed
from django.dispatch import receiver, Signal

# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer')
    account_number = models.CharField(max_length=20)
    id_number = models.CharField(max_length=8, null=False, blank=False)
    county = models.CharField(max_length=100, null=True, blank=True)
    loan_owed = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    loan_limit = models.DecimalField(max_digits=10, decimal_places=2, default=8000)
    trust_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def amount_borrowable(self):
        return max(self.loan_limit - self.loan_owed, Decimal('0.00'))    
    
    def update_customer_loan_owed(self):
        all_loans=self.user.loans.all()
        total=0
        for loan in all_loans:
            total+=loan.remaining_amount
        
        self.loan_owed=total
        # loan.user.customer.save()
        # total_owed = Loan.objects.filter(user=self.user, is_active=True) \
        #                      .aggregate(total_owed=Sum(F('amount') - F('repaid_amount'),
        #                                               output_field=models.DecimalField()))['total_owed'] or Decimal('0.00')
        # default_charges = Loan.objects.filter(user=self.user, is_active=True) \
        #                               .aggregate(total_default_charges=Sum('default_charges'))['total_default_charges'] or Decimal('0.00')
        # self.loan_owed = total_owed + default_charges
        # self.save()
        
    
    def __str__(self):
        return f"Details for {self.user.first_name}'s Customer profile"
    class Meta:
        db_table="Customer"
        


        
class Loan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loans')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_disbursed = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    deduction_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5)
    # ************ how are you to update 
    # amount_deducted = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    loan_duration = models.IntegerField(default = 90)
    application_date = models.DateField(default=timezone.now)
    approval_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)  # Add due_date field
    repaid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.FloatField(default=0)
    is_approved = models.BooleanField(default=False)
    payment_ref = models.CharField(max_length=25, null=True, default=None)
    is_active = models.BooleanField(default=True)
    is_disbursed = models.BooleanField(default=False)
    default_days=models.IntegerField(default=0)
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
        
        # Ensure due_date is a date object (if it's a datetime object)
        if isinstance(self.due_date, datetime):
            self.due_date = self.due_date.date()
        # _____________________________________________________________________ FUNCTION CALL
        self.generate_amount_disbursed()

        # Check if the loan is active and the due date has passed
        # if self.is_active and date.today() > self.due_date:
            # remaining_amount = self.amount - self.repaid_amount
            # **************************** _________________ ****************
            # ************ not right way to get increased amount
            # increased_amount_due_to_late_payment = remaining_amount * ((1 + self.default_rate) / 100)
            # ************______ different logic for calculating increased amount required _____ 
            # self.amount = F('amount') + increased_amount_due_to_late_payment

        # Check if the loan is fully repaid
        # ************something else needed -- today <= due_date + below
        if self.repaid_amount >= self.amount:
            self.is_active = False
            self.remaining_days = 0

        # ************????
        self.calculated_remaining_days
        
        print("Save has been done ")
        print("Save has been done ")
        print("Save has been done ")
        super().save(*args, **kwargs)

    # ************ _________________________________ unused 
    @property
    def remaining_amount(self):
        return self.total_loan - self.repaid_amount
    
    # @property
    # def amount_deducted(self):
    #     return self.total_loan - self.amount_disbursed
    
    

    @property
    def calculated_remaining_days(self):
        today = date.today()
        today = today + timedelta(days=91)
        if isinstance(self.due_date, datetime):
            self.due_date = self.due_date.date()
        if today > self.due_date:
            self.default_days = (today - self.due_date).days
            # self.save()
            # self.user.customer.update_customer_loan_owed()
            # owed.send(sender=None, loan_id=self.id)
            # print(self.id)
            return 0
        else:
            self.default_days = 0
            # self.user.customer.update_customer_loan_owed()
            # self.save()
            # owed.send(sender=None)
            return (self.due_date - today).days

    @property
    def is_overdue(self):
        return self.due_date.date<timezone.now()
    
    @property
    def default_charges(self):
        if self.calculated_remaining_days == 0:
            default_charges=self.amount_disbursed*(self.default_rate/100)*self.default_days
            return default_charges
        else:
            return 0
    @property
    def total_loan(self):
        return self.amount +self.default_charges
        


        
    
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
    user=models.OneToOneField(settings.AUTH_USER_MODEL , on_delete=models.CASCADE, related_name="savings_account")
    customer_id = models.IntegerField(null=True, default=None)
    amount_saved = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    items=models.ManyToManyField(Item ,through="SavingsItem", related_name="savings")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # start_date = models.DateField(default=timezone.now)
    # is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.phone_number} - {self.amount_saved} "

    class Meta:
        ordering = ['-created_at']
        db_table="Savings_Accounts"
        
class SavingsItem(models.Model):
    savings = models.ForeignKey('Savings', on_delete=models.CASCADE, related_name='savings_items')
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='savings_items')
    target_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_saved = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_ref = models.CharField(max_length=25, null=True, default=None)
    customer_id = models.IntegerField(null=True, default=None)
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
        if not self.achieved:
            return self.target_amount-self.amount_saved
        return 0
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
        if self.achieved:
            self.in_progress=False
            self.save()
            return True
            
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
            # _____________________________SIMULATING DAYS AHEAD__________________
            # today = today + timedelta(days=10)
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
    savings_item = models.ForeignKey(SavingsItem, on_delete=models.SET_NULL, null=True, blank=True)
    receiving_till = models.CharField(max_length=15, null=True, blank=True)
    receiving_number = models.CharField(max_length=15, null=True, blank=True)
    
    
    
    class Meta:
        db_table="Payments"
        ordering=("-payment_date",)
        
    def __str__(self):
        return f"{self.customer.user.first_name}'s {self.type} payment_number {self.id}"
    

    # @property
    # def default_days_count(self):
    #     if self.calculated_remaining_days>0:
    #         return 0
        
    #     today=timezone.now()
    #     today=today+timedelta(days=100)
    #     default_days=(today-self.due_date).days
    #     return default_days

    # @property
    # def late_payment_update(self):
    #     today = date.today()
    #     if today > self.due_date and self.is_active:
    #         remaining_amount = self.amount - self.repaid_amount
    #         # ************ not right way to get increased amount
    #         increased_amount_due_to_late_payment = remaining_amount * (1 + self.default_rate / 100)
    #         # ************ never to be modified - amount_disbursed
    #         self.amount += increased_amount_due_to_late_payment
    #         self.save()
    #         # _____________________________________________________________________ FUNCTION CALL
    #         self.user.customer.update_customer_loan_owed()
    #         # ************ why return amount
    #     return self.amount
    