from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import BloodBag, StockTransaction
from .serializers import *
from users.permissions import *
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
import logging
import time
from functools import wraps

logger = logging.getLogger('api_logger')

def log_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        view_class = args[0].__class__.__name__
        method_name = func.__name__
        logger.info(f"{view_class}.{method_name} took {execution_time:.2f}ms to execute")
        return result
    return wrapper

class BloodBagCreateAPIView(generics.CreateAPIView):
    serializer_class = BloodBagSerializer
    permission_classes = [AllowAny]

    @log_execution_time
    def create(self, request, *args, **kwargs):
        logger.info(f"Blood bag creation attempt - Data: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Blood bag creation validation failed - Errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create the blood bag
            blood_bag = serializer.save()
            logger.info(f"Blood bag created successfully - ID: {blood_bag.id}")
            
            # Create a collection transaction
            transaction = StockTransaction.objects.create(
                blood_bag=blood_bag,
                transaction_type='COLLECTION',
            )
            logger.info(f"Stock transaction created - ID: {transaction.id}, Type: COLLECTION")
            
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except Exception as e:
            logger.error(f"Blood bag creation failed - Error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class BloodRequestCreateView(generics.CreateAPIView):
    serializer_class = BloodRequestCreateSerializer
    permission_classes = [AllowAny]

    @log_execution_time
    def create(self, request, *args, **kwargs):
        logger.info(f"Blood request creation attempt - Data: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Blood request creation validation failed - Errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            blood_request = serializer.save()
            logger.info(f"Blood request created successfully - ID: {blood_request.id}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Blood request creation failed - Error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class BloodRequestResponseView(generics.UpdateAPIView):
    serializer_class = BloodRequestResponseSerializer
    permission_classes = [AllowAny]
    queryset = BloodRequest.objects.all()

    @log_execution_time
    def perform_update(self, serializer):
        logger.info(f"Blood request response update attempt - Request ID: {serializer.instance.id}")
        
        try:
            instance = serializer.save(response_date=timezone.now())
            logger.info(f"Blood request updated - ID: {instance.id}, Status: {instance.status}")
            
            if instance.status == 'APPROVED':
                available_bags = BloodBag.objects.filter(
                    blood_bank=instance.blood_bank,
                    blood_group=instance.blood_group,
                    status='AVAILABLE'
                )[:instance.units_required]
                
                logger.info(f"Found {len(available_bags)} available blood bags for request {instance.id}")
                
                for bag in available_bags:
                    bag.status = 'RESERVED'
                    bag.save()
                    
                    transaction = StockTransaction.objects.create(
                        blood_bag=bag,
                        transaction_type='ALLOCATION',
                        source_location=instance.blood_bank,
                        destination_location=instance.hospital_name,
                        notes=f"Allocated for request #{instance.id} - Patient: {instance.patient_name}"
                    )
                    
                    instance.allocated_blood_bags.add(bag)
                    logger.info(f"Blood bag {bag.id} allocated and transaction {transaction.id} created")
                
                logger.info(f"Blood request {instance.id} fully processed with {len(available_bags)} allocations")
        except Exception as e:
            logger.error(f"Blood request response update failed - Error: {str(e)}")
            raise

class BloodBanksByBloodGroupView(generics.ListAPIView):
    
    @log_execution_time
    def get(self, request, blood_group, *args, **kwargs):
        logger.info(f"Fetching blood banks for blood group: {blood_group}")
        
        try:
            blood_banks = BloodBankProfile.objects.filter(
                status='VERIFIED',
                blood_bags__blood_group=blood_group,
                blood_bags__status='AVAILABLE'
            ).distinct().values(
                'user__name',
                'user__email',
                'user__contact',
                'address',
                'id'
            )
            
            logger.info(f"Found {len(blood_banks)} blood banks with {blood_group} blood group available")
            
            blood_bank_list = []
            for bank in blood_banks:
                available_units = BloodBag.objects.filter(
                    blood_bank_id=bank['id'],
                    blood_group=blood_group,
                    status='AVAILABLE'
                ).count()
                
                bank_details = {
                    "name": bank['user__name'],
                    "email": bank['user__email'],
                    "contact": bank['user__contact'],
                    "address": bank['address'],
                    "units": available_units
                }
                blood_bank_list.append(bank_details)
                logger.debug(f"Blood bank {bank['user__name']} has {available_units} units of {blood_group}")
            
            logger.info(f"Successfully retrieved details for {len(blood_bank_list)} blood banks")
            return Response(blood_bank_list)
            
        except Exception as e:
            logger.error(f"Error fetching blood banks by blood group - Error: {str(e)}")
            return Response(
                {"error": "Failed to fetch blood banks"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class BloodInventoryView(generics.ListAPIView):
    serializer_class = BloodBagCountSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        blood_group = self.kwargs.get('blood_group')
        if blood_group not in dict(BloodBag.BLOOD_GROUPS):
            return []
            
        count = BloodBag.objects.filter(
            status='AVAILABLE',
            blood_group=blood_group
        ).count()
        
        return [{'units': count}]
    
    def list(self, request, *args, **kwargs):
        blood_group = self.kwargs.get('blood_group')
        if blood_group not in dict(BloodBag.BLOOD_GROUPS):
            return Response(
                {"error": f"Invalid blood group. Valid options are: {', '.join(dict(BloodBag.BLOOD_GROUPS).keys())}"},
                status=400
            )
        
        return super().list(request, *args, **kwargs)

class TotalBagsView(generics.ListAPIView):
    serializer_class = TotalBagsSerializer
    
    def get_queryset(self):
        total = BloodBag.objects.filter(status='AVAILABLE').count()
        return [{'total_bags': total}]

## end ##