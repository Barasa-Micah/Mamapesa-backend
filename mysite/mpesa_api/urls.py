from django.urls import path

from . import views

# URL pattern for getting M-Pesa access token
urlpatterns = [
    # Existing endpoints
    # path('access/token', views.getAccessToken, name='get_mpesa_access_token'),
    # path('online/lipa', views.lipa_na_mpesa_online, name='lipa_na_mpesa'),
    # path('c2b/register', views.register_urls, name="register_mpesa_validation"),
    # path('c2b/confirmation', views.confirmation, name="confirmation"),
    # path('c2b/validation', views.validation, name="validation"),
    # path('c2b/callback', views.call_back, name="call_back"),
    
    # New endpoints
    # path('group/join', views.join_group, name='join_group'),
    # path('group/<str:unique_code>/details', views.get_group_details, name='get_group_details'),
    # path('group/<int:group_id>/invite_code', views.generate_invite_code, name='generate_invite_code'),
    # path('group/<str:unique_code>/edit', views.edit_group, name='edit_group'),
    # path('group/<str:unique_code>/members', views.fetch_members, name='fetch_members'),
    # path('group/<str:unique_code>/admin/transactions', views.admin_group_transactions, name='admin_group_transactions'),
]
