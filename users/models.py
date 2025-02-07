from django.db import models
from django.contrib.auth.models import BaseUserManager, PermissionsMixin, AbstractBaseUser
from django.core.validators import RegexValidator
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password
import os

# Validator for phone numbers
phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class Admin(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    contact = models.CharField(validators=[phone_regex], max_length=17)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(default=now)
    modified_date = models.DateTimeField(auto_now=True)
    user_type = models.CharField(
        max_length=20,
        choices=[
            ('ADMIN', 'Admin'),
            ('BLOOD_BANK', 'Blood Bank'),
            ('STAFF', 'Staff'),
            ('DONOR', 'Donor'),
            ('CONSUMER', 'Consumer')
        ],
        default='ADMIN'
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Admins"

def store_license(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.user.email}.{ext}"
    return os.path.join('blood_bank_documents', 'license' ,  filename)

def store_registration(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.user.email}.{ext}"
    return os.path.join('blood_bank_documents', 'registration_cretificate' ,  filename)

def store_tax(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.user.email}.{ext}"
    return os.path.join('blood_bank_documents', 'tax_documents' ,  filename)

class BloodBankProfile(models.Model):
    user = models.OneToOneField(Admin, on_delete=models.CASCADE, related_name='blood_bank_profile')
    address = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=[('PENDING', 'Pending'), ('VERIFIED', 'Verified'), ('REJECTED', 'Rejected')],
        default='PENDING'
    )
    license_document = models.FileField(upload_to=store_license , blank=True, null=True)
    registration_certificate = models.FileField(upload_to=store_registration, blank=True, null=True)
    tax_documents = models.FileField(upload_to=store_tax, blank=True, null=True)

    # license_document = models.FileField(upload_to=rename_file, blank=True, null=True)
    # registration_certificate = models.FileField(upload_to=rename_file, blank=True, null=True)
    # tax_documents = models.FileField(upload_to=rename_file, blank=True, null=True)

    def __str__(self):
        return f"{self.user.email}"
    
    class Meta:
        verbose_name = "Hospital"
        verbose_name_plural = "hospitals"

class StaffProfile(models.Model):
    user = models.OneToOneField(Admin, on_delete=models.CASCADE, related_name='staff_profile')
    blood_bank = models.ForeignKey(BloodBankProfile, on_delete=models.CASCADE, related_name='staff_members')
    role = models.CharField(max_length=255)
    # first_name = models.CharField(max_length=255)
    # last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.email}"
    
    class Meta:
        verbose_name = "Staff"
        verbose_name_plural = "Staffs"

class DonorProfile(models.Model):
    user = models.OneToOneField(Admin, on_delete=models.CASCADE, related_name='donor_profile')
    blood_group = models.CharField(max_length=5)
    last_donation = models.DateField(null=True, blank=True)
    address = models.TextField()

    def __str__(self):
        return f"{self.user.email}"
    
    class Meta:
        verbose_name = "Donor"
        verbose_name_plural = "Donors"

class ConsumerProfile(models.Model):
    user = models.OneToOneField(Admin, on_delete=models.CASCADE, related_name='consumer_profile')
    blood_group = models.CharField(max_length=5)
    address = models.TextField()

    def __str__(self):
        return f"{self.user.email}"
    
    class Meta:
        verbose_name = "Consumer"
        verbose_name_plural = "Consumers"