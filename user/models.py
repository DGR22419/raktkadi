from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator

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
        return self.create_user(email, password, **extra_fields)

class MedicalCenter(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    contact = models.CharField(validators=[phone_regex], max_length=17)
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'contact']

    def __str__(self):
        return self.name
    
    class Meta:
        permissions = [
            ("can_view_medical_center", "Can view medical center"),
        ]
        verbose_name = "Medical Center"
        verbose_name_plural = "Medical Centers"

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='medical_center_set',
        related_query_name='medical_center'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='medical_center_set',
        related_query_name='medical_center'
    )

class Patient(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    contact = models.CharField(validators=[phone_regex], max_length=17)
    blood_group = models.CharField(max_length=5)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'contact', 'blood_group']

    def __str__(self):
        return self.name
    
    class Meta:
        permissions = [
            ("can_view_patient", "Can view patient"),
        ]
        verbose_name = "Patient"
        verbose_name_plural = "Patients"

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='patient_set',
        related_query_name='patient'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='patient_set',
        related_query_name='patient'
    )

class Donor(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    contact = models.CharField(validators=[phone_regex], max_length=17)
    blood_group = models.CharField(max_length=5)
    last_donation = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'contact', 'blood_group']

    def __str__(self):
        return self.name
    
    class Meta:
        permissions = [
            ("can_view_donor", "Can view donor"),
        ]
        verbose_name = "Donor"
        verbose_name_plural = "Donors"

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='donor_set',
        related_query_name='donor'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='donor_set',
        related_query_name='donor'
    )
    

class BloodRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('FULFILLED', 'Fulfilled'),
        ('CANCELLED', 'Cancelled')
    ]
    
    hospital_name = models.CharField(max_length=255, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='blood_requests')
    blood_group = models.CharField(max_length=5)
    units_required = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    urgency_level = models.CharField(max_length=10, choices=[
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    fulfilled_by = models.ForeignKey(Donor, on_delete=models.SET_NULL, null=True, blank=True, related_name='fulfilled_requests')
    fulfilled_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
    

class RegularUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    contact = models.CharField(validators=[phone_regex], max_length=17)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'contact']

    def __str__(self):
        return self.name
    
    class Meta:
        permissions = [
            ("can_view_basic_info", "Can view basic information"),
        ]
        verbose_name = "Regular User"
        verbose_name_plural = "Regular Users"

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='regular_user_set',
        related_query_name='regular_user'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='regular_user_set',
        related_query_name='regular_user'
    )
    

