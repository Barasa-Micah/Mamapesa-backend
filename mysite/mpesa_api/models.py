from django.db import models
from datetime import date
from dateutil.relativedelta import relativedelta

class BaseModel(models.Model):
    """
   Abstract base model with created_at and updated_at fields.
   """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# Group Model
class Group(BaseModel):
    unique_code = models.CharField(max_length=10, unique=True)
    group_name = models.CharField(max_length=100)
    target_amount = models.FloatField(null=True, blank=True)
    total_amount_saved = models.FloatField(default=0.0)
    description = models.TextField(null=True, blank=True)
    is_chama = models.BooleanField(default=False)
    validity_months = models.IntegerField(null=True, blank=True)
    start_date = models.DateField()
    installments = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Group: {self.group_name}"

    def calculate_due_date(self):
        """Calculates the due date based on the start date and validity in months."""
        if self.start_date and self.validity_months:
            due_date = self.start_date + relativedelta(months=self.validity_months)
            return due_date
        return None

    @property
    def due_date(self):
        """Returns the due date calculated by the calculate_due_date method."""
        return self.calculate_due_date()

    @property
    def remaining_days(self):
        """Calculates the days remaining until the due date."""
        if self.due_date:
            today = date.today()
            remaining = (self.due_date - today).days
            return max(remaining, 0)  # Return 0 if the date has passed
        return None

    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

# GroupMember Model
class GroupMember(BaseModel):
    group = models.ForeignKey(Group, related_name='members', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # Member's name
    total_contributed = models.FloatField(default=0.0)  # Total amount contributed by the member
    is_admin = models.BooleanField(default=False)  # If the member is an admin
    joined_at = models.DateTimeField(auto_now_add=True)  # Date the member joined

    def __str__(self):
        return f"GroupMember: {self.name} (Group: {self.group.group_name}, Admin: {self.is_admin})"
    
    class Meta:
        verbose_name = 'Group Member'
        verbose_name_plural = 'Group Members'
    

# M-pesa Payment models

class MpesaCalls(BaseModel):
    """
   Model representing a M-pesa call.
   """
    id = models.BigAutoField(primary_key=True)  # Explicitly define primary key
    ip_address = models.TextField()
    caller = models.TextField()
    conversation_id = models.TextField()
    content = models.TextField()

    class Meta:
        verbose_name = 'Mpesa Call'
        verbose_name_plural = 'Mpesa Calls'
        app_label = 'mpesa_api'


class MpesaCallBacks(BaseModel):
    """
   Model representing a M-pesa call back.
   """
    id = models.BigAutoField(primary_key=True)  # Explicitly define primary key
    ip_address = models.TextField()
    caller = models.TextField()
    conversation_id = models.TextField()
    content = models.TextField()

    class Meta:
        verbose_name = 'Mpesa Call Back'
        verbose_name_plural = 'Mpesa Call Backs'
        app_label = 'mpesa_api'


class MpesaPayment(BaseModel):
    """
   Model representing a Mpesa payment.
   """
    id = models.BigAutoField(primary_key=True)  # Explicitly define primary key
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    type = models.TextField()
    reference = models.TextField()
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.TextField()
    organization_balance = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Mpesa Payment'
        verbose_name_plural = 'Mpesa Payments'

    def __str__(self):
        return self.first_name

