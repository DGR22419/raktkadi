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
from django.shortcuts import render


User = get_user_model()

## home page ##

def home_view(request):
    return render(request, 'home.html')

## login view ##
class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)

            user_type = user.user_type
            
            # Get user type specific data
            # user_data = {
            #     # "id": user.email,
            #     "email": user.email,
            #     "name": user.name,
            #     "user_type": user.user_type,
            # }

            # # Add profile specific data based on user type
            # if user.user_type == 'BLOOD_BANK':
            #     profile = user.blood_bank_profile
            #     user_data.update({
            #         "blood_bank_name": profile.blood_bank_name,
            #         "status": profile.status,
            #         "address": profile.address
            #     })
            # elif user.user_type == 'STAFF':
            #     profile = user.staff_profile
            #     user_data.update({
            #         "role": profile.role,
            #         "first_name": profile.first_name,
            #         "last_name": profile.last_name
            #     })
            # Add similar blocks for other user types if needed

            # return Response({
            #     "message": "Login successful",
            #     "tokens": {
            #         "refresh": str(refresh),
            #         "access": str(refresh.access_token),
            #     },
            #     "user": user_data
            # }, status=status.HTTP_200_OK)
            return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user_type": user_type
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_200_OK)


## main blood bank view ##
class BloodBankView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, email=None):
        if email:
            # Get specific blood bank
            blood_bank = get_object_or_404(User, email=email, user_type='BLOOD_BANK')
            serializer = BloodBankSerializer(blood_bank)
            return Response(serializer.data)
        else:
            blood_banks = User.objects.filter(user_type='BLOOD_BANK')
            serializer = BloodBankSerializer(blood_banks, many=True)
            return Response(serializer.data)

    @transaction.atomic
    def post(self, request):
        # Anyone can register a new blood bank
        serializer = BloodBankRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                response_serializer = BloodBankSerializer(user)
                return Response(
                    response_serializer.data, 
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {"error": str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def put(self, request, email):
        try:
            blood_bank = get_object_or_404(User, email=email, user_type='BLOOD_BANK')
            
            serializer = BloodBankSerializer(
                blood_bank, 
                data=request.data, 
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Blood bank not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, email):
        try:
            # Fetch the user with the specified email and user_type
            blood_bank = get_object_or_404(User, email=email, user_type='BLOOD_BANK')
            
            # Check if the request is made by the owner of the account
            # if request.user.email != email:
            #     return Response(
            #         {"error": "Permission denied"},
            #         status=status.HTTP_403_FORBIDDEN
            #     )
            
            # Perform a hard delete
            blood_bank.delete()
            
            return Response(
                {"message": "Blood bank deleted successfully"},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Blood bank not found"},
                status=status.HTTP_404_NOT_FOUND
            )

class VerifiedBloodBankView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        verified_blood_banks = User.objects.filter(user_type='BLOOD_BANK', blood_bank_profile__status='VERIFIED')
        serializer = BloodBankSerializer(verified_blood_banks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

## Staff views ## 
class StaffView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, email=None):
        if email:
            # Get specific staff member
            staff = get_object_or_404(User, email=email, user_type='STAFF')
            serializer = StaffSerializer(staff)
            return Response(serializer.data)
        else:
            # List all staff members
            staff_members = User.objects.filter(user_type='STAFF')
            serializer = StaffSerializer(staff_members, many=True)
            return Response(serializer.data)

    @transaction.atomic
    def post(self, request):
        # Anyone can register a new staff member
        serializer = StaffRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                response_serializer = StaffSerializer(user)
                return Response(
                    response_serializer.data, 
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {"error": str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def put(self, request, email):
        try:
            staff = get_object_or_404(User, email=email, user_type='STAFF')
            
            serializer = StaffSerializer(
                staff, 
                data=request.data, 
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Staff member not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, email):
        try:
            # Fetch the user with the specified email and user_type
            staff = get_object_or_404(User, email=email, user_type='STAFF')
            
            # Perform a hard delete
            staff.delete()
            
            return Response(
                {"message": "Staff member deleted successfully"},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Staff member not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
## Donor views ## 
class DonorView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, email=None):
        if email:
            # Get specific donor
            donor = get_object_or_404(User, email=email, user_type='DONOR')
            serializer = DonorSerializer(donor)
            return Response(serializer.data)
        else:
            # List all donors
            donors = User.objects.filter(user_type='DONOR')
            serializer = DonorSerializer(donors, many=True)
            return Response(serializer.data)

    @transaction.atomic
    def post(self, request):
        # Anyone can register a new donor
        serializer = DonorRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                response_serializer = DonorSerializer(user)
                return Response(
                    response_serializer.data, 
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {"error": str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def put(self, request, email):
        try:
            donor = get_object_or_404(User, email=email, user_type='DONOR')
            
            serializer = DonorSerializer(
                donor, 
                data=request.data, 
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Donor not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, email):
        try:
            # Fetch the user with the specified email and user_type
            donor = get_object_or_404(User, email=email, user_type='DONOR')
            
            # Perform a hard delete
            donor.delete()
            
            return Response(
                {"message": "Donor deleted successfully"},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Donor not found"},
                status=status.HTTP_404_NOT_FOUND
            )

## Consumer views ##
class ConsumerView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, email=None):
        if email:
            # Get specific consumer
            consumer = get_object_or_404(User, email=email, user_type='CONSUMER')
            serializer = ConsumerSerializer(consumer)
            return Response(serializer.data)
        else:
            # List all consumers
            consumers = User.objects.filter(user_type='CONSUMER')
            serializer = ConsumerSerializer(consumers, many=True)
            return Response(serializer.data)

    @transaction.atomic
    def post(self, request):
        # Anyone can register a new consumer
        serializer = ConsumerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                response_serializer = ConsumerSerializer(user)
                return Response(
                    response_serializer.data, 
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {"error": str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def put(self, request, email):
        try:
            consumer = get_object_or_404(User, email=email, user_type='CONSUMER')
            
            serializer = ConsumerSerializer(
                consumer, 
                data=request.data, 
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Consumer not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, email):
        try:
            # Fetch the user with the specified email and user_type
            consumer = get_object_or_404(User, email=email, user_type='CONSUMER')
            
            # Perform a hard delete
            consumer.delete()
            
            return Response(
                {"message": "Consumer deleted successfully"},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Consumer not found"},
                status=status.HTTP_404_NOT_FOUND
            )


## Test view ##   
class Test_blood_bank(APIView):
    permission_classes = [IsBloodBank]

    def get(self, request, *args, **kwargs):
        return Response({"message": "Welcome Blood Bank!"})

class Test_staff(APIView):
    permission_classes = [IsStaff]

    def get(self, request, *args, **kwargs):
        return Response({"message": "Welcome staff!"})

class Test_donor(APIView):
    permission_classes = [IsDonor]

    def get(self, request, *args, **kwargs):
        return Response({"message": "Welcome donor!"})
    
class Test_consumer(APIView):
    permission_classes = [IsConsumer]

    def get(self, request, *args, **kwargs):
        return Response({"message": "Welcome consumer!"})


## End ##