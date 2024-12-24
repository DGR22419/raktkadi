from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MedicalCenterViewSet, 
    PatientViewSet, 
    DonorViewSet, 
    BloodRequestViewSet, 
    RegularUserViewSet,
    CustomTokenObtainPairView
)
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'medical-centers', MedicalCenterViewSet)
router.register(r'patients', PatientViewSet)
router.register(r'donors', DonorViewSet)
router.register(r'blood-requests', BloodRequestViewSet)
router.register(r'regular-users', RegularUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
