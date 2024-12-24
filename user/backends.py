from django.contrib.auth.backends import ModelBackend
from .models import MedicalCenter, RegularUser
import logging

logger = logging.getLogger(__name__)

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = username
        if email is None:
            email = kwargs.get('email')
        if email is None or password is None:
            return None
        
        # Try authenticating as MedicalCenter
        try:
            user = MedicalCenter.objects.get(email=email)
            if user.check_password(password):
                logger.info(f"Authenticated medical center: {email}")
                return user
        except MedicalCenter.DoesNotExist:
            pass

        # Try authenticating as RegularUser
        try:
            user = RegularUser.objects.get(email=email)
            if user.check_password(password):
                logger.info(f"Authenticated regular user: {email}")
                return user
        except RegularUser.DoesNotExist:
            pass

        logger.warning(f"Failed authentication attempt for: {email}")
        return None

    def get_user(self, user_id):
        try:
            return MedicalCenter.objects.get(pk=user_id)
        except MedicalCenter.DoesNotExist:
            try:
                return RegularUser.objects.get(pk=user_id)
            except RegularUser.DoesNotExist:
                return None 