from rest_framework import permissions
from .models import MedicalCenter, RegularUser
import logging

logger = logging.getLogger(__name__)

class IsMedicalCenter(permissions.BasePermission):
    """
    Strict permission check for Medical Centers only
    """
    def has_permission(self, request, view):
        # Log the user type for debugging
        logger.info(f"User type checking: {type(request.user)}")
        
        # First check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Strict check if user is a MedicalCenter instance
        is_medical = isinstance(request.user, MedicalCenter)
        logger.info(f"Is medical center: {is_medical}")
        return is_medical

class IsRegularUserOrMedicalCenter(permissions.BasePermission):
    """
    Permission class for regular operations
    """
    def has_permission(self, request, view):
        # First check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Medical centers can do everything
        if isinstance(request.user, MedicalCenter):
            return True

        # For regular users, restrict certain operations
        if isinstance(request.user, RegularUser):
            # Block these specific operations
            if view.action in ['create', 'destroy']:
                if view.basename in ['medical-centers', 'regular-users']:
                    return False
            return True

        return False