from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Admin, BloodBank, Staff, Donor, Consumer
import logging

logger = logging.getLogger(__name__)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email is None or password is None:
            raise serializers.ValidationError("Must include 'email' and 'password'")

        user = authenticate(request=self.context.get('request'), username=email, password=password)
        if not user:
            logger.warning(f"Failed authentication attempt for: {email}")
            raise serializers.ValidationError("Invalid credentials")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")

        refresh = RefreshToken.for_user(user)

        # Determine user type
        user_type = None
        if isinstance(user, Admin):
            user_type = 'Admin'
        elif isinstance(user, BloodBank):
            user_type = 'BloodBank'
        elif isinstance(user, Staff):
            user_type = 'Staff'
        elif isinstance(user, Donor):
            user_type = 'Donor'
        elif isinstance(user, Consumer):
            user_type = 'Consumer'

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_type': user_type,
        }
    
class BloodBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodBank
        fields = ['email', 'name', 'password', 'contact', 'address', 'blood_bank_name']

    def create(self, validated_data):
        blood_bank = BloodBank(**validated_data)
        blood_bank.set_password(validated_data['password'])  # Hash the password
        blood_bank.save()
        return blood_bank

    def validate_email(self, value):
        if BloodBank.objects.filter(email=value).exists():
            raise serializers.ValidationError("A blood bank with this email already exists.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value
    
class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['email', 'name', 'password', 'contact', 'role', 'first_name', 'last_name']

    def create(self, validated_data):
        staff = Staff(**validated_data)
        staff.set_password(validated_data['password'])  # Hash the password
        staff.save()
        return staff

    def validate_email(self, value):
        if Staff.objects.filter(email=value).exists():
            raise serializers.ValidationError("A staff member with this email already exists.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value
    
## donor serializer ##
class DonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donor
        fields = ['email', 'name', 'password', 'contact', 'address', 'blood_group', 'first_name', 'last_name']

    def create(self, validated_data):
        donor = Donor(**validated_data)
        donor.set_password(validated_data['password'])  # Hash the password
        donor.save()
        return donor

    def validate_email(self, value):
        if Donor.objects.filter(email=value).exists():
            raise serializers.ValidationError("A donor with this email already exists.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value
    
## consumer serializer ##
class ConsumerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consumer
        fields = ['email', 'name', 'password', 'contact', 'address', 'blood_group', 'first_name', 'last_name']

    def create(self, validated_data):
        consumer = Consumer(**validated_data)
        consumer.set_password(validated_data['password'])  # Hash the password
        consumer.save()
        return consumer

    def validate_email(self, value):
        if Consumer.objects.filter(email=value).exists():
            raise serializers.ValidationError("A consumer with this email already exists.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value