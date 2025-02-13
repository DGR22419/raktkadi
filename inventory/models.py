from django.db import models
from django.utils.timezone import now
from users.models import Admin, BloodBankProfile, DonorProfile , ConsumerProfile
import uuid 


class BloodBag(models.Model):   
    BLOOD_GROUPS = [
        ('A+', 'A +ve'),
        ('A-', 'A -ve'),
        ('B+', 'B +ve'),
        ('B-', 'B -ve'),
        ('AB+', 'AB +ve'),
        ('AB-', 'AB -ve'),
        ('O+', 'O +ve'),
        ('O-', 'O -ve')
    ]

    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('RESERVED', 'Reserved'),
        ('USED', 'Used'),
        ('EXPIRED', 'Expired')
    ]

    blood_bank = models.ForeignKey(BloodBankProfile, on_delete=models.CASCADE, related_name='blood_bags')
    donor = models.ForeignKey(DonorProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='donated_bags')
    
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS)
    volume_ml = models.DecimalField(max_digits=5, decimal_places=2)  # in milliliters
    
    collection_date = models.DateField()
    expiration_date = models.DateField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    
    barcode = models.CharField(max_length=50, unique=True, editable=False)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_barcode(self):
        """
        Generates a unique barcode with the format:
        BB-{blood_bank_id}-{blood_group}-{collection_date}-{unique_id}
        Example: BB-001-AP-20250206-7A3F
        """
        # Format blood bank ID with leading zeros
        bank_id = str(self.blood_bank.id).zfill(3)
        
        # Format blood group (remove + or - for shorter code)
        blood_group_code = self.blood_group.replace('+', 'P').replace('-', 'N')
        
        # Format collection date
        date_str = self.collection_date.strftime('%Y%m%d')
        
        # Generate a short unique identifier
        unique_id = str(uuid.uuid4())[:4].upper()
        
        # Combine all parts
        return f"BB-{bank_id}-{blood_group_code}-{date_str}-{unique_id}"

    def save(self, *args, **kwargs):
        # Generate barcode if it doesn't exist
        if not self.barcode:
            self.barcode = self.generate_barcode()
            
            # Ensure uniqueness
            while BloodBag.objects.filter(barcode=self.barcode).exists():
                self.barcode = self.generate_barcode()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.blood_group} Blood Bag - {self.barcode}"

class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('COLLECTION', 'Blood Collection'),
        ('ALLOCATION', 'Blood Allocation'),
        ('TRANSFER', 'Blood Transfer'),
        ('DISPOSAL', 'Blood Disposal')
    ]

    blood_bag = models.ForeignKey(BloodBag, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    
    # performer = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True)
    
    timestamp = models.DateTimeField(default=now)
    
    source_location = models.CharField(max_length=255, blank=True, null=True)
    destination_location = models.CharField(max_length=255, blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.blood_bag} - {self.timestamp}"

class InventoryAlert(models.Model):
    ALERT_TYPES = [
        ('LOW_STOCK', 'Low Blood Stock'),
        ('NEAR_EXPIRY', 'Near Expiry'),
        ('CRITICAL_SHORTAGE', 'Critical Shortage')
    ]

    blood_bank = models.ForeignKey(BloodBankProfile, on_delete=models.CASCADE, related_name='inventory_alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    
    blood_group = models.CharField(max_length=5, choices=BloodBag.BLOOD_GROUPS)
    
    description = models.TextField()
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.alert_type} - {self.blood_group}"
    
class BloodRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed')
    ]

    PRIORITY_CHOICES = [
        ('NORMAL', 'Normal'),
        ('URGENT', 'Urgent'),
        ('EMERGENCY', 'Emergency')
    ]

    BLOOD_GROUPS = [
        ('A+', 'A +ve'),
        ('A-', 'A -ve'),
        ('B+', 'B +ve'),
        ('B-', 'B -ve'),
        ('AB+', 'AB +ve'),
        ('AB-', 'AB -ve'),
        ('O+', 'O +ve'),
        ('O-', 'O -ve')
    ]
    consumer = models.ForeignKey(ConsumerProfile, on_delete=models.CASCADE, related_name='blood_requests')
    blood_bank = models.ForeignKey(BloodBankProfile, on_delete=models.CASCADE, related_name='received_requests')
    # Request Details
    # blood_group = models.CharField(max_length=5)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS)
    units_required = models.PositiveIntegerField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='NORMAL')
    
    # Patient Details
    patient_name = models.CharField(max_length=255)
    patient_age = models.PositiveIntegerField()
    patient_gender = models.CharField(max_length=10)
    # diagnosis = models.TextField()
    hospital_name = models.CharField(max_length=255)
    
    # Status tracking
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    requested_date = models.DateTimeField(auto_now_add=True)
    required_date = models.DateField()
    response_date = models.DateTimeField(null=True, blank=True)
    
    # If request is approved, which blood bags were allocated
    allocated_blood_bags = models.ManyToManyField(BloodBag, blank=True)
    
    # Additional Info
    notes = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Request {self.id} - {self.blood_group} for {self.patient_name}"
    
## end ##