from django.shortcuts import render, get_object_or_404
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import *
from .permissions import *
from .models import *
import logging
import time
from functools import wraps

logger = logging.getLogger('api_logger')
User = get_user_model()

def log_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Get view class name and method
        view_class = args[0].__class__.__name__
        method_name = func.__name__
        
        logger.info(f"{view_class}.{method_name} took {execution_time:.2f}ms to execute")
        return result
    return wrapper

@log_execution_time
def home_view(request):
    logger.info(f"Home page accessed - IP: {request.META.get('REMOTE_ADDR')}")
    return render(request, 'home.html')

class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @log_execution_time
    def post(self, request):
        logger.info(f"Login attempt - Email: {request.data.get('email')}")
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data

            if user.user_type == 'BLOOD_BANK' and status != 'VERIFIED':
                logger.warning(f"Login attempt by unverified blood bank - Email: {user.email}")
                return Response({
                    "error": "Your blood bank account is pending verification. Please wait for admin approval."
                }, status=status.HTTP_403_FORBIDDEN)

            refresh = RefreshToken.for_user(user)
            user_type = user.user_type
            logger.info(f"Successful login - Email: {user.email}, Type: {user_type}")
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user_type": user_type
            }, status=status.HTTP_200_OK)
        logger.warning(f"Failed login attempt - Errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_200_OK)

class BloodBankView(APIView):
    permission_classes = [AllowAny]

    @log_execution_time
    def get(self, request, email=None):
        logger.info(f"Blood bank fetch - Email: {email if email else 'all'}")
        if email:
            blood_bank = get_object_or_404(User, email=email, user_type='BLOOD_BANK')
            serializer = BloodBankSerializer(blood_bank)
            return Response(serializer.data)
        blood_banks = User.objects.filter(user_type='BLOOD_BANK')
        serializer = BloodBankSerializer(blood_banks, many=True)
        return Response(serializer.data)

    @transaction.atomic
    @log_execution_time
    def post(self, request):
        logger.info("Blood bank registration attempt")
        serializer = BloodBankRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                logger.info(f"Blood bank registered successfully - Email: {user.email}")
                response_serializer = BloodBankSerializer(user)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Blood bank registration failed - Error: {str(e)}")
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        logger.warning(f"Blood bank registration validation failed - Errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    @log_execution_time
    def put(self, request, email):
        logger.info(f"Blood bank update attempt - Email: {email}")
        try:
            blood_bank = get_object_or_404(User, email=email, user_type='BLOOD_BANK')
            serializer = BloodBankSerializer(blood_bank, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Blood bank updated successfully - Email: {email}")
                return Response(serializer.data)
            logger.warning(f"Blood bank update validation failed - Errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            logger.error(f"Blood bank not found - Email: {email}")
            return Response({"error": "Blood bank not found"}, status=status.HTTP_404_NOT_FOUND)
        
    @log_execution_time
    def delete(self, request, email):
        logger.info(f"Blood bank deletion attempt - Email: {email}")
        try:
            blood_bank = get_object_or_404(User, email=email, user_type='BLOOD_BANK')
            blood_bank.delete()
            logger.info(f"Blood bank deleted successfully - Email: {email}")
            return Response({"message": "Blood bank deleted successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            logger.error(f"Blood bank not found for deletion - Email: {email}")
            return Response({"error": "Blood bank not found"}, status=status.HTTP_404_NOT_FOUND)

class VerifiedBloodBankView(APIView):
    permission_classes = [AllowAny]

    @log_execution_time
    def get(self, request):
        logger.info("Fetching verified blood banks")
        verified_blood_banks = User.objects.filter(user_type='BLOOD_BANK', blood_bank_profile__status='VERIFIED')
        serializer = BloodBankSerializer(verified_blood_banks, many=True)
        logger.info(f"Retrieved {len(verified_blood_banks)} verified blood banks")
        return Response(serializer.data, status=status.HTTP_200_OK)

class StaffView(APIView):
    permission_classes = [AllowAny]

    @log_execution_time
    def get(self, request, email=None):
        logger.info(f"Staff fetch - Email: {email if email else 'all'}")
        if email:
            staff = get_object_or_404(User, email=email, user_type='STAFF')
            serializer = StaffSerializer(staff)
            return Response(serializer.data)
        staff_members = User.objects.filter(user_type='STAFF')
        serializer = StaffSerializer(staff_members, many=True)
        return Response(serializer.data)

    @transaction.atomic
    @log_execution_time
    def post(self, request):
        logger.info("Staff registration attempt")
        serializer = StaffRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                logger.info(f"Staff registered successfully - Email: {user.email}")
                response_serializer = StaffSerializer(user)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Staff registration failed - Error: {str(e)}")
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        logger.warning(f"Staff registration validation failed - Errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    @log_execution_time
    def put(self, request, email):
        logger.info(f"Staff update attempt - Email: {email}")
        try:
            staff = get_object_or_404(User, email=email, user_type='STAFF')
            serializer = StaffSerializer(staff, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Staff updated successfully - Email: {email}")
                return Response(serializer.data)
            logger.warning(f"Staff update validation failed - Errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            logger.error(f"Staff not found - Email: {email}")
            return Response({"error": "Staff member not found"}, status=status.HTTP_404_NOT_FOUND)

    @log_execution_time
    def delete(self, request, email):
        logger.info(f"Staff deletion attempt - Email: {email}")
        try:
            staff = get_object_or_404(User, email=email, user_type='STAFF')
            staff.delete()
            logger.info(f"Staff deleted successfully - Email: {email}")
            return Response({"message": "Staff member deleted successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            logger.error(f"Staff not found for deletion - Email: {email}")
            return Response({"error": "Staff member not found"}, status=status.HTTP_404_NOT_FOUND)

class DonorView(APIView):
    permission_classes = [AllowAny]

    @log_execution_time
    def get(self, request, email=None):
        logger.info(f"Donor fetch - Email: {email if email else 'all'}")
        if email:
            donor = get_object_or_404(User, email=email, user_type='DONOR')
            serializer = DonorSerializer(donor)
            return Response(serializer.data)
        donors = User.objects.filter(user_type='DONOR')
        serializer = DonorSerializer(donors, many=True)
        return Response(serializer.data)

    @transaction.atomic
    @log_execution_time
    def post(self, request):
        logger.info("Donor registration attempt")
        serializer = DonorRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                logger.info(f"Donor registered successfully - Email: {user.email}")
                response_serializer = DonorSerializer(user)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Donor registration failed - Error: {str(e)}")
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        logger.warning(f"Donor registration validation failed - Errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    @log_execution_time
    def put(self, request, email):
        logger.info(f"Donor update attempt - Email: {email}")
        try:
            donor = get_object_or_404(User, email=email, user_type='DONOR')
            serializer = DonorSerializer(donor, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Donor updated successfully - Email: {email}")
                return Response(serializer.data)
            logger.warning(f"Donor update validation failed - Errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            logger.error(f"Donor not found - Email: {email}")
            return Response({"error": "Donor not found"}, status=status.HTTP_404_NOT_FOUND)

    @log_execution_time
    def delete(self, request, email):
        logger.info(f"Donor deletion attempt - Email: {email}")
        try:
            donor = get_object_or_404(User, email=email, user_type='DONOR')
            donor.delete()
            logger.info(f"Donor deleted successfully - Email: {email}")
            return Response({"message": "Donor deleted successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            logger.error(f"Donor not found for deletion - Email: {email}")
            return Response({"error": "Donor not found"}, status=status.HTTP_404_NOT_FOUND)

class ConsumerView(APIView):
    permission_classes = [AllowAny]

    @log_execution_time
    def get(self, request, email=None):
        logger.info(f"Consumer fetch - Email: {email if email else 'all'}")
        if email:
            consumer = get_object_or_404(User, email=email, user_type='CONSUMER')
            serializer = ConsumerSerializer(consumer)
            return Response(serializer.data)
        consumers = User.objects.filter(user_type='CONSUMER')
        serializer = ConsumerSerializer(consumers, many=True)
        return Response(serializer.data)

    @transaction.atomic
    @log_execution_time
    def post(self, request):
        logger.info("Consumer registration attempt")
        serializer = ConsumerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                logger.info(f"Consumer registered successfully - Email: {user.email}")
                response_serializer = ConsumerSerializer(user)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Consumer registration failed - Error: {str(e)}")
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        logger.warning(f"Consumer registration validation failed - Errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    @log_execution_time
    def put(self, request, email):
        logger.info(f"Consumer update attempt - Email: {email}")
        try:
            consumer = get_object_or_404(User, email=email, user_type='CONSUMER')
            serializer = ConsumerSerializer(consumer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Consumer updated successfully - Email: {email}")
                return Response(serializer.data)
            logger.warning(f"Consumer update validation failed - Errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            logger.error(f"Consumer not found - Email: {email}")
            return Response({"error": "Consumer not found"}, status=status.HTTP_404_NOT_FOUND)

    @log_execution_time
    def delete(self, request, email):
        logger.info(f"Consumer deletion attempt - Email: {email}")
        try:
            consumer = get_object_or_404(User, email=email, user_type='CONSUMER')
            consumer.delete()
            logger.info(f"Consumer deleted successfully - Email: {email}")
            return Response({"message": "Consumer deleted successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            logger.error(f"Consumer not found for deletion - Email: {email}")
            return Response({"error": "Consumer not found"}, status=status.HTTP_404_NOT_FOUND)

class Test_blood_bank(APIView):
    permission_classes = [IsBloodBank]

    @log_execution_time
    def get(self, request, *args, **kwargs):
        logger.info(f"Test blood bank access - User: {request.user.email}")
        return Response({"message": "Welcome Blood Bank!"})

class Test_staff(APIView):
    permission_classes = [IsStaff]

    @log_execution_time
    def get(self, request, *args, **kwargs):
        logger.info(f"Test staff access - User: {request.user.email}")
        return Response({"message": "Welcome staff!"})

class Test_donor(APIView):
    permission_classes = [IsDonor]

    @log_execution_time
    def get(self, request, *args, **kwargs):
        logger.info(f"Test donor access - User: {request.user.email}")
        return Response({"message": "Welcome donor!"})
    
class Test_consumer(APIView):
    permission_classes = [IsConsumer]
    
    @log_execution_time
    def get(self, request, *args, **kwargs):
        logger.info(f"Test consumer access - User: {request.user.email}")
        return Response({"message": "Welcome consumer!"})