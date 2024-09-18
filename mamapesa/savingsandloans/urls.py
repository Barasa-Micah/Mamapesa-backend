from django.urls import path
from . import views

urlpatterns = [
    path(
        "savings-account/", views.SavingsAccountView.as_view(), name="savings-account"
    ),
    path("savings-items/", views.SavingsItemsView.as_view(), name="savings-items"),
    path(
        "savings-items/<int:id>/", views.SavingsItemView.as_view(), name="savings-item"
    ),
    path(
        "deposit-savings/<int:saving_item_id>/",
        views.DepositSavingsView.as_view(),
        name="deposit-savings",
    ),
    # path("withdraw-savings/<int:saving_item_id>/", views.WithdrawSavingsToSupplier.as_view(), name="withdraw-savings"),
    # path("suspend-savings-items/<int:saving_item_id>", views.SuspendSavingsItemView.as_view(), name="suspend-savings-items"),
    path("create-saving/", views.CreateSavingsView.as_view(), name="create-savings"),
    # path("change-saving-period/<int:saving_item_id>", views.ChangeSavingsPeriodView.as_view(), name="change-savings-period"),
    path(
        "withdraw-to-supplier/<int:saving_item_id>/",
        views.WithdrawSavingsToSupplier.as_view(),
        name="withdraw-to-supplier",
    ),
    # path("savings-transactions/", views.SavingsTransactionsView.as_view(), name='savings-transaction-list'),
    path("request-loan/", views.LoanRequestView.as_view(), name="loans"),
    path("repay-loan/", views.LoanRepaymentView.as_view(), name="repayments"),
    path("transactions/", views.TransactionView.as_view(), name="transaction-list"),
    path("user-loan-info/", views.UserLoanInfoView.as_view(), name="user-loan-info"),
    path("specific-loan/<int:id>/", views.SpecificLoan.as_view(), name="specific-loan"),
    path("customer-info/", views.CustomerAccountView.as_view(), name="customer-info"),

    # Group savings management URLs
    path('group-savings/', views.GroupSavingView.as_view(), name='group-savings-list-create'),  # List all groups and create a new group
    path('group-savings/<str:unique_code>/', views.GroupSavingView.as_view(), name='group-savings-detail-update-delete'),  # Get, update, or delete a specific group by unique code
    path('group-savings/<str:unique_code>/members/', views.GroupSavingView.as_view(), name='group-savings-members'),  # Add a member or get members of a specific group

    # New URLs
    path('generate-invite-code/<int:group_id>/', views.GenerateInviteCodeView.as_view(), name='generate-invite-code'),
    path('admin-group-transactions/<str:unique_code>/', views.AdminGroupTransactionsView.as_view(), name='admin-group-transactions'),
    path('join-group/', views.JoinGroupView.as_view(), name='join-group'),
    path('join-group/<str:unique_code>/', views.JoinGroupView.as_view(), name='get-group-members'),
    path('all-groups/', views.GroupListView.as_view(), name='all-groups'),
]
