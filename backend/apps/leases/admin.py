from django.contrib import admin
from django.utils.html import format_html
from .models import Lease, PaymentSchedule, LeaseTerms


@admin.register(LeaseTerms)
class LeaseTermsAdmin(admin.ModelAdmin):
    """
    Admin configuration for LeaseTerms model.
    Provides comprehensive management of lease terms and conditions.
    """
    list_display = [
        'lease', 'max_occupants', 'pets_allowed', 'smoking_allowed', 'subletting_allowed', 'parking_spaces_included'
    ]
    list_filter = [
        'pets_allowed', 'smoking_allowed', 'subletting_allowed', 'commercial_use_allowed'
    ]
    search_fields = ['lease__lease_number', 'lease__tenant__first_name', 'lease__tenant__last_name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'lease_type', 'is_active')
        }),
        ('Duration & Financial Terms', {
            'fields': (
                'min_duration_months', 'max_duration_months',
                'security_deposit_months', 'late_fee_percentage',
                'grace_period_days', 'notice_period_days'
            )
        }),
        ('Property Rules', {
            'fields': (
                'allows_pets', 'pet_deposit_amount', 'allows_smoking',
                'utilities_included', 'maintenance_responsibility'
            )
        }),
        ('Additional Terms', {
            'fields': ('special_conditions', 'renewal_terms')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


class PaymentScheduleInline(admin.TabularInline):
    """
    Inline admin for PaymentSchedule within Lease admin.
    """
    model = PaymentSchedule
    extra = 0
    readonly_fields = ['created_at', 'updated_at']
    fields = [
        'due_date', 'amount', 'payment_type', 'status',
        'paid_date', 'paid_amount', 'notes'
    ]


@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    """
    Admin configuration for Lease model.
    Provides comprehensive lease management with inline payment schedules.
    """
    list_display = [
        'lease_number', 'property_title', 'tenant_name', 'status',
        'start_date', 'end_date', 'monthly_rent', 'security_deposit',
        'created_at'
    ]
    list_filter = [
        'status', 'start_date', 'end_date',
        'created_at'
    ]
    search_fields = [
        'lease_number', 'property__title', 'tenant__first_name',
        'tenant__last_name', 'tenant__email'
    ]
    readonly_fields = [
        'lease_number', 'created_at', 'updated_at'
    ]
    inlines = [PaymentScheduleInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'lease_number', 'property', 'tenant', 'lease_terms', 'status'
            )
        }),
        ('Lease Period', {
            'fields': ('start_date', 'end_date', 'actual_move_in_date', 'actual_move_out_date')
        }),
        ('Financial Terms', {
            'fields': (
                'monthly_rent', 'security_deposit', 'pet_deposit'
            )
        }),
        ('Additional Information', {
            'fields': ('notes', 'special_terms')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def property_title(self, obj):
        """Display property title in list view."""
        return obj.property.title if obj.property else '-'
    property_title.short_description = 'Property'
    
    def tenant_name(self, obj):
        """Display tenant full name in list view."""
        if obj.tenant:
            return f"{obj.tenant.first_name} {obj.tenant.last_name}"
        return '-'
    tenant_name.short_description = 'Tenant'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'property', 'tenant', 'lease_terms'
        )


@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    """
    Admin configuration for PaymentSchedule model.
    Provides detailed payment tracking and management.
    """
    list_display = [
        'lease_info', 'due_date', 'amount_due', 'payment_type',
        'status', 'amount_paid', 'paid_date', 'is_overdue'
    ]
    list_filter = [
        'payment_type', 'status', 'due_date', 'paid_date',
        'lease__status', 'created_at'
    ]
    search_fields = [
        'lease__lease_number', 'lease__property__title',
        'lease__tenant__first_name', 'lease__tenant__last_name',
        'notes'
    ]
    readonly_fields = ['created_at', 'updated_at', 'is_overdue']
    date_hierarchy = 'due_date'
    
    fieldsets = (
        ('Payment Information', {
            'fields': (
                'lease', 'due_date', 'amount', 'payment_type', 'status'
            )
        }),
        ('Payment Details', {
            'fields': ('paid_date', 'paid_amount', 'payment_method', 'transaction_id')
        }),
        ('Additional Information', {
            'fields': ('notes', 'late_fee_applied', 'is_overdue')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def lease_info(self, obj):
        """Display lease information in list view."""
        if obj.lease:
            return f"{obj.lease.lease_number} - {obj.lease.property.title}"
        return '-'
    lease_info.short_description = 'Lease'
    
    def is_overdue(self, obj):
        """Display overdue status with color coding."""
        if obj.is_overdue():
            return format_html(
                '<span style="color: red; font-weight: bold;">Yes</span>'
            )
        return format_html(
            '<span style="color: green;">No</span>'
        )
    is_overdue.short_description = 'Overdue'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'lease__property', 'lease__tenant'
        )
