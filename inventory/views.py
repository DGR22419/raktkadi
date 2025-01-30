from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import BloodBag, StockTransaction
from .serializers import *
from users.permissions import *
from rest_framework.permissions import AllowAny , IsAuthenticated

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
    
# //dcaserver/MKSY/mksy21/

