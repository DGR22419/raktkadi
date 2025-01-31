from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import BloodBag, StockTransaction
from .serializers import *
from users.permissions import *
from rest_framework.permissions import AllowAny , IsAuthenticated
from django.utils import timezone


class BloodBagCreateAPIView(generics.CreateAPIView):
    """API view to create a new blood bag"""
    serializer_class = BloodBagSerializer
    # permission_classes = [permissions.IsAuthenticated]
    # permission_classes = [ IsBloodBank | IsStaff | IsAdmin ]
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create the blood bag
        blood_bag = serializer.save()
        
        # Create a collection transaction
        StockTransaction.objects.create(
            blood_bag=blood_bag,
            transaction_type='COLLECTION',
            # performer=request.user
        )
        
        # Return response
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED, 
            headers=headers
        )

class BloodRequestCreateView(generics.CreateAPIView):
    serializer_class = BloodRequestCreateSerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [AllowAny]

class BloodRequestResponseView(generics.UpdateAPIView):
    serializer_class = BloodRequestResponseSerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [AllowAny]
    queryset = BloodRequest.objects.all()

    def perform_update(self, serializer):
        instance = serializer.save(response_date=timezone.now())
        
        # If request is approved, update blood bag status
        if instance.status == 'APPROVED':
            # Get available blood bags
            from .models import BloodBag
            available_bags = BloodBag.objects.filter(
                blood_bank=instance.blood_bank,
                blood_group=instance.blood_group,
                status='AVAILABLE'
            )[:instance.units_required]
            
            # Update blood bags status and create transactions
            for bag in available_bags:
                bag.status = 'RESERVED'
                bag.save()
                
                # Create allocation transaction
                from .models import StockTransaction
                StockTransaction.objects.create(
                    blood_bag=bag,
                    transaction_type='ALLOCATION',
                    source_location=instance.blood_bank,
                    destination_location=instance.hospital_name,
                    notes=f"Allocated for request #{instance.id} - Patient: {instance.patient_name}"
                )
                
                # Add to allocated bags
                instance.allocated_blood_bags.add(bag)

class BloodBanksByBloodGroupView(generics.ListAPIView):
    """API to list verified blood banks having specific blood group available"""
    
    def get(self, request, blood_group, *args, **kwargs):
        # Get verified blood banks that have the specified blood group available
        blood_banks = BloodBankProfile.objects.filter(
            status='VERIFIED',
            blood_bags__blood_group=blood_group,
            blood_bags__status='AVAILABLE'
        ).distinct().values(
            'user__name',
            'user__email',
            'user__contact',
            'address',
            'id'  # Adding id for annotate
        )
        
        blood_bank_list = []
        for bank in blood_banks:
            # Count available units for the specific blood group
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
            
        return Response(blood_bank_list)