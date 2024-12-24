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
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
import logging
from .permissions import IsMedicalCenter, IsRegularUserOrMedicalCenter
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied, AuthenticationFailed

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
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = RegularUser
        fields = ['id', 'email', 'name', 'contact', 'date_joined', 'password']
        read_only_fields = ['date_joined']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = RegularUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        return super().update(instance, validated_data)

# ViewSets
class MedicalCenterViewSet(viewsets.ModelViewSet):
    queryset = MedicalCenter.objects.all()
    serializer_class = MedicalCenterSerializer
    
    def get_permissions(self):
        logger.info(f"Action being performed: {self.action}")
        if self.action == 'create':
            # Block authenticated users from creating medical centers
            if self.request.user and self.request.user.is_authenticated:
                logger.info("Authenticated user attempting to create medical center")
                return [permissions.IsAdminUser()]
            logger.info("Allowing unauthenticated medical center creation")
            return [permissions.AllowAny()]
        logger.info("Requiring medical center permission")
        return [IsMedicalCenter()]

    def handle_exception(self, exc):
        if isinstance(exc, (PermissionDenied, DRFPermissionDenied)):
            return Response(
                {"detail": "You don't have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        if isinstance(exc, AuthenticationFailed):
            return Response(
                {"detail": "You don't have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().handle_exception(exc)

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
    permission_classes = [IsRegularUserOrMedicalCenter]

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
    permission_classes = [IsRegularUserOrMedicalCenter]

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
    permission_classes = [IsRegularUserOrMedicalCenter]

    def get_queryset(self):
        # Handle swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return BloodRequest.objects.none()

        user = self.request.user
        logger.info(f"BloodRequest queryset for user type: {type(user)}")
        
        if isinstance(user, MedicalCenter):
            # Medical centers can see all requests
            return BloodRequest.objects.all()
        
        # Regular users can only see requests where they are the patient
        if isinstance(user, RegularUser):
            return BloodRequest.objects.filter(patient=user)
            
        return BloodRequest.objects.none()

    def perform_create(self, serializer):
        if isinstance(self.request.user, RegularUser):
            # If regular user is creating, they can only create for themselves
            serializer.save(patient=self.request.user)
        else:
            # Medical centers can create for any patient
            serializer.save()

    @swagger_auto_schema(
        operation_summary="List blood requests",
        operation_description="Returns blood requests based on user permissions"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create blood request",
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

    def get_permissions(self):
        logger.info(f"Regular user action being performed: {self.action}")
        if self.action in ['create', 'destroy']:
            # Only medical centers can create/delete users
            return [IsMedicalCenter()]
        return [IsRegularUserOrMedicalCenter()]

    def handle_exception(self, exc):
        if isinstance(exc, (PermissionDenied, DRFPermissionDenied)):
            return Response(
                {"detail": "You don't have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        if isinstance(exc, AuthenticationFailed):
            return Response(
                {"detail": "You don't have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().handle_exception(exc)

    def get_queryset(self):
        user = self.request.user
        logger.info(f"User type in queryset: {type(user)}")
        
        if isinstance(user, MedicalCenter):
            logger.info("Medical center accessing user list")
            return RegularUser.objects.all()
        
        logger.info("Regular user accessing user list")
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
        # Add extra validation for user creation
        if not isinstance(request.user, MedicalCenter):
            return Response(
                {"detail": "Only medical centers can create users"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Handle password update if it's included
        if 'password' in serializer.validated_data:
            password = serializer.validated_data.pop('password')
            instance.set_password(password)
        
        # Update other fields
        for attr, value in serializer.validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return Response(serializer.data)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        # Log the authentication attempt
        logger.info(f"Attempting authentication for email: {email}")

        # Try to authenticate as MedicalCenter first
        user = authenticate(self.context['request'], username=email, password=password)
        
        if not user:
            # If not a medical center, try RegularUser
            try:
                regular_user = RegularUser.objects.get(email=email)
                if regular_user.check_password(password):
                    user = regular_user
                    logger.info(f"Authenticated as RegularUser: {email}")
            except ObjectDoesNotExist:
                logger.warning(f"No user found for email: {email}")
                raise serializers.ValidationError(
                    {"detail": "No active account found with the given credentials"}
                )

        if not user:
            logger.warning(f"Invalid password for email: {email}")
            raise serializers.ValidationError(
                {"detail": "No active account found with the given credentials"}
            )

        if not user.is_active:
            logger.warning(f"Inactive user attempt: {email}")
            raise serializers.ValidationError(
                {"detail": "User account is disabled"}
            )

        # Set the user on the serializer instance
        self.user = user

        # Get the token for the user
        refresh = self.get_token(user)
        
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'email': user.email,
            'name': user.name,
        }

        # Add user type information to response
        if isinstance(user, MedicalCenter):
            data['user_type'] = 'medical_center'
            data['is_medical_center'] = True
        else:
            data['user_type'] = 'regular_user'
            data['is_medical_center'] = False
        
        logger.info(f"Successfully generated token for {email}")
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        if isinstance(user, MedicalCenter):
            token['user_type'] = 'medical_center'
            token['is_medical_center'] = True
        else:
            token['user_type'] = 'regular_user'
            token['is_medical_center'] = False
            
        token['email'] = user.email
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            return Response(
                {"detail": str(e.detail[0]) if isinstance(e.detail, list) else e.detail},
                status=status.HTTP_401_UNAUTHORIZED
            )
