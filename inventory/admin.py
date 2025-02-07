from django.contrib import admin
from .models import *
from django.db.models import Count
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.contrib import messages

class BloodBagAdmin(admin.ModelAdmin):
    list_display = ('blood_group', 'volume_ml', 'collection_date', 'expiration_date', 'status', 'barcode', 'blood_bank', 'donor')
    search_fields = ('blood_group', 'barcode', 'blood_bank__blood_bank_name', 'donor__first_name', 'donor__last_name')
    list_filter = ('blood_group', 'status', 'collection_date', 'expiration_date', 'blood_bank')
    ordering = ('-collection_date',)
    readonly_fields = ('barcode',)
    
    def changelist_view(self, request, extra_context=None):
        stats_html = self.get_stats_html(request)
        self.message_user(request, mark_safe(stats_html), level=messages.WARNING)
        return super().changelist_view(request, extra_context=extra_context)
    
    def get_stats_html(self, request):
        qs = self.get_queryset(request)
        
        # Calculate statistics
        context = {
            'total_bags': qs.count(),
            'available_bags': qs.filter(status='AVAILABLE').count(),
            'reserved_bags': qs.filter(status='RESERVED').count(),
            'used_bags': qs.filter(status='USED').count(),
            'expired_bags': qs.filter(status='EXPIRED').count(),
            'blood_group_stats': qs.filter(
                status='AVAILABLE'
            ).values('blood_group').annotate(
                count=Count('id')
            ).order_by('blood_group')
        }
        return render_to_string('admin/inventory/blood_bags.html', context)
    
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

class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'consumer', 'blood_bank', 'blood_group', 'units_required', 'priority', 'status', 'requested_date', 'required_date')
    list_filter = ('status', 'priority', 'blood_group', 'requested_date')
    search_fields = ('notes', 'rejection_reason')
    readonly_fields = ('requested_date', 'response_date')
    
    # def get_queryset(self, request):
    #     return super().get_queryset(request).select_related('consumer', 'blood_bank')
admin.site.register(BloodBag, BloodBagAdmin)
admin.site.register(StockTransaction, StockTransactionAdmin)
admin.site.register(BloodRequest , BloodRequestAdmin)
# admin.site.register(InventoryAlert, InventoryAlertAdmin)