from django.contrib import admin

# Register your models here.
from .models import Hospital, Patient, Donor

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'contact', 'address', 'date_joined')
    search_fields = ('name', 'email')
    list_filter = ('is_active', 'date_joined')
    ordering = ('-date_joined',)

@admin.register(Patient) 
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'contact', 'blood_group', 'date_joined')
    search_fields = ('name', 'email', 'blood_group')
    list_filter = ('blood_group', 'is_active', 'date_joined')
    ordering = ('-date_joined',)

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'contact', 'blood_group', 'last_donation', 'date_joined')
    search_fields = ('name', 'email', 'blood_group')
    list_filter = ('blood_group', 'is_active', 'date_joined')
    ordering = ('-date_joined',)
