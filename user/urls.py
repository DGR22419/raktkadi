from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HospitalViewSet, PatientViewSet, DonorViewSet, BloodRequestViewSet

router = DefaultRouter()
router.register(r'hospitals', HospitalViewSet)
router.register(r'patients', PatientViewSet) 
router.register(r'donors', DonorViewSet)
router.register(r'blood-requests', BloodRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
