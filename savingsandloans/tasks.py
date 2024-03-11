#This is the folder that is used to handle the loans celery

from celery import shared_task
from newmamapesa.models import Loan, CustomUser
from datetime import date

@shared_task
def apply_late_payment_interest():
    for loan in Loan.objects.filter(due_date__lt=date.today(), is_active=True):
        loan.check_and_update_loan_owed_due_to_late_payment()


@shared_task
def recalculate_users_total_loan_owed():
    for user in CustomUser.objects.all():
        user.update_loan_owed()

