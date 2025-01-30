from django.urls import path
from .views import BloodBagCreateAPIView

urlpatterns = [
    path('create/', BloodBagCreateAPIView.as_view(), name='blood-bag-create'),
]