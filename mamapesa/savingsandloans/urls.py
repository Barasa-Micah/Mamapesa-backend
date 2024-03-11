from django.urls import path, include
from . import views

urlpatterns=[
    path("savings-account/", views.SavingsAccountView.as_view(), name="savings-account"),
    path("savings-items/", views.SavingsItemsView.as_view(), name="savings-items"),
    path("savings-items/<int:id>", views.SavingsItemView.as_view(), name="savings-item"),
    path("deposit-savings/<int:saving_item_id>", views.DepositSavingsView.as_view(), name="deposit-savings"),
    path("create-saving/", views.CreateSavingsView.as_view(), name="create-savings"),
    path("change-saving-period/<int:saving_item_id>", views.ChangeSavingsPeriodView.as_view(), name="change-savings-period"),
    path('loans/', views.LoanRequestView.as_view(), name='loans'),
    path('user-loan-info/', views.UserLoanInfoView.as_view(), name='user-loan-info'),
    path('repayments/', views.LoanRepaymentView.as_view(), name='repayments'),
    path('transactions/', views.LoanTransactionView.as_view(), name='transaction-list'),
]
