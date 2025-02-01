from django.urls import path
from .views import BloodBagCreateAPIView , BloodRequestCreateView , BloodRequestResponseView , BloodBanksByBloodGroupView

urlpatterns = [
    path('create/', BloodBagCreateAPIView.as_view(), name='blood-bag-create'),
    path('request/create/', BloodRequestCreateView.as_view(), name='blood-request-create'),
    path('request/<int:pk>/respond/', BloodRequestResponseView.as_view(), name='blood-request-respond'),
    path('blood-banks/<str:blood_group>/', BloodBanksByBloodGroupView.as_view(), name='blood-banks-by-blood-group'),
]