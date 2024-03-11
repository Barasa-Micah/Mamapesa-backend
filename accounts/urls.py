from django.urls import path
from . import views

urlpatterns=[
    path('login/',views.LoginWithToken.as_view(),name="login"),
    path('register/', views.user_registration, name='register'),
]

