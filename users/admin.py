from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Admin, BloodBank, Staff, Donor, Consumer

# Admin User Admin Configuration
class AdminUserAdmin(UserAdmin):
    model = Admin
    list_display = ('email', 'name', 'contact', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'created_date', 'modified_date')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'name', 'contact')
    ordering = ('-date_joined',)

    # fieldsets = (
    #     (None, {'fields': ('email', 'password')}),
    #     (_('Personal info'), {'fields': ('name', 'contact')}),
    #     (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    #     (_('Important dates'), {'fields': ('date_joined', 'created_date', 'modified_date')}),
    # )

    # add_fieldsets = (
    #     (None, {'classes': ('wide',), 'fields': ('email', 'password1', 'password2', 'name', 'contact', 'is_active', 'is_staff', 'is_superuser')}),
    # )

    # def get_fieldsets(self, request, obj=None):
    #     if not obj:  # User creation
    #         return self.add_fieldsets
    #     return super().get_fieldsets(request, obj)

# Register Admin model in the admin panel
admin.site.register(Admin, AdminUserAdmin)

# Blood Bank Admin Configuration
from django.contrib import admin
from .models import BloodBank

class BloodBankAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'contact', 'is_active', 'is_staff', 'blood_bank_name', 'status', 'date_joined', 'created_date', 'modified_date')
    list_filter = ('is_active', 'status')
    search_fields = ('email', 'name', 'contact', 'blood_bank_name')
    ordering = ('-date_joined',)

    # fieldsets = (
    #     (None, {'fields': ('email', 'password')}),
    #     (_('Blood Bank Info'), {'fields': ('name', 'contact', 'blood_bank_name', 'address', 'status', 'license_document', 'registration_certificate', 'tax_documents')}),
    #     (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    #     (_('Important dates'), {'fields': ('date_joined', 'created_date', 'modified_date')}),
    # )

    # Ensure that the documents are displayed and can be interacted with in the admin form
    # def get_fieldsets(self, request, obj=None):
    #     if not obj:  # User creation
    #         return self.add_fieldsets
    #     return super().get_fieldsets(request, obj)

# Register Blood Bank model in the admin panel
admin.site.register(BloodBank, BloodBankAdmin)


# Staff Admin Configuration
class StaffAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'contact', 'role', 'is_active', 'is_staff', 'date_joined', 'created_date', 'modified_date')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('email', 'name', 'contact', 'role')
    ordering = ('-date_joined',)

    # fieldsets = (
    #     (None, {'fields': ('email', 'password')}),
    #     (_('Personal info'), {'fields': ('name', 'contact', 'role', 'first_name', 'last_name')}),
    #     (_('Permissions'), {'fields': ('is_active', 'is_staff', 'groups', 'user_permissions')}),
    #     (_('Important dates'), {'fields': ('date_joined', 'created_date', 'modified_date')}),
    # )

# Register Staff model in the admin panel
admin.site.register(Staff, StaffAdmin)

# Donor Admin Configuration
class DonorAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'contact', 'blood_group', 'is_active', 'is_staff', 'date_joined', 'created_date', 'modified_date')
    list_filter = ('is_active', 'blood_group')
    search_fields = ('email', 'name', 'contact', 'blood_group')
    ordering = ('-date_joined',)

    # fieldsets = (
    #     (None, {'fields': ('email', 'password')}),
    #     (_('Personal info'), {'fields': ('name', 'contact', 'blood_group', 'first_name', 'last_name', 'address')}),
    #     (_('Permissions'), {'fields': ('is_active', 'is_staff', 'groups', 'user_permissions')}),
    #     (_('Important dates'), {'fields': ('date_joined', 'created_date', 'modified_date')}),
    # )

# Register Donor model in the admin panel
admin.site.register(Donor, DonorAdmin)

# Consumer Admin Configuration
class ConsumerAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'contact', 'blood_group', 'is_active', 'is_staff', 'date_joined', 'created_date', 'modified_date')
    list_filter = ('is_active', 'blood_group')
    search_fields = ('email', 'name', 'contact', 'blood_group')
    ordering = ('-date_joined',)

    # fieldsets = (
    #     (None, {'fields': ('email', 'password')}),
    #     (_('Personal info'), {'fields': ('name', 'contact', 'blood_group', 'first_name', 'last_name', 'address')}),
    #     (_('Permissions'), {'fields': ('is_active', 'is_staff', 'groups', 'user_permissions')}),
    #     (_('Important dates'), {'fields': ('date_joined', 'created_date', 'modified_date')}),
    # )

# Register Consumer model in the admin panel
admin.site.register(Consumer, ConsumerAdmin)