from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *
from django.contrib.auth import authenticate

User = get_user_model()

## login serializer ##
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User account is disabled.")
                return user
            raise serializers.ValidationError("Invalid email or password.")
        raise serializers.ValidationError("Must include 'email' and 'password'.")

## Blood Bank Profile serializer ##
class BloodBankProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodBankProfile
        fields = ['address', 'status', 'license_document', 
                 'registration_certificate', 'tax_documents']

class BloodBankRegistrationSerializer(serializers.Serializer):
    # User fields
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    name = serializers.CharField()
    contact = serializers.CharField()
    
    # Blood Bank Profile fields
    # blood_bank_name = serializers.CharField()
    address = serializers.CharField()
    license_document = serializers.FileField(required=False)
    registration_certificate = serializers.FileField(required=False)
    tax_documents = serializers.FileField(required=False)

    def create(self, validated_data):
        # Extract profile data
        profile_data = {
            'address': validated_data.pop('address'),
            'license_document': validated_data.pop('license_document', None),
            'registration_certificate': validated_data.pop('registration_certificate', None),
            'tax_documents': validated_data.pop('tax_documents', None),
        }

        # Create user
        validated_data['user_type'] = 'BLOOD_BANK'
        user = User.objects.create_user(**validated_data)

        # Create blood bank profile
        BloodBankProfile.objects.create(user=user, **profile_data)

        return user

class BloodBankSerializer(serializers.ModelSerializer):
    address = serializers.CharField(source='blood_bank_profile.address')
    status = serializers.CharField(source='blood_bank_profile.status')
    license_document = serializers.FileField(source='blood_bank_profile.license_document', required=False)
    registration_certificate = serializers.FileField(source='blood_bank_profile.registration_certificate', required=False)
    tax_documents = serializers.FileField(source='blood_bank_profile.tax_documents', required=False)

    class Meta:
        model = User
        fields = ['email', 'name', 'contact', 'address', 'status',
                 'license_document', 'registration_certificate', 'tax_documents', 'is_active']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('blood_bank_profile', {})
        
        # Update User model fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update BloodBankProfile fields
        profile = instance.blood_bank_profile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance


## Staff profile serializer ##
class StaffProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffProfile
        fields = ['role', ]

class StaffRegistrationSerializer(serializers.Serializer):
    # User fields
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    name = serializers.CharField()
    contact = serializers.CharField()
    
    # Staff Profile fields
    role = serializers.CharField()

    def create(self, validated_data):
        # Extract profile data
        profile_data = {
            'role': validated_data.pop('role'),
        }

        # Create user
        validated_data['user_type'] = 'STAFF'
        user = User.objects.create_user(**validated_data)

        # Create staff profile
        StaffProfile.objects.create(user=user, **profile_data)

        return user

class StaffSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='staff_profile.role')

    class Meta:
        model = User
        fields = ['email', 'name', 'contact', 'role', 'is_active']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('staff_profile', {})
        
        # Update User model fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update StaffProfile fields
        profile = instance.staff_profile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance
    

## Donor profile serializer ##
class DonorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonorProfile
        fields = ['blood_group', 'last_donation','address']

class DonorRegistrationSerializer(serializers.Serializer):
    # User fields
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    name = serializers.CharField()
    contact = serializers.CharField()
    
    # Donor Profile fields
    blood_group = serializers.CharField()
    last_donation = serializers.DateField(required=False)
    address = serializers.CharField()

    def create(self, validated_data):
        # Extract profile data
        profile_data = {
            'blood_group': validated_data.pop('blood_group'),
            'last_donation': validated_data.pop('last_donation', None),
            'address': validated_data.pop('address'),
        }

        # Create user
        validated_data['user_type'] = 'DONOR'
        user = User.objects.create_user(**validated_data)

        # Create donor profile
        DonorProfile.objects.create(user=user, **profile_data)

        return user

class DonorSerializer(serializers.ModelSerializer):
    blood_group = serializers.CharField(source='donor_profile.blood_group')
    last_donation = serializers.DateField(source='donor_profile.last_donation', required=False)
    address = serializers.CharField(source='donor_profile.address')

    class Meta:
        model = User
        fields = ['email', 'name', 'contact', 'blood_group', 'last_donation','address', 'is_active']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('donor_profile', {})
        
        # Update User model fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update DonorProfile fields
        profile = instance.donor_profile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance
    

## Consumer profile serializer ##
class ConsumerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsumerProfile
        fields = ['blood_group', 'address']

class ConsumerRegistrationSerializer(serializers.Serializer):
    # User fields
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    name = serializers.CharField()
    contact = serializers.CharField()
    
    # Consumer Profile fields
    blood_group = serializers.CharField()
    address = serializers.CharField()

    def create(self, validated_data):
        # Extract profile data
        profile_data = {
            'blood_group': validated_data.pop('blood_group'),
            'address': validated_data.pop('address'),
        }

        # Create user
        validated_data['user_type'] = 'CONSUMER'
        user = User.objects.create_user(**validated_data)

        # Create consumer profile
        ConsumerProfile.objects.create(user=user, **profile_data)

        return user

class ConsumerSerializer(serializers.ModelSerializer):
    blood_group = serializers.CharField(source='consumer_profile.blood_group')
    address = serializers.CharField(source='consumer_profile.address')

    class Meta:
        model = User
        fields = ['email', 'name', 'contact', 'blood_group', 'address', 'is_active']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('consumer_profile', {})
        
        # Update User model fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update ConsumerProfile fields
        profile = instance.consumer_profile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance



