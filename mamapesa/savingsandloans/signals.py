from django.dispatch import receiver, Signal

# from newmamapesa.models import SavingsItem, SavingsTransaction, LoanTransaction
from accounts.models import CustomUser
from .models import Customer, Loan, SavingsItem, Payment, Savings
from django.db.models.signals import post_save
from decimal import Decimal
from django.db.models import Q
from django.conf import settings


CustomUser = settings.AUTH_USER_MODEL


@receiver(post_save, sender=CustomUser)
def create_savings_account_on_user_creation(sender, instance, created, **kwargs):
    if created:
        Savings.objects.create(user=instance)
        Customer.objects.create(user=instance)


@receiver(post_save, sender=SavingsItem)
def create_savings_account_on_user_creation(sender, instance, created, **kwargs):
    if created:
        instance.target_amount = instance.item.price
        instance.save()


@receiver(post_save, sender=SavingsItem)
def update_saving_account_total_amount(sender, instance, created, **kwargs):
    all_savings_items = instance.savings.savings_items.all()
    total_price = Decimal("0.00")
    for each in all_savings_items:
        total_price += each.amount_saved

    instance.savings.amount_saved = total_price
    instance.savings.save()


# after_deposit - signal sent after a deposit is made
after_deposit = Signal()


@receiver(after_deposit, sender=None)
def create_a_transaction(sender, **kwargs):
    customer = kwargs["user"].customer
    amount = kwargs["amount"]
    type = kwargs["type"]
    transaction_id = kwargs["transaction_id"]
    payment_method = 1
    payment_ref = kwargs["payment_ref"]
    status = kwargs["status"]
    savings_item = kwargs["savings_item"]
    receiving_till = kwargs.get("receiving_till")

    new_payment = Payment(
        customer=customer,
        amount=amount,
        type=type,
        transaction_id=transaction_id,
        payment_method_id=payment_method,
        payment_ref=payment_ref,
        status=status,
        savings_item=savings_item,
        receiving_till=receiving_till,
    )
    new_payment.save()


update_savings_payment_status = Signal()


@receiver(update_savings_payment_status, sender=None)
def update_status(sender, **kwargs):
    customer = kwargs["user"].customer
    status = kwargs["status"]
    type = kwargs["type"]
    savings_item = kwargs["savings_item"]

    specific_payment = Payment.objects.filter(
        Q(customer=customer) & Q(savings_item=savings_item) & Q(type=type)
    ).first()
    specific_payment.status = status
    specific_payment.save()


loan_disbursed = Signal()


@receiver(loan_disbursed, sender=None)
def create_loan_transaction(sender, **kwargs):
    try:
        Payment.objects.create(
            customer=kwargs["user"].customer,
            amount=kwargs["amount"],
            type="Loan Disbursement",
            transaction_id=kwargs["transaction_id"],
            payment_method_id=1,
            payment_ref=kwargs["payment_ref"],
            loan=kwargs["loan"],
        )

    except KeyError as e:
        print(f"Error in create_loan_transaction signal: Missing key {e}")

    except Exception as e:
        print(f"Error in create_loan_transaction signal: {e}")


after_loan_repayment = Signal()


@receiver(after_loan_repayment, sender=None)
def create_loan_repayment(sender, **kwargs):
    try:
        Payment.objects.create(
            customer=kwargs["user"].customer,
            amount=kwargs["amount"],
            type="Loan Repayment",
            transaction_id=kwargs["transaction_id"],
            payment_method_id=1,
            payment_ref=kwargs["payment_ref"],
            loan=kwargs["loan"],
        )

        loan = kwargs["loan"]
        loan.is_disbursed = True
        loan.save()

    except KeyError as e:
        print(f"Error in create_loan_repayment signal: Missing key {e}")

    except Exception as e:
        print(f"Error in create_loan_repayment signal: {e}")


update_transaction_status = Signal()


@receiver(update_transaction_status, sender=None)
def update_transaction(sender, **kwargs):
    try:
        status = kwargs["status"]
        loan = kwargs["loan"]
        type = kwargs["type"]

        payment = Payment.objects.filter(Q(loan=loan) & Q(type=type)).first()

        if payment:
            payment.status = status
            payment.save()
        else:
            print(f"No payment record found for loan {loan} and type {type}")

    except KeyError as e:
        print(f"Error in update_transaction signal: Missing key {e}")

    except Exception as e:
        print(f"Error in update_transaction signal: {e}")


# _____
@receiver(post_save, sender=Loan)
def update_loan_owed(sender, instance, **kwargs):
    all_loans = instance.user.loans.all()
    total = 0
    for loan in all_loans:
        total += loan.remaining_amount

    instance.user.customer.loan_owed = total
    instance.user.customer.save()


# @receiver(post_save, sender=Loan)
# # @receiver(post_delete, sender=Loan)
# def update_customer_loan_owed(sender, instance, **kwargs):
#     customer = instance.user.customer
#     customer.update_customer_loan_owed()
