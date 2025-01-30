from rest_framework import serializers
from .models import BloodBag, Admin, BloodBankProfile

class BloodBagSerializer(serializers.ModelSerializer):
    donor_email = serializers.EmailField(
        source='donor.user.email', 
        required=False, 
        allow_null=True
    )
    blood_bank_email = serializers.EmailField(
        source='blood_bank.user.email'
    )

    class Meta:
        model = BloodBag
        fields = [
            'blood_group', 
            'volume_ml', 
            'collection_date', 
            'expiration_date', 
            'barcode',
            'donor_email',
            'blood_bank_email'
        ]
        extra_kwargs = {
            'barcode': {'required': True}
        }

    def validate(self, data):
        """Validate collection and expiration dates"""
        if data['collection_date'] >= data['expiration_date']:
            raise serializers.ValidationError("Expiration date must be after collection date")
        return data

    def create(self, validated_data):
        """Custom create method to handle email-based lookups"""
        # Extract blood bank by email
        blood_bank_email = validated_data.pop('blood_bank', {}).get('user', {}).get('email')
        # blood_bank = BloodBankProfile.objects.get(user__email=blood_bank_email)
        if blood_bank_email:
            from users.models import BloodBankProfile
            blood_bank = BloodBankProfile.objects.get(user__email=blood_bank_email)
        
        # Optional donor handling
        donor = None
        donor_email = validated_data.pop('donor', {}).get('user', {}).get('email')
        if donor_email:
            from users.models import DonorProfile
            donor = DonorProfile.objects.get(user__email=donor_email)
        
        # Create blood bag
        validated_data['blood_bank'] = blood_bank
        validated_data['donor'] = donor
        
        return super().create(validated_data)