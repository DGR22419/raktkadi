from rest_framework import serializers
from .models import BloodBag, Admin, BloodBankProfile , BloodRequest

class BloodBagSerializer(serializers.ModelSerializer):
    donor_email = serializers.EmailField(
        source='donor.user.email', 
        required=True, 
        allow_null=False
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
            'donor_email',
            'blood_bank_email'
        ]
        extra_kwargs = {
            'barcode': {'required': True}
        }

    def validate_blood_bank_email(self, value):
        """
        Validate that blood bank email exists and is verified
        """
        try:
            from users.models import BloodBankProfile
            blood_bank = BloodBankProfile.objects.get(user__email=value)
            
            if blood_bank.status != 'VERIFIED':
                raise serializers.ValidationError(
                    f"Blood bank is not verified. Current status: {blood_bank.status}"
                )
            return value
        except BloodBankProfile.DoesNotExist:
            raise serializers.ValidationError(
                "Blood bank with this email does not exist."
            )

    def validate(self, data):

        unexpected_fields = set(self.initial_data.keys()) - set(self.fields.keys())
        if unexpected_fields:
            raise serializers.ValidationError(
                f"Got unexpected fields: {', '.join(unexpected_fields)}"
            )
        
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
    
class BloodRequestCreateSerializer(serializers.ModelSerializer):
    consumer_email = serializers.EmailField(source='consumer.user.email')
    blood_bank_email = serializers.EmailField(source='blood_bank.user.email')

    class Meta:
        model = BloodRequest
        fields = [
            'consumer_email',
            'blood_bank_email',
            'blood_group',
            'units_required',
            'priority',
            'patient_name',
            'patient_age',
            'patient_gender',
            'hospital_name',
            'required_date',
            'notes'
        ]

    def validate(self, data):
        
        unexpected_fields = set(self.initial_data.keys()) - set(self.fields.keys())
        if unexpected_fields:
            raise serializers.ValidationError(
                f"Got unexpected fields: {', '.join(unexpected_fields)}"
            )
        return data

    def create(self, validated_data):
        # Extract emails and get related objects
        consumer_email = validated_data.pop('consumer').get('user').get('email')
        blood_bank_email = validated_data.pop('blood_bank').get('user').get('email')
        
        from users.models import ConsumerProfile, BloodBankProfile
        consumer = ConsumerProfile.objects.get(user__email=consumer_email)
        blood_bank = BloodBankProfile.objects.get(user__email=blood_bank_email)
        
        # Create blood request
        return BloodRequest.objects.create(
            consumer=consumer,
            blood_bank=blood_bank,
            **validated_data
        )

class BloodRequestResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodRequest
        fields = ['status', 'rejection_reason', 'notes']
        
    def validate(self, data):
        if data.get('status') == 'REJECTED' and not data.get('rejection_reason'):
            raise serializers.ValidationError("Rejection reason is required when rejecting a request")
        return data