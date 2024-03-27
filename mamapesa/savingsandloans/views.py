from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .api.stk_push import make_stk_push_request
from .serializers import (
    SavingsAccountSerializer,
    SavingsItemSerializer,
    LoanRequestSerializer,
    CustomUserSerializer,
    CustomerAccountSerializer,
    PaymentSerializer,
    LoanSerializer,
)
from rest_framework import status, generics
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Savings, SavingsItem, Item, Payment, Loan, Customer
from decimal import Decimal
from .signals import (
    after_deposit,
    loan_disbursed,
    update_transaction_status,
    after_loan_repayment,
    update_savings_payment_status,
)

# from .serializer_helpers import get_all_transactions
from django.utils import timezone
from rest_framework.exceptions import ValidationError


class SavingsAccountView(APIView):
    """
    API endpoint for retrieving savings accounts.
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Retrieve the savings account associated with the authenticated user
        savings_account = get_object_or_404(Savings, user=user)
        serializer = SavingsAccountSerializer(savings_account)
        # Return the serialized data as JSON response
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)


class CustomerAccountView(APIView):
    """
    API endpoint for retrieving customer accounts.
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Retrieve the savings account associated with the authenticated user
        customer_account = get_object_or_404(Customer, user=user)
        serializer = CustomerAccountSerializer(customer_account)
        # Return the serialized data as JSON response
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)


class SavingsItemsView(APIView):
    """
    API endpoint for retrieving the items a user is saving towards
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # retrieving the savings items associated to a user's savings account
        all_savings_items = SavingsItem.objects.filter(savings=user.savings_account)

        serializer = SavingsItemSerializer(all_savings_items, many=True)

        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)


class SavingsItemView(APIView):
    """
    API endpoint for retrieving a specific saving item by id
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        user = request.user
        condition1 = {"savings": user.savings_account}
        condition2 = {"id": id}
        # filtering the savings item belonging to user's savings account and by id
        specific_savings_item = SavingsItem.objects.filter(
            **condition1, **condition2
        ).first()
        # incase user wants to access another user's savings item
        if not specific_savings_item:
            response_dict = dict(error="Resource not found")
            return Response(response_dict, status=status.HTTP_404_NOT_FOUND)
        # print()
        serializer = SavingsItemSerializer(specific_savings_item)
        # print(serializer.data)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)


class DepositSavingsView(APIView):
    """
    API endpoint for depositing into a specific savings item
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, saving_item_id):
        user = request.user
        specific_save_item = get_object_or_404(SavingsItem, id=saving_item_id)
        # checking if saving item belong to the user
        if specific_save_item.savings.user == user:
            deposit_amount = request.data.get("deposit_amount")
            phone_number = request.data.get("phone_number")
            # amount=request.data.get("amount")
            # payment method id
            payment_method = request.data.get("payment_method")
            # if payment_method not provided default to 1
            if not payment_method:
                payment_method = 1
                # handle payment here

            if deposit_amount:
                # add the deposited amount to the amount saved
                specific_save_item.amount_saved += deposit_amount
                specific_save_item.save()
                # send SIGNAL to create transaction____________________________
                after_deposit.send(
                    sender=None,
                    user=user,
                    amount=deposit_amount,
                    type="Savings Deposit",
                    transaction_id="",
                    payment_ref="",
                    status="pending",
                    savings_item=specific_save_item,
                )
                # call stk push to pay
                response_code, response_data = make_stk_push_request(
                    deposit_amount, phone_number, specific_save_item.item.name
                )
                
                if response_code == 200:
                    deposit_successful = True
                else:
                    deposit_successful = False
                    # return payment error
                # PAYMENT COMPLETED
                if deposit_successful:
                    update_savings_payment_status.send(
                        sender=None,
                        user=user,
                        savings_item=specific_save_item,
                        status="completed",
                        type="Savings Deposit",
                    )
                else:
                    update_savings_payment_status.send(
                        sender=None,
                        user=user,
                        savings_item=specific_save_item,
                        status="failed",
                        type="Savings Deposit Payment Failed",
                    )

                response_dict = dict(message="Deposit successful")
                return JsonResponse(response_dict, status=status.HTTP_202_ACCEPTED)
            else:
                response_dict = dict(error="Provide the deposit amount")
                return JsonResponse(response_dict, status=status.HTTP_400_BAD_REQUEST)
        else:
            response_dict = dict(
                error="Sorry the requested resource could not be found"
            )
            return JsonResponse(response_dict, status=status.HTTP_404_NOT_FOUND)


class CreateSavingsView(APIView):
    """
    API endpoint for creating a new savings item
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        received_item_name = request.data.get("item_name")
        received_item_price = request.data.get("item_price")
        saving_period = request.data.get("saving_period")
        phone_number = request.data.get("phone_number")
        initial_deposit = request.data.get("initial_deposit")

        # handle payment here
        if phone_number and initial_deposit:
             # call stk push to pay
            response_code, response_data = make_stk_push_request(
                initial_deposit, phone_number, received_item_name
            )
            
            if response_code == 200:
                deposit_successful = True
            else:
                deposit_successful = False
                
        # start creation process if received item name and price exist
        if deposit_successful:
            #  REASON: no Items available from supplier for now, CREATE an item and associate it with the user's savings
            new_item = Item(name=received_item_name, price=received_item_price)
            new_item.description = f"An item called {received_item_name}"
            new_item.save()
            user = request.user
            # associating item to a SavingsItem instance
            new_savings_item = SavingsItem(item=new_item, savings=user.savings_account)
            new_savings_item.target_amount = received_item_price
            # if saving period provided use it ELSE use the database default
            if saving_period:
                new_savings_item.saving_period = saving_period
            new_savings_item.save()
            response_dict = dict(message="Item added successfully to savings items!!")
            # returning created savings Item to user
            response_dict["saving_item"] = dict(
                name=new_savings_item.item.name,
                start_date=new_savings_item.start_date,
                end_date=new_savings_item.due_date,
                duration=new_savings_item.saving_period,
            )
            return JsonResponse(response_dict, status=status.HTTP_201_CREATED)
        else:
            response_dict = dict(
                message="Payment failed please pay depsoit amount"
            )
            return JsonResponse(response_dict, status=status.HTTP_400_BAD_REQUEST)


# class ChangeSavingsPeriodView(APIView):
#     """
#     API endpoint for changing the savings period od savings item
#     """
#     authentication_classes = [SessionAuthentication, TokenAuthentication]
#     permission_classes = [IsAuthenticated]
#     def post(self, request, saving_item_id):
#         new_savings_period=request.data.get("new_savings_period")
#         # if savings period provided
#         if new_savings_period:
#             user=request.user
#             specific_savings_item=get_object_or_404(SavingsItem, id=saving_item_id)
#             # verify if savings item belongs to the current user
#             if specific_savings_item.savings.user==user:
#                 previous_end_date=specific_savings_item.due_date
#                 specific_savings_item.saving_period=new_savings_period
#                 specific_savings_item.save()

#                 response_dict=dict(message="Successfully updated savings period")
#                 # returning the changes as response
#                 response_dict["item"]=dict(name=specific_savings_item.item.name, price=specific_savings_item.item.price)
#                 response_dict["previous_end_date"]=previous_end_date
#                 response_dict["new_end_date"]=specific_savings_item.due_date
#                 return JsonResponse(response_dict, status=status.HTTP_200_OK)
#             # handle response if savings item does not belong to user
#             else:
#                 response_dict=dict(message="The resource could not be found")
#                 return JsonResponse(response_dict, status=status.HTTP_404_NOT_FOUND)
#         #if savings period not provided
#         else:
#             response_dict=dict(message="Please provide the necessary data i.e new_savings_period ")
#             return JsonResponse(response_dict, status=status.HTTP_400_BAD_REQUEST)

# class SavingsTransactionsView(APIView):
#     """
#     API endpoint for retrieving transactions of a user
#     """
#     authentication_classes = [SessionAuthentication, TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user=request.user
#         all_savings_items=SavingsItem.objects.filter(savings=user.savings_account)
#         # calling function to get transactions
#         all_transactions=get_all_transactions(all_savings_items)
#         # if there are transactions
#         if all_transactions:
#             serializer=SavingsTransactionSerializer(all_transactions, many=True)
#             return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
#         else:
#             response_dict=dict(message="No transactions")
#             return JsonResponse(response_dict, status=status.HTTP_400_BAD_REQUEST)


class WithdrawSavingsToSupplier(APIView):
    """
    API endpoint for withdrawing to supplier till after savings target reached
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, saving_item_id):

        user = request.user
        condition1 = {"savings": user.savings_account}
        condition2 = {"id": saving_item_id}
        # filtering the savings item belonging to user's savings account and by id
        specific_savings_item = SavingsItem.objects.filter(
            **condition1, **condition2
        ).first()
        # incase user wants to access another user's savings item
        if not specific_savings_item:
            response_dict = dict(error="Resource not found")
            return Response(response_dict, status=status.HTTP_404_NOT_FOUND)

        # getting specific savings item to withdraw from
        specific_savings_item = get_object_or_404(SavingsItem, id=saving_item_id)
        supplier_till = request.data.get("supplier_till")
        amount = request.data.get("withdraw_amount")  # optional
        # handle if supplier till not provided
        if not supplier_till:
            response_dict = dict(message="Supplier till not provided")
            return JsonResponse(response_dict, status=status.HTTP_400_BAD_REQUEST)
        # check if target achieved
        if not specific_savings_item.achieved:
            response_dict = dict(message="Target amount not reached")
            return JsonResponse(response_dict, status=status.HTTP_400_BAD_REQUEST)

        # handle if supplier till provided

        if amount:
            # prevent user from using app money, only used amount saved
            if Decimal(amount) > specific_savings_item.amount_saved:
                response_dict = dict(message="Not enough funds in account")
                return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        # print("Done to here!!")

        if amount:
            amount_paid_to_till = Decimal(amount)
        # if amount not provided, use target_amount for the savings item
        if not amount:
            amount_paid_to_till = specific_savings_item.target_amount

        # ______________ TRYING TO WITHDRAW EXTRA FUNDS ______________________________________________________________________
        if specific_savings_item.achieved & (
            specific_savings_item.amount_saved < specific_savings_item.target_amount
        ):
            if amount:
                extra_funds_to_withdraw = Decimal(amount)
            # if amount not provided, use target_amount for the savings item
            if not amount:
                extra_funds_to_withdraw = specific_savings_item.amount_saved
            # extra_funds_to_withdraw=specific_savings_item.amount_saved

            after_deposit.send(
                sender=None,
                user=user,
                amount=extra_funds_to_withdraw,
                type="Supplier Withdrawal",
                transaction_id="",
                payment_ref="",
                status="pending",
                savings_item=specific_savings_item,
                receiving_till=supplier_till,
            )
            withdraw_successful = False
            # ______________SIMULATING PAYMENT INTEGRATION__________________
            withdraw_successful = True
            # PAYMENT COMPLETED

            specific_savings_item.in_progress = False
            specific_savings_item.achieved = True
            specific_savings_item.save()

            if withdraw_successful:
                specific_savings_item.amount_saved -= extra_funds_to_withdraw
                specific_savings_item.save()

                update_savings_payment_status.send(
                    sender=None,
                    user=user,
                    savings_item=specific_savings_item,
                    status="completed",
                    type="Supplier Withdrawal",
                )

                response_dict = dict(
                    message=f"Withdrawal successful to supplier => Amount :{extra_funds_to_withdraw}"
                )
                return JsonResponse(response_dict, status=status.HTTP_200_OK)
            else:
                update_savings_payment_status.send(
                    sender=None,
                    user=user,
                    savings_item=specific_savings_item,
                    status="failed",
                    type="Supplier Withdrawal",
                )
                response_dict = dict(message="Withdrawal failed")
                return JsonResponse(response_dict, status=status.HTTP_400_BAD_REQUEST)

            # response_dict=dict(message="Withdrawing extra funds")
            # return Response(response_dict, status=status.HTTP_200_OK)

        after_deposit.send(
            sender=None,
            user=user,
            amount=amount_paid_to_till,
            type="Supplier Withdrawal",
            transaction_id="",
            payment_ref="",
            status="pending",
            savings_item=specific_savings_item,
            receiving_till=supplier_till,
        )

        withdraw_successful = False
        # ______________SIMULATING PAYMENT INTEGRATION__________________
        withdraw_successful = True
        # PAYMENT COMPLETED

        specific_savings_item.in_progress = False
        specific_savings_item.achieved = True
        specific_savings_item.save()

        if withdraw_successful:
            specific_savings_item.amount_saved -= amount_paid_to_till
            specific_savings_item.save()

            update_savings_payment_status.send(
                sender=None,
                user=user,
                savings_item=specific_savings_item,
                status="completed",
                type="Supplier Withdrawal",
            )

            response_dict = dict(message="Withdrawal successful to supplier")
            return JsonResponse(response_dict, status=status.HTTP_200_OK)
        else:

            update_savings_payment_status.send(
                sender=None,
                user=user,
                savings_item=specific_savings_item,
                status="failed",
                type="Supplier Withdrawal",
            )

            response_dict = dict(message="Withdrawal failed")
            return JsonResponse(response_dict, status=status.HTTP_400_BAD_REQUEST)

        # handle if savings is done (i.e in_progress=False) to withdraw extra funds
        # It was toggled to in_progress=False when the savings target amount reached AND PAID to supplier
        # else:
        #     # if extra funds to be withdrawn are available in account
        #     if amount:
        #         if Decimal(amount)>specific_savings_item.amount_saved:
        #             response_dict=dict(message="Not enough funds in account")
        #             return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        #         else:
        #             payment_successful=False
        #             # handle payment of extra funds to gateway

        #             payment_successful=True

        #             if payment_successful:
        #                 specific_savings_item.amount_saved-=amount
        #                 specific_savings_item.save()

        #                 response_dict=dict(message="Withdrawal of extra funds successful")
        #                 return Response(response_dict, status=status.HTTP_200_OK)


class LoanRequestView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def post(self, request):
        amount = request.data.get("amount")

        user = request.user

        # loan_limit=user.customer.loan_limit

        if not amount:
            response_dict = dict(error="amount not provided")
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)

        eligibility_check = self.check_loan_eligibility(user, amount)
        if eligibility_check["is_eligible"]:

            loan = user.loans.create(amount=amount)
            loan.save()

            user.customer.loan_owed += amount
            user.customer.save()

            # _______________________SIGNAL______________
            loan_disbursed.send(
                sender=None,
                user=user,
                amount=amount,
                transaction_id="",
                payment_ref="",
                loan=loan,
            )

            disbursement_successful = False

            # SIMULATING PAYMENT INTEGRATION ______________________

            disbursement_successful = True

            # ____________________PAYMENT DONE__________________
            if disbursement_successful:
                loan.is_disbursed = True
                loan.is_approved = True
                loan.approval_date = timezone.now()
                loan.save()
                loan.calculated_remaining_days

                update_transaction_status.send(
                    sender=None, type="Loan Disbursement", loan=loan, status="completed"
                )

            else:
                update_transaction_status.send(
                    sender=None, loan=loan, type="Loan Disbursement", status="failed"
                )

            response_dict = dict(
                success=True, message="Loan request successful", amount=amount
            )
            return Response(response_dict, status=status.HTTP_201_CREATED)

        else:
            response_dict = dict(
                success=False,
                error="Not eligible for loan",
                amount_borrowable=user.customer.amount_borrowable,
            )
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)

    def check_loan_eligibility(self, user, amount_requested):
        if user.customer.loan_owed + amount_requested > user.customer.loan_limit:
            return {
                "is_eligible": False,
                "error": "Loan limit exceeded due to existing debt.",
            }

        # if amount_requested > user.customer.amount_borrowable:
        #     return {'is_eligible': False, 'error': "Requested loan exceeds borrowable limit."}

        return {"is_eligible": True, "error": None}


class LoanRepaymentView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        amount_paid = request.data.get("amount")
        if not amount_paid:
            response_dict = dict(error="amount_paid not provided")
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)

        if amount_paid > 0:
            all_loans = user.loans.filter(is_active=True)
            if all_loans.exists():
                total_remaining_loan_amount = user.customer.loan_owed

                if amount_paid > total_remaining_loan_amount:
                    raise ValidationError(
                        f"Amount paid ({amount_paid}) exceeds the total remaining loan amount ({total_remaining_loan_amount})"
                    )

                user.customer.loan_owed -= amount_paid
                user.customer.save()

                amount_to_redistribute = amount_paid
                repayment_successful = False

                for loan in all_loans:
                    if amount_to_redistribute <= 0:
                        break

                    repayment_amount = min(
                        amount_to_redistribute, loan.remaining_amount
                    )
                    if repayment_amount > loan.remaining_amount:
                        remaining_amount = loan.remaining_amount
                        raise ValidationError(
                            f"Amount paid exceeds the remaining loan amount ({remaining_amount})"
                        )

                    loan.repaid_amount += repayment_amount
                    user.customer.loan_owed -= repayment_amount
                    loan.save()

                    if repayment_amount != 0:
                        after_loan_repayment.send(
                            sender=None,
                            user=user,
                            amount=repayment_amount,
                            transaction_id="",
                            payment_ref="",
                            loan=loan,
                        )

                    amount_to_redistribute -= repayment_amount

                    # user.customer.update_customer_loan_owed()

                    # SIMULATING PAYMENT INTEGRATION ______________________
                    repayment_successful = (
                        True  # Update this based on actual payment integration
                    )

                # ____________________PAYMENT DONE__________________
                if repayment_successful:
                    response_dict = dict(message="Repayment of loan successful")
                    for loan in all_loans:
                        update_transaction_status.send(
                            sender=None,
                            loan=loan,
                            type="Loan Repayment",
                            status="completed",
                        )
                    return Response(response_dict, status=status.HTTP_200_OK)
                else:
                    response_dict = dict(
                        success=False,
                        message="Loan repayment failed",
                        amount=amount_paid,
                    )
                    for loan in all_loans:
                        update_transaction_status.send(
                            sender=None,
                            loan=loan,
                            type="Loan Repayment",
                            status="failed",
                        )
                    return Response(response_dict, status=status.HTTP_201_CREATED)
            else:
                response_dict = dict(message="No active loans found")
                return Response(response_dict, status=status.HTTP_200_OK)
        else:
            response_dict = dict(message="Amount not provided or invalid")
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)


class UserLoanInfoView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        loans = user.loans.all().order_by("-created_at")

        # user.customer.update_customer_loan_owed()

        # for loan in loans:
        #     if callable(getattr(loan, 'late_payment_update', None)):
        #         loan.late_payment_update()

        #     loan.remaining_days = loan.calculated_remaining_days

        return loans


class SpecificLoan(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        loan = Loan.objects.get(pk=id)
        serializer = LoanSerializer(loan)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransactionView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # transactions=Payment.objects.filter(type__ne="Loan Service Charge")
        transactions = Payment.objects.exclude(type="Loan Service Charge")
        serializer = PaymentSerializer(transactions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
