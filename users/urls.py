from django.urls import path
from .views import *

urlpatterns = [

    ## login urls ##
    path('login/', LoginView.as_view(), name='login'),

    ## User urls ##
    path('blood-banks/', BloodBankView.as_view(), name='blood-bank-list'),
    path('blood-banks/verified/', VerifiedBloodBankView.as_view(), name='verified-blood-bank-list'),
    path('blood-banks/<str:email>/', BloodBankView.as_view(), name='blood-bank-detail'),
    path('staff/', StaffView.as_view(), name='staff'),
    path('staff/<str:email>/', StaffView.as_view(), name='staff-detail'),
    path('donors/', DonorView.as_view(), name='donor-list'),
    path('donors/<str:email>/', DonorView.as_view(), name='donor-detail'),
    path('consumers/', ConsumerView.as_view(), name='consumers'),
    path('consumers/<str:email>/', ConsumerView.as_view(), name='consumer_detail'),

    ## Test urls ##
    path('test/bloodbank/', Test_blood_bank.as_view()),
    path('test/staff/', Test_staff.as_view()),
    path('test/donor/', Test_donor.as_view()),
    path('test/consumer/', Test_consumer.as_view()),

    ###############################################################################
]