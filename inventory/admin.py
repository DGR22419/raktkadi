from django.contrib import admin
from .models import *
from django.db.models import Count
from django.template.loader import render_to_string
from django.utils.html import format_html

class BloodBagAdmin(admin.ModelAdmin):
    list_display = ('blood_group', 'volume_ml', 'collection_date', 'expiration_date', 'status', 'barcode', 'blood_bank', 'donor')
    search_fields = ('blood_group', 'barcode', 'blood_bank__blood_bank_name', 'donor__first_name', 'donor__last_name')
    list_filter = ('blood_group', 'status', 'collection_date', 'expiration_date', 'blood_bank')
    ordering = ('-collection_date',)
    readonly_fields = ('barcode',)
    
    def changelist_view(self, request, extra_context=None):
        stats_html = self.get_stats_html(request)
        self.change_list_template = 'admin/change_list.html'
        if not hasattr(self, 'action_form') or not self.action_form:
            from django.contrib.admin.helpers import ActionForm
            self.action_form = ActionForm
        
        self.message_user(request, format_html(stats_html))
        return super().changelist_view(request, extra_context=extra_context)
    
    def get_stats_html(self, request):
        qs = self.get_queryset(request)
        
        # Calculate statistics
        total_bags = qs.count()
        available_bags = qs.filter(status='AVAILABLE').count()
        reserved_bags = qs.filter(status='RESERVED').count()
        used_bags = qs.filter(status='USED').count()
        expired_bags = qs.filter(status='EXPIRED').count()
        
        # Get blood group statistics
        blood_group_stats = qs.filter(
            status='AVAILABLE'
        ).values('blood_group').annotate(
            count=Count('id')
        ).order_by('blood_group')
        
        # Enhanced button style CSS
        button_style = """
            display: inline-block;
            padding: 15px 25px;
            margin: 5px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
            min-width: 160px;
        """
        
        # Format HTML with enhanced styling
        stats_html = f"""
        <div style="margin: 10px 0; padding: 10px; background-color: #f8f9fa; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
            <div style="font-size: 24px; font-weight: bold; margin-bottom: 10px; color: #333;">
                Blood Bank Statistics
            </div>
            
            <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 10px;">
                <div style="{button_style} background-color: #f8f9fa;">
                    <div style="font-size: 28px; font-weight: bold; color: #333;">{total_bags}</div>
                    <div style="font-size: 16px; color: #666;">Total Bags</div>
                </div>
                
                <div style="{button_style} background-color: #d4edda;">
                    <div style="font-size: 28px; font-weight: bold; color: #28a745;">{available_bags}</div>
                    <div style="font-size: 16px; color: #155724;">Available</div>
                </div>
                
                <div style="{button_style} background-color: #fff3cd;">
                    <div style="font-size: 28px; font-weight: bold; color: #856404;">{reserved_bags}</div>
                    <div style="font-size: 16px; color: #856404;">Reserved</div>
                </div>
                
                <div style="{button_style} background-color: #cce5ff;">
                    <div style="font-size: 28px; font-weight: bold; color: #004085;">{used_bags}</div>
                    <div style="font-size: 16px; color: #004085;">Used</div>
                </div>
                
                <div style="{button_style} background-color: #f8d7da;">
                    <div style="font-size: 28px; font-weight: bold; color: #721c24;">{expired_bags}</div>
                    <div style="font-size: 16px; color: #721c24;">Expired</div>
                </div>
            </div>
            
            <div style="margin-top: 10px;">
                <div style="font-size: 20px; font-weight: bold; margin-bottom: 10px; color: #333;">
                    Available Blood Groups
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                    {' '.join([f'''
                        <div style="{button_style} background-color: #e8f4f8;">
                            <div style="font-size: 24px; font-weight: bold; color: #0056b3;">{stat["count"]}</div>
                            <div style="font-size: 16px; color: #004085;">{stat["blood_group"]}</div>
                        </div>
                    ''' for stat in blood_group_stats])}
                </div>
            </div>
        </div>
        """
        return stats_html

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