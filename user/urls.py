from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MedicalCenterViewSet, PatientViewSet, DonorViewSet, BloodRequestViewSet, RegularUserViewSet

router = DefaultRouter()
router.register(r'medical-centers', MedicalCenterViewSet)
router.register(r'patients', PatientViewSet) 
router.register(r'donors', DonorViewSet)
router.register(r'blood-requests', BloodRequestViewSet)
router.register(r'regular-users', RegularUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
