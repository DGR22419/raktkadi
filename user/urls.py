from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HospitalViewSet, PatientViewSet, DonorViewSet

router = DefaultRouter()
router.register(r'hospitals', HospitalViewSet)
router.register(r'patients', PatientViewSet) 
router.register(r'donors', DonorViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
