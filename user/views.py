from django.shortcuts import render

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Hospital, Patient, Donor
from rest_framework import serializers

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
