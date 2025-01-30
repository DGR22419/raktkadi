from django.contrib import admin
from .models import *
from django.utils.html import format_html


class AdminAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'contact', 'user_type', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'name', 'contact', 'user_type')
    list_filter = ('user_type', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    ordering = ('email',)

class BloodBankProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'status')
    search_fields = ('status',)
    list_filter = ('status',)
    fields = ('user', 'address' ,  'license_document' , 'registration_certificate' , 'tax_documents','status')

class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    search_fields = ('role',)
    list_filter = ('role',)

class DonorProfileAdmin(admin.ModelAdmin):
    list_display = ('user','blood_group', 'last_donation')
    search_fields = ('blood_group',)
    list_filter = ('blood_group', 'last_donation')

class ConsumerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'blood_group')
    search_fields = ('blood_group',)
    list_filter = ('blood_group',)

class SuperUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'contact', 'user_type', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'name', 'contact', 'user_type')
    ordering = ['email' , ]

    def get_queryset(self, request):
        """Override the queryset to display only superusers."""
        qs = super().get_queryset(request)  # Get the default queryset
        return qs.filter(is_superuser=True)  # Filter to show only superusers

admin.site.register(Admin, SuperUserAdmin)
# admin.site.register(Admin, AdminAdmin)
admin.site.register(BloodBankProfile, BloodBankProfileAdmin)
admin.site.register(StaffProfile, StaffProfileAdmin)
admin.site.register(DonorProfile, DonorProfileAdmin)
admin.site.register(ConsumerProfile, ConsumerProfileAdmin)