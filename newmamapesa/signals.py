from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.db.models import Sum, F
from decimal import Decimal
from newmamapesa.models import Savings, SavingsItem, Loan, Customer
from django.db import models 

# Assuming CustomUser is a model from settings.AUTH_USER_MODEL
CustomUser = settings.AUTH_USER_MODEL

@receiver(post_save, sender=CustomUser)
def create_savings_and_customer_on_user_creation(sender, instance, created, **kwargs):
    if created:
        Savings.objects.create(user=instance)
        Customer.objects.create(user=instance)

@receiver(post_save, sender=SavingsItem)
def update_savings_item_on_creation(sender, instance, created, **kwargs):
    if created:
        instance.target_amount = instance.item.price  # Ensure 'item' attribute exists in SavingsItem and has a 'price' field
        instance.save()

@receiver(post_save, sender=Loan)
def update_loan_owed_on_save(sender, instance, **kwargs):
    # Ensure the customer's loan_owed is updated when a loan is saved
    if hasattr(instance.user, 'customer'):
        update_customer_loan_owed(instance.user.customer)

@receiver(post_delete, sender=Loan)
def update_loan_owed_on_delete(sender, instance, **kwargs):
    # Ensure the customer's loan_owed is updated when a loan is deleted
    if hasattr(instance.user, 'customer'):
        update_customer_loan_owed(instance.user.customer)

def update_customer_loan_owed(customer):
    # Correctly access loans through the user associated with the customer
    total_owed = Loan.objects.filter(user=customer.user, is_active=True).aggregate(
        total_owed=Sum(F('amount') - F('repaid_amount'), output_field=models.DecimalField())
    )['total_owed'] or Decimal('0.00')
    
    # Update the Customer model's loan_owed field with the calculated total
    customer.loan_owed = total_owed
    customer.save()