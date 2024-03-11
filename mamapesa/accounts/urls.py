from django.urls import path
from . import views

urlpatterns=[
    path('login/',views.LoginWithToken.as_view(),name="login"),
    path('testing/',views.TestView.as_view(),name="testing"),
    path('register/', views.user_registration, name='register'),
    #  path('login/', views.UserLoginView.as_view(), name='login'),
]

