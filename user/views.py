from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Hospital, Patient, Donor , BloodRequest
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework import status
from django.utils import timezone

# Serializers
class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = ['id', 'email', 'name', 'contact', 'address', 'date_joined']

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


# ViewSets
class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List all hospitals",
        operation_description="Returns a list of all registered hospitals"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a hospital",
        operation_description="Create a new hospital registration"
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
