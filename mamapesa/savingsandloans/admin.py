from django.contrib import admin

# Register your models here.

from newmamapesa.models import Loan, LoanTransaction, LoanRepayment

admin.site.register(Loan)
admin.site.register(LoanTransaction)
admin.site.register(LoanRepayment)
