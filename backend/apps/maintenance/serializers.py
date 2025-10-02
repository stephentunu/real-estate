from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import MaintenanceRequest, Contractor, WorkOrder
from apps.properties.models import Property
from apps.users.models import User

User = get_user_model()

class ContractorSerializer(serializers.ModelSerializer):
    """Serializer for contractors."""
    
    rating_display = serializers.SerializerMethodField()
    specialties_display = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Contractor
        fields = [
            'id', 'name', 'company_name', 'email', 'phone', 'address',
            'specialties', 'specialties_display', 'hourly_rate', 'rating',
            'rating_display', 'total_jobs', 'status', 'status_display',
            'license_number', 'insurance_info', 'notes', 'visibility_level',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'rating_display', 'specialties_display', 'status_display',
            'total_jobs', 'created_at', 'updated_at'
        ]
    
    def get_rating_display(self, obj):
        """Format rating for display."""
        if obj.rating:
            return f"{obj.rating:.1f}/5.0"
        return "No rating"
    
    def get_specialties_display(self, obj):
        """Format specialties for display."""
        if obj.specialties:
            return ", ".join(obj.specialties)
        return "No specialties listed"

class MaintenanceRequestListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for maintenance request listings."""
    
    tenant_name = serializers.CharField(source='tenant.get_full_name', read_only=True)
    property_title = serializers.CharField(source='property_ref.title', read_only=True)
    property_address = serializers.SerializerMethodField()
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    days_open = serializers.SerializerMethodField()
    has_work_order = serializers.SerializerMethodField()
    
    class Meta:
        model = MaintenanceRequest
        fields = [
            'id', 'request_number', 'tenant', 'tenant_name', 'property_ref',
            'property_title', 'property_address', 'title', 'category', 'category_display',
            'priority', 'priority_display', 'status', 'status_display',
            'requested_date', 'days_open', 'has_work_order', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'request_number', 'tenant_name', 'property_title', 'property_address',
            'priority_display', 'status_display', 'category_display', 'days_open',
            'has_work_order', 'created_at', 'updated_at'
        ]
    
    def get_property_address(self, obj):
        """Get property address."""
        if obj.property_ref:
            parts = [obj.property_ref.address_line_1, obj.property_ref.city, obj.property_ref.state]
            return ", ".join(filter(None, parts))
        return None
    
    def get_days_open(self, obj):
        """Calculate days since request was created."""
        from django.utils import timezone
        if obj.status not in ['completed', 'cancelled']:
            delta = timezone.now().date() - obj.requested_date
            return delta.days
        return None
    
    def get_has_work_order(self, obj):
        """Check if request has associated work order."""
        return hasattr(obj, 'work_order') and obj.work_order is not None

class MaintenanceRequestDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for maintenance request details."""
    
    tenant_details = serializers.SerializerMethodField()
    property_details = serializers.SerializerMethodField()
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    days_open = serializers.SerializerMethodField()
    work_order = serializers.SerializerMethodField()
    
    class Meta:
        model = MaintenanceRequest
        fields = [
            'id', 'request_number', 'tenant', 'tenant_details', 'property_ref',
            'property_details', 'title', 'description', 'category', 'category_display',
            'priority', 'priority_display', 'status', 'status_display',
            'requested_date', 'preferred_date', 'completed_date', 'days_open',
            'location_details', 'access_instructions', 'photos', 'tenant_notes',
            'admin_notes', 'work_order', 'visibility_level', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'request_number', 'tenant_details', 'property_details',
            'priority_display', 'status_display', 'category_display', 'days_open',
            'work_order', 'created_at', 'updated_at'
        ]
    
    def get_tenant_details(self, obj):
        """Get tenant details."""
        if obj.tenant:
            return {
                'id': obj.tenant.id,
                'name': obj.tenant.get_full_name(),
                'email': obj.tenant.email,
                'phone': getattr(obj.tenant, 'phone', None)
            }
        return None
    
    def get_property_details(self, obj):
        """Get property details."""
        if obj.property_ref:
            return {
                'id': obj.property_ref.id,
                'title': obj.property_ref.title,
                'address': f"{obj.property_ref.address_line_1}, {obj.property_ref.city}, {obj.property_ref.state}",
                'bedrooms': obj.property_ref.bedrooms,
                'bathrooms': obj.property_ref.bathrooms
            }
        return None
    
    def get_days_open(self, obj):
        """Calculate days since request was created."""
        from django.utils import timezone
        if obj.status not in ['completed', 'cancelled']:
            delta = timezone.now().date() - obj.requested_date
            return delta.days
        return None
    
    def get_work_order(self, obj):
        """Get associated work order details."""
        if hasattr(obj, 'work_order') and obj.work_order:
            work_order = obj.work_order
            return {
                'id': work_order.id,
                'work_order_number': work_order.work_order_number,
                'contractor': work_order.contractor.name if work_order.contractor else None,
                'status': work_order.get_status_display(),
                'scheduled_date': work_order.scheduled_date,
                'estimated_cost': f"${work_order.estimated_cost:,.2f}" if work_order.estimated_cost else None,
                'actual_cost': f"${work_order.actual_cost:,.2f}" if work_order.actual_cost else None
            }
        return None

class MaintenanceRequestCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating maintenance requests."""
    
    class Meta:
        model = MaintenanceRequest
        fields = [
            'tenant', 'property_ref', 'title', 'description', 'category',
            'priority', 'preferred_date', 'location_details', 'access_instructions',
            'photos', 'tenant_notes', 'visibility_level'
        ]
    
    def validate(self, data):
        """Validate maintenance request data."""
        preferred_date = data.get('preferred_date')
        
        if preferred_date:
            from django.utils import timezone
            if preferred_date < timezone.now().date():
                raise serializers.ValidationError(
                    "Preferred date cannot be in the past."
                )
        
        return data

class WorkOrderSerializer(serializers.ModelSerializer):
    """Serializer for work orders."""
    
    maintenance_request_details = serializers.SerializerMethodField()
    contractor_details = ContractorSerializer(source='contractor', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    estimated_cost_display = serializers.SerializerMethodField()
    actual_cost_display = serializers.SerializerMethodField()
    duration_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkOrder
        fields = [
            'id', 'work_order_number', 'maintenance_request', 'maintenance_request_details',
            'contractor', 'contractor_details', 'title', 'description', 'status', 'status_display',
            'scheduled_date', 'started_date', 'completed_date', 'estimated_hours',
            'actual_hours', 'duration_hours', 'estimated_cost', 'estimated_cost_display',
            'actual_cost', 'actual_cost_display', 'materials_cost', 'labor_cost',
            'notes', 'completion_notes', 'photos_before', 'photos_after',
            'visibility_level', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'work_order_number', 'maintenance_request_details', 'contractor_details',
            'status_display', 'estimated_cost_display', 'actual_cost_display',
            'duration_hours', 'created_at', 'updated_at'
        ]
    
    def get_maintenance_request_details(self, obj):
        """Get maintenance request details."""
        if obj.maintenance_request:
            return {
                'id': obj.maintenance_request.id,
                'request_number': obj.maintenance_request.request_number,
                'title': obj.maintenance_request.title,
                'category': obj.maintenance_request.get_category_display(),
                'priority': obj.maintenance_request.get_priority_display()
            }
        return None
    
    def get_estimated_cost_display(self, obj):
        """Format estimated cost for display."""
        return f"${obj.estimated_cost:,.2f}" if obj.estimated_cost else "Not estimated"
    
    def get_actual_cost_display(self, obj):
        """Format actual cost for display."""
        return f"${obj.actual_cost:,.2f}" if obj.actual_cost else "Not recorded"
    
    def get_duration_hours(self, obj):
        """Calculate duration in hours."""
        if obj.started_date and obj.completed_date:
            from datetime import datetime, timedelta
            if isinstance(obj.started_date, datetime) and isinstance(obj.completed_date, datetime):
                delta = obj.completed_date - obj.started_date
                return round(delta.total_seconds() / 3600, 2)
        return None

class WorkOrderCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating work orders."""
    
    class Meta:
        model = WorkOrder
        fields = [
            'maintenance_request', 'contractor', 'title', 'description',
            'scheduled_date', 'estimated_hours', 'estimated_cost',
            'materials_cost', 'labor_cost', 'notes', 'visibility_level'
        ]
    
    def validate(self, data):
        """Validate work order data."""
        scheduled_date = data.get('scheduled_date')
        estimated_hours = data.get('estimated_hours')
        estimated_cost = data.get('estimated_cost')
        
        if scheduled_date:
            from django.utils import timezone
            if scheduled_date < timezone.now().date():
                raise serializers.ValidationError(
                    "Scheduled date cannot be in the past."
                )
        
        if estimated_hours is not None and estimated_hours <= 0:
            raise serializers.ValidationError(
                "Estimated hours must be greater than 0."
            )
        
        if estimated_cost is not None and estimated_cost < 0:
            raise serializers.ValidationError(
                "Estimated cost cannot be negative."
            )
        
        return data