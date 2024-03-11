from django.dispatch import receiver
from newmamapesa.models import SavingsItem
from django.db.models.signals import post_save
from newmamapesa.models import LoanTransaction, Loan, LoanRepayment
from decimal import Decimal

@receiver(post_save, sender=SavingsItem)
def update_saving_account_total_amount(sender, instance, created, **kwargs):
    # if created:
    all_savings_items=instance.savings.savings_items.all()
    total_price=Decimal("0.00")
    for each in all_savings_items:
        total_price+=each.amount_saved
        
    instance.savings.amount_saved=total_price
    # print(f"done {total_price}")
    instance.savings.save()


@receiver(post_save, sender=Loan)
def create_loan_transaction(sender, instance, created, **kwargs):
    if created:
        LoanTransaction.objects.create(
            user=instance.user,
            amount=instance.amount,
            description=f"Loan request for {instance.amount}",
            type='expense',
            loan=instance,
            is_successful=True
        )

@receiver(post_save, sender=LoanRepayment)
def create_repayment_transaction(sender, instance, created, **kwargs):
    if created:
        LoanTransaction.objects.create(
            user=instance.loan.user,
            amount=instance.amount_paid,
            description=f"Loan repayment of {instance.amount_paid}",
            type='income',
            loan=instance.loan,
            is_successful=True
        )