from django.dispatch import receiver, Signal
# from newmamapesa.models import SavingsItem, SavingsTransaction, LoanTransaction
from newmamapesa.models import SavingsItem, Communication, Payment
from django.db.models.signals import post_save
from decimal import Decimal
from django.db.models import Q

@receiver(post_save, sender=SavingsItem)
def update_saving_account_total_amount(sender, instance, created, **kwargs):
    all_savings_items=instance.savings.savings_items.all()
    total_price=Decimal("0.00")
    for each in all_savings_items:
        total_price+=each.amount_saved
        
    instance.savings.amount_saved=total_price
    instance.savings.save()
    
# after_deposit - signal sent after a deposit is made 
after_deposit=Signal()
# @receiver(after_deposit)
# def create_a_transaction(sender, **kwargs):
#     amount=kwargs["amount"]
#     savings_item=kwargs["savings_item"]
#     payment_method=kwargs["payment_method"]
#     type=kwargs["type"]

#     new_transaction=SavingsTransaction(amount=amount, savings_item_id=savings_item, payment_method_id=payment_method, type=type)
#     new_transaction.save()


loan_disbursed=Signal()
@receiver(loan_disbursed, sender=None)
def create_loan_transaction(sender, **kwargs):
    Payment.objects.create(
        customer=kwargs["user"].customer,
        amount=kwargs["amount"],
        type='Loan Disbursement',
        transaction_id=kwargs["transaction_id"],
        payment_method_id=1,
        payment_ref=kwargs["payment_ref"],
        loan=kwargs["loan"]
    )

        
after_loan_repayment=Signal()
@receiver(after_loan_repayment, sender=None)
def create_loan_repayment(sender, **kwargs):
    Payment.objects.create(
        customer=kwargs["user"].customer,
        amount=kwargs["amount"],
        type='Loan Repayment',
        transaction_id=kwargs["transaction_id"],
        payment_method_id=1,
        payment_ref=kwargs["payment_ref"],
        loan=kwargs["loan"]
    )
    # loan=kwargs["loan"]
    # loan.is_disbursed=True
    # loan.save()




update_transaction_status=Signal()
@receiver(update_transaction_status, sender=None)
def update_transaction(sender, **kwargs):
    status=kwargs["status"]
    loan=kwargs["loan"]
    type=kwargs["type"]

    payment=Payment.objects.filter(Q(loan=loan) & Q(type=type)).first()
    payment.status=status
    payment.save()


# after_repay_loan=Signal()
# @receiver(after_repay_loan, sender=None)
# def create_transaction_after_repay(sender, **kwargs):
#     user=kwargs["user"]
#     loan=kwargs["loan"]
#     amount=kwargs["amount"]
    
#     new_loan_transaction=LoanTransaction(user=user, loan=loan, amount=amount, type="loan_repayment")
#     new_loan_transaction.save()




# @receiver(post_save, sender=Payment)
# def update_trustscore_on_payment(sender, instance, created, **kwargs):
#     if instance.status == "COMPLETED" and instance.type == 'LOAN_REPAYMENT':
#         # Assuming the Customer model has a direct link to the corresponding CustomUser
#         user = instance.customer.user
#         user.update_loan_owed()
#         user.calculate_payment_history_score() 


# @receiver(post_save, sender=Payment)
# def update_trustscore_on_payment(sender, instance, **kwargs):
#     if instance.status == "COMPLETED" and instance.type in ['LOAN_REPAYMENT', 'SAVINGS_DEPOSIT']:
#         instance.user.recalculate_trust_score()  # Assuming a method to recalculate TrustSco

# @receiver(post_save, sender=Loan)
# def handle_loan_disbursement(sender, instance, created, **kwargs):
#     if instance.is_disbursed and not instance.disbursement_communication_sent:
#         Communication.objects.create(
#             user=instance.user,
#             communication_type='loan_disbursement',
#             message=f"Your loan of {instance.amount} has been disbursed."
#         )
#         # Mark that communication has been sent to avoid duplicate entries
#         instance.disbursement_communication_sent = True
#         instance.save()


# @receiver(post_save, sender=Payment)
# def update_after_payment(sender, instance, created, **kwargs):
#     if instance.status == "COMPLETED":
#         # Update Loan Repayment
#         if instance.type == 'LOAN_REPAYMENT' and instance.loan:
#             instance.loan.repaid_amount += instance.amount
#             instance.loan.save()
            
#             # Assuming the CustomUser model has a method recalculate_trust_score()
#             instance.loan.user.recalculate_trust_score()
            
#             # Create a Communication entry for loan repayment
#             Communication.objects.create(
#                 user=instance.loan.user,
#                 communication_type='loan_payment',
#                 message=f"Your payment of {instance.amount} has been successfully processed."
#             )
            
#         # Additional communication types based on the payment instance type
#         elif instance.type == 'LOAN_DISBURSEMENT':
#             Communication.objects.create(
#                 user=instance.loan.user,
#                 communication_type='loan_disbursement',
#                 message=f"Your loan of {instance.amount} has been disbursed."
#             )