from django.contrib import admin
from .models import *

class BloodBagAdmin(admin.ModelAdmin):
    list_display = ('blood_group', 'volume_ml', 'collection_date', 'expiration_date', 'status', 'barcode', 'blood_bank', 'donor')
    search_fields = ('blood_group', 'barcode', 'blood_bank__blood_bank_name', 'donor__first_name', 'donor__last_name')
    list_filter = ('blood_group', 'status', 'collection_date', 'expiration_date', 'blood_bank')
    ordering = ('-collection_date',)

class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('blood_bag', 'transaction_type', 'timestamp', 'source_location', 'destination_location')
    search_fields = ('blood_bag__barcode', 'transaction_type', 'source_location', 'destination_location')
    list_filter = ('transaction_type', 'timestamp')
    ordering = ('-timestamp',)

class InventoryAlertAdmin(admin.ModelAdmin):
    list_display = ('blood_bank', 'alert_type', 'blood_group', 'is_active', 'created_at', 'resolved_at')
    search_fields = ('blood_bank__blood_bank_name', 'alert_type', 'blood_group')
    list_filter = ('alert_type', 'blood_group', 'is_active', 'created_at', 'resolved_at')
    ordering = ('-created_at',)

admin.site.register(BloodBag, BloodBagAdmin)
admin.site.register(StockTransaction, StockTransactionAdmin)
# admin.site.register(InventoryAlert, InventoryAlertAdmin)