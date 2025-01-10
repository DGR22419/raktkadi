from django.urls import path , include
from .views import *
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)


urlpatterns = [
    # path('staff/', StaffRegisterLoginView.as_view(), name='staff-register-login'),
    path('token/', LoginView.as_view(), name='token_obtain_pair'),  # Login endpoint
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refresh token
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'), 
    path('blood-bank/', BloodBankView.as_view()),
    path('blood-bank/<str:email>/', BloodBankView.as_view()),
    path('staff/', StaffView.as_view()),
    path('staff/<str:email>/', StaffView.as_view()),
    path('donor/', DonorView.as_view()),
    path('donor/<str:email>/', DonorView.as_view()),
    path('consumer/', ConsumerView.as_view()),
    path('consumer/<str:email>/', ConsumerView.as_view())
]
