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
