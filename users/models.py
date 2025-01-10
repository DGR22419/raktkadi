from django.db import models
from django.contrib.auth.models import BaseUserManager, PermissionsMixin , AbstractBaseUser
from django.core.validators import RegexValidator
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password, check_password

# Validator for phone numbers
phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

# Blood Bank Model
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
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=True)  # Superuser flag
    date_joined = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(default=now)
    modified_date = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  # Email is the unique identifier
    REQUIRED_FIELDS = []  # No need for a username

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Admin"
        verbose_name_plural = "Admins"
############################################################
class BloodBank(models.Model):
    email = models.EmailField(unique=True, primary_key=True)
    name = models.CharField(max_length=255 , blank=False )
    password = models.CharField(max_length=128)
    contact = models.CharField(validators=[phone_regex], max_length=17)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(default=now)
    modified_date = models.DateTimeField(auto_now=True)
    address = models.TextField()
    blood_bank_name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=10,
        choices=[('PENDING', 'Pending'), ('VERIFIED', 'Verified'), ('REJECTED', 'Rejected')],
        default='PENDING'
    )
    # documents = models.FileField(upload_to='blood_bank_documents/', blank=True, null=True)
    # Document fields
    
    license_document = models.FileField(upload_to='blood_bank_documents/licenses/', blank=True, null=True)
    registration_certificate = models.FileField(upload_to='blood_bank_documents/registration_certificates/', blank=True, null=True)
    tax_documents = models.FileField(upload_to='blood_bank_documents/tax_documents/', blank=True, null=True)

    # File upload settings (optional, to limit size or types)
    max_file_size = 5 * 1024 * 1024  # 5 MB
    allowed_types = ['application/pdf', 'image/jpeg', 'image/png']

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  # Specify that email will be used as the login field
    REQUIRED_FIELDS = [] 

    class Meta:
        verbose_name = "Blood Bank"
        verbose_name_plural = "Blood Banks"
    
    def set_password(self, raw_password):
        """Hashes the password and stores it."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Verifies the provided password against the stored hash."""
        return check_password(raw_password, self.password)
    
    def save(self, *args, **kwargs):
        if self.pk is None or not BloodBank.objects.filter(pk=self.pk).exists():
            self.set_password(self.password)
        super(BloodBank, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

# Staff Model
class Staff(models.Model):
# class Staff(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=128)
    contact = models.CharField(validators=[phone_regex], max_length=17)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(default=now)
    modified_date = models.DateTimeField(auto_now=True)
    role = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  # Specify that email will be used as the login field
    REQUIRED_FIELDS = [] 

    class Meta:
        verbose_name = "Staff"
        verbose_name_plural = "Staff"

    def set_password(self, raw_password):
        """Hashes the password and stores it."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Verifies the provided password against the stored hash."""
        return check_password(raw_password, self.password)
    
    def save(self, *args, **kwargs):
        if self.pk is None or not Staff.objects.filter(pk=self.pk).exists():
            self.set_password(self.password)
        super(Staff, self).save(*args, **kwargs)

# Donor Model
class Donor(models.Model):
    email = models.EmailField(unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=128)
    contact = models.CharField(validators=[phone_regex], max_length=17)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(default=now)
    modified_date = models.DateTimeField(auto_now=True)
    blood_group = models.CharField(max_length=5)
    last_donation = models.DateField(null=True, blank=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    address = models.TextField()

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  # Specify that email will be used as the login field
    REQUIRED_FIELDS = [] 

    class Meta:
        verbose_name = "Donor"
        verbose_name_plural = "Donors"

    def set_password(self, raw_password):
        """Hashes the password and stores it."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Verifies the provided password against the stored hash."""
        return check_password(raw_password, self.password)
    
    def save(self, *args, **kwargs):
        if self.pk is None or not Donor.objects.filter(pk=self.pk).exists():
            self.set_password(self.password)
        super(Donor, self).save(*args, **kwargs)

# Consumer Model
class Consumer(models.Model):
    email = models.EmailField(unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=128)
    contact = models.CharField(validators=[phone_regex], max_length=17)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(default=now)
    modified_date = models.DateTimeField(auto_now=True)
    address = models.TextField()
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    blood_group = models.CharField(max_length=5)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  # Specify that email will be used as the login field
    REQUIRED_FIELDS = [] 

    class Meta:
        verbose_name = "Consumer"
        verbose_name_plural = "Consumers"

    def set_password(self, raw_password):
        """Hashes the password and stores it."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Verifies the provided password against the stored hash."""
        return check_password(raw_password, self.password)
