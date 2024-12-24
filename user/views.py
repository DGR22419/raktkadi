from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import MedicalCenter, Patient, Donor , BloodRequest, RegularUser
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework import status
from django.utils import timezone
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

# Serializers
class MedicalCenterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = MedicalCenter
        fields = ['id', 'email', 'name', 'contact', 'address', 'date_joined', 'password']
        read_only_fields = ['date_joined']

    def create(self, validated_data):
        password = validated_data.pop('password')
        medical_center = MedicalCenter.objects.create(**validated_data)
        medical_center.set_password(password)
        medical_center.save()
        return medical_center

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        return super().update(instance, validated_data)

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient 
        fields = ['id', 'email', 'name', 'contact', 'blood_group', 'date_joined']

class DonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donor
        fields = ['id', 'email', 'name', 'contact', 'blood_group', 'last_donation', 'date_joined']

class BloodRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodRequest
        fields = ['id', 'hospital_name', 'patient', 'blood_group', 'units_required', 
                 'status', 'urgency_level', 'created_at', 'fulfilled_by', 
                 'fulfilled_at', 'notes']
        read_only_fields = ['status', 'fulfilled_by', 'fulfilled_at']

class RegularUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = RegularUser
        fields = ['id', 'email', 'name', 'contact', 'date_joined', 'password']
        read_only_fields = ['date_joined']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = RegularUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

# ViewSets
class MedicalCenterViewSet(viewsets.ModelViewSet):
    queryset = MedicalCenter.objects.all()
    serializer_class = MedicalCenterSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List all medical centers",
        operation_description="Returns a list of all registered medical centers"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a medical center",
        operation_description="Create a new medical center registration"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List all patients",
        operation_description="Returns a list of all registered patients"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a patient",
        operation_description="Create a new patient registration"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

class DonorViewSet(viewsets.ModelViewSet):
    queryset = Donor.objects.all()
    serializer_class = DonorSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List all donors",
        operation_description="Returns a list of all registered donors"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a donor",
        operation_description="Create a new donor registration"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

class BloodRequestViewSet(viewsets.ModelViewSet):
    queryset = BloodRequest.objects.all()
    serializer_class = BloodRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List all blood requests",
        operation_description="Returns a list of all blood requests"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a blood request",
        operation_description="Create a new blood request"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Fulfill a blood request",
        operation_description="Mark a blood request as fulfilled by a donor"
    )
    @action(detail=True, methods=['post'])
    def fulfill(self, request, pk=None):
        blood_request = self.get_object()
        donor_id = request.data.get('donor_id')
        
        if blood_request.status != 'PENDING':
            return Response(
                {'error': 'This request cannot be fulfilled as it is not pending'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            donor = Donor.objects.get(id=donor_id)
            blood_request.fulfilled_by = donor
            blood_request.status = 'FULFILLED'
            blood_request.fulfilled_at = timezone.now()
            blood_request.save()
            
            return Response(BloodRequestSerializer(blood_request).data)
        except Donor.DoesNotExist:
            return Response(
                {'error': 'Donor not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class RegularUserViewSet(viewsets.ModelViewSet):
    queryset = RegularUser.objects.all()
    serializer_class = RegularUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Log the creation
        logger.info(f"Created new RegularUser: {user.email}")
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, MedicalCenter):
            return RegularUser.objects.all()
        return RegularUser.objects.filter(id=user.id)

    @swagger_auto_schema(
        operation_summary="List regular users",
        operation_description="Returns a list of regular users (filtered based on permissions)"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a regular user",
        operation_description="Create a new regular user account"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        logger.info(f"Attempting authentication with email: {attrs[self.username_field]}")
        
        # First try to authenticate as RegularUser
        try:
            user = RegularUser.objects.get(email=attrs[self.username_field])
            logger.info(f"Found RegularUser with email: {attrs[self.username_field]}")
            
            if user.check_password(attrs['password']):
                logger.info("Password check successful for RegularUser")
                if not user.is_active:
                    logger.info("RegularUser account is not active")
                    raise serializers.ValidationError("User account is not active")
                self.user = user
                logger.info("RegularUser authentication successful")
                return super().validate(attrs)
            else:
                logger.info("Password check failed for RegularUser")
        except RegularUser.DoesNotExist:
            logger.info(f"No RegularUser found with email: {attrs[self.username_field]}")

        # If RegularUser authentication fails, try MedicalCenter
        try:
            user = MedicalCenter.objects.get(email=attrs[self.username_field])
            logger.info(f"Found MedicalCenter with email: {attrs[self.username_field]}")
            
            if user.check_password(attrs['password']):
                logger.info("Password check successful for MedicalCenter")
                if not user.is_active:
                    logger.info("MedicalCenter account is not active")
                    raise serializers.ValidationError("User account is not active")
                self.user = user
                logger.info("MedicalCenter authentication successful")
                return super().validate(attrs)
            else:
                logger.info("Password check failed for MedicalCenter")
        except MedicalCenter.DoesNotExist:
            logger.info(f"No MedicalCenter found with email: {attrs[self.username_field]}")

        logger.info("Authentication failed for both RegularUser and MedicalCenter")
        raise serializers.ValidationError(
            'No active account found with the given credentials'
        )

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
