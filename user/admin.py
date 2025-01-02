from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import MedicalCenter, Patient, Donor, BloodRequest, RegularUser

class MedicalCenterAdmin(UserAdmin):
    list_display = ('email', 'name', 'contact', 'address', 'date_joined', 'is_staff')
    search_fields = ('email', 'name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'contact', 'address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'name', 'contact', 'address'),
        }),
    )

class RegularUserAdmin(UserAdmin):
    list_display = ('email', 'name', 'contact', 'date_joined', 'is_active')
    search_fields = ('email', 'name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'contact')}),
        ('Permissions', {'fields': ('is_active',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'name', 'contact'),
        }),
    )

admin.site.register(MedicalCenter, MedicalCenterAdmin)
# admin.site.register(Patient)
# admin.site.register(Donor)
# admin.site.register(BloodRequest)
admin.site.register(RegularUser, RegularUserAdmin)
