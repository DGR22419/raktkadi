from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from rest_framework.permissions import AllowAny , IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets

# class LoginView(APIView):
#     permission_classes = [AllowAny]
#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         return Response(serializer.validated_data, status=status.HTTP_200_OK)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        # Validate the input data
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_200_OK
            )
        
        # If valid, return the validated data
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class BloodBankView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, email=None):
        if email:
            try:
                blood_bank = BloodBank.objects.get(email=email)
                serializer = BloodBankSerializer(blood_bank)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except BloodBank.DoesNotExist:
                return Response({"error": "BloodBank not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            blood_banks = BloodBank.objects.all()
            serializer = BloodBankSerializer(blood_banks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = BloodBankSerializer(data=request.data)  # Use the new serializer for blood bank registration
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, email):
        try:
            blood_bank = BloodBank.objects.get(email=email)
        except BloodBank.DoesNotExist:
            return Response({"error": "BloodBank not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        if 'email' in data and data['email'] == blood_bank.email:
            data.pop('email')

        serializer = BloodBankSerializer(blood_bank, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, email):
        try:
            blood_bank = BloodBank.objects.get(email=email)
        except BloodBank.DoesNotExist:
            return Response({"error": "BloodBank not found"}, status=status.HTTP_404_NOT_FOUND)

        blood_bank.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

## staff views ## 
class StaffView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, email=None):
        if email:
            try:
                staff = Staff.objects.get(email=email)
                serializer = StaffSerializer(staff)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Staff.DoesNotExist:
                return Response({"error": "Staff not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            staff_members = Staff.objects.all()
            serializer = StaffSerializer(staff_members, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = StaffSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, email):
        try:
            staff = Staff.objects.get(email=email)
        except Staff.DoesNotExist:
            return Response({"error": "Staff not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        if 'email' in data and data['email'] == staff.email:
            data.pop('email')

        serializer = StaffSerializer(staff, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, email):
        try:
            staff = Staff.objects.get(email=email)
        except Staff.DoesNotExist:
            return Response({"error": "Staff not found"}, status=status.HTTP_404_NOT_FOUND)

        staff.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

## Donor views ##
class DonorView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, email=None):
        if email:
            try:
                donor = Donor.objects.get(email=email)
                serializer = DonorSerializer(donor)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Donor.DoesNotExist:
                return Response({"error": "Donor not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            donors = Donor.objects.all()
            serializer = DonorSerializer(donors, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = DonorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, email):
        try:
            donor = Donor.objects.get(email=email)
        except Donor.DoesNotExist:
            return Response({"error": "Donor not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        if 'email' in data and data['email'] == donor.email:
            data.pop('email')

        serializer = DonorSerializer(donor, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, email):
        try:
            donor = Donor.objects.get(email=email)
        except Donor.DoesNotExist:
            return Response({"error": "Donor not found"}, status=status.HTTP_404_NOT_FOUND)

        donor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
## consumer views ##
class ConsumerView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, email=None):
        if email:
            try:
                consumer = Consumer.objects.get(email=email)
                serializer = ConsumerSerializer(consumer)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Consumer.DoesNotExist:
                return Response({"error": "Consumer not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            consumers = Consumer.objects.all()
            serializer = ConsumerSerializer(consumers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ConsumerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, email):
        try:
            consumer = Consumer.objects.get(email=email)
        except Consumer.DoesNotExist:
            return Response({"error": "Consumer not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        if 'email' in data and data['email'] == consumer.email:
            data.pop('email')

        serializer = ConsumerSerializer(consumer, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, email):
        try:
            consumer = Consumer.objects.get(email=email)
        except Consumer.DoesNotExist:
            return Response({"error": "Consumer not found"}, status=status.HTTP_404_NOT_FOUND)

        consumer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)