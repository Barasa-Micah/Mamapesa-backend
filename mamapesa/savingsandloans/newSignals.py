# from django.dispatch import Signal, receiver
# from .models import Loan
# owed=Signal()
# @receiver(owed, sender=None)
# def update_loan_owed(sender, **kwargs):
#     loan_id=kwargs["loan_id"]
#     loan=Loan.objects.get(pk=loan_id)
#     print(f"Received loan id {loan_id}")
    
#     all_loans=loan.user.loans.all()
#     total=0
#     for loan in all_loans:
#         total+=loan.remaining_amount
    
#     loan.user.customer.loan_owed=total
#     loan.user.customer.save()
#     print(f"new loan owed {loan.user.customer.loan_owed}")
#     # user=kwargs["user"]
    
#     # # instance=kwargs.get("instance")
#     # all_loans=user.loans.all()
#     # total=0
#     # for loan in all_loans:
#     #     total+=loan.remaining_amount
    
#     # user.customer.loan_owed=total
#     # user.customer.save()