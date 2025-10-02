from django.contrib import admin
from django.utils.html import format_html
from .models import MaintenanceRequest, Contractor, WorkOrder


@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    """
    Admin configuration for Contractor model.
    Provides comprehensive contractor management and performance tracking.
    """
    list_display = [
        'user', 'company_name', 'specializations_display', 'rating',
        'total_jobs', 'status', 'business_phone', 'business_email', 'created_at'
    ]
    list_filter = [
        'status', 'rating', 'created_at'
    ]
    search_fields = [
        'user__first_name', 'user__last_name', 'company_name', 'business_email', 'business_phone',
        'license_number'
    ]
    readonly_fields = ['created_at', 'updated_at', 'total_jobs']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'user', 'company_name', 'business_email', 'business_phone',
                'address', 'city', 'state', 'postal_code', 'status'
            )
        }),
        ('Professional Details', {
            'fields': (
                'specializations', 'license_number', 'website'
            )
        }),
        ('Performance Metrics', {
            'fields': ('rating', 'total_jobs')
        }),
        ('Availability', {
            'fields': ('available_days', 'available_hours_start', 'available_hours_end')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def specializations_display(self, obj):
        """Display contractor specializations in list view."""
        if obj.specializations:
            return ', '.join(obj.specializations[:3])
        return '-'
    specializations_display.short_description = 'Specializations'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('user')


class WorkOrderInline(admin.TabularInline):
    """
    Inline admin for WorkOrder within MaintenanceRequest admin.
    """
    model = WorkOrder
    extra = 0
    readonly_fields = ['work_order_number', 'created_at', 'updated_at']
    fields = [
        'work_order_number', 'contractor', 'status', 'scheduled_date',
        'estimated_cost', 'actual_cost', 'completion_date'
    ]


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    """
    Admin configuration for MaintenanceRequest model.
    Provides comprehensive maintenance request management with inline work orders.
    """
    list_display = [
        'request_number', 'property_title', 'tenant_name', 'category',
        'priority', 'status', 'created_at', 'estimated_cost'
    ]
    list_filter = [
        'category', 'priority', 'status',
        'created_at', 'scheduled_date'
    ]
    search_fields = [
        'request_number', 'title', 'description',
        'property_ref__title', 'tenant__first_name', 'tenant__last_name'
    ]
    readonly_fields = [
        'request_number', 'created_at', 'updated_at',
        'days_since_submitted'
    ]
    inlines = [WorkOrderInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'request_number', 'property', 'tenant', 'title',
                'description', 'category', 'priority', 'status'
            )
        }),
        ('Scheduling & Access', {
             'fields': (
                 'preferred_date', 'preferred_time', 'scheduled_date', 'scheduled_time',
                 'tenant_available', 'access_instructions'
             )
         }),
         ('Cost Information', {
             'fields': ('estimated_cost', 'actual_cost')
         }),
         ('Additional Details', {
             'fields': ('location_details', 'images', 'days_since_submitted')
         }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def property_title(self, obj):
        """Display property title in list view."""
        return obj.property_ref.title if obj.property_ref else '-'
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
            'property_ref', 'tenant', 'landlord'
        )


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    """
    Admin configuration for WorkOrder model.
    Provides detailed work order tracking and contractor management.
    """
    list_display = [
        'work_order_number', 'maintenance_request_info', 'contractor_name',
        'status', 'scheduled_date', 'estimated_cost', 'actual_cost',
        'is_overdue'
    ]
    list_filter = [
        'status', 'scheduled_date',
        'contractor', 'created_at'
    ]
    search_fields = [
        'work_order_number', 'maintenance_request__request_number',
        'maintenance_request__title', 'contractor__user__first_name',
        'contractor__user__last_name', 'contractor__company_name', 'work_description'
    ]
    readonly_fields = [
        'work_order_number', 'created_at', 'updated_at', 'is_overdue'
    ]
    date_hierarchy = 'scheduled_date'
    
    fieldsets = (
        ('Work Order Information', {
            'fields': (
                'work_order_number', 'maintenance_request', 'contractor',
                'status', 'work_description'
            )
        }),
        ('Scheduling', {
            'fields': (
                'scheduled_date', 'estimated_hours', 'completion_date',
                'actual_hours'
            )
        }),
        ('Cost Information', {
            'fields': (
                'estimated_cost', 'actual_cost', 'materials_cost',
                'labor_cost'
            )
        }),
        ('Quality & Completion', {
            'fields': (
                'quality_rating', 'completion_notes', 'warranty_period',
                'is_overdue'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def maintenance_request_info(self, obj):
        """Display maintenance request information in list view."""
        if obj.maintenance_request:
            return f"{obj.maintenance_request.request_number} - {obj.maintenance_request.title}"
        return '-'
    maintenance_request_info.short_description = 'Maintenance Request'
    
    def contractor_name(self, obj):
        """Display contractor name in list view."""
        return obj.contractor.name if obj.contractor else '-'
    contractor_name.short_description = 'Contractor'
    
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
            'maintenance_request__property', 'maintenance_request__tenant',
            'contractor'
        )
