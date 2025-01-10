from django.contrib.auth.backends import ModelBackend
from .models import Admin, BloodBank, Staff, Donor, Consumer
import logging

logger = logging.getLogger(__name__)

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = username
        if email is None:
            email = kwargs.get('email')
        if email is None or password is None:
            return None
        
        # Try authenticating as Admin
        try:
            user = Admin.objects.get(email=email)
            if user.check_password(password):
                logger.info(f"Authenticated admin: {email}")
                return user
        except Admin.DoesNotExist:
            pass

        # Try authenticating as BloodBank
        try:
            user = BloodBank.objects.get(email=email)
            if user.check_password(password):
                logger.info(f"Authenticated blood bank: {email}")
                return user
        except BloodBank.DoesNotExist:
            pass

        # Try authenticating as Staff
        try:
            user = Staff.objects.get(email=email)
            if user.check_password(password):
                logger.info(f"Authenticated staff: {email}")
                return user
        except Staff.DoesNotExist:
            pass

        # Try authenticating as Donor
        try:
            user = Donor.objects.get(email=email)
            if user.check_password(password):
                logger.info(f"Authenticated donor: {email}")
                return user
        except Donor.DoesNotExist:
            pass

        # Try authenticating as Consumer
        try:
            user = Consumer.objects.get(email=email)
            if user.check_password(password):
                logger.info(f"Authenticated consumer: {email}")
                return user
        except Consumer.DoesNotExist:
            pass

        logger.warning(f"Failed authentication attempt for: {email}")
        return None

    def get_user(self, user_id):
        try:
            return Admin.objects.get(pk=user_id)
        except Admin.DoesNotExist:
            pass

        try:
            return BloodBank.objects.get(pk=user_id)
        except BloodBank.DoesNotExist:
            pass

        try:
            return Staff.objects.get(pk=user_id)
        except Staff.DoesNotExist:
            pass

        try:
            return Donor.objects.get(pk=user_id)
        except Donor.DoesNotExist:
            pass

        try:
            return Consumer.objects.get(pk=user_id)
        except Consumer.DoesNotExist:
            return None
