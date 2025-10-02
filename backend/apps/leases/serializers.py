from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Lease, LeaseTerms, PaymentSchedule, LeaseTemplate
from apps.properties.models import Property
from apps.users.models import User

User = get_user_model()

class LeaseTemplateSerializer(serializers.ModelSerializer):
    """Serializer for lease templates."""
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    template_type_display = serializers.CharField(source='get_template_type_display', read_only=True)
    is_popular = serializers.ReadOnlyField()
    
    class Meta:
        model = LeaseTemplate
        fields = [
            'id', 'name', 'description', 'template_type', 'template_type_display',
            'created_by', 'created_by_name', 'is_public', 'is_default',
            'default_lease_duration_months', 'default_notice_period_days',
            'default_security_deposit_months', 'terms_and_conditions',
            'special_clauses', 'default_max_occupants', 'default_pets_allowed',
            'default_smoking_allowed', 'default_subletting_allowed',
            'usage_count', 'is_popular', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_by_name', 'template_type_display', 'usage_count',
            'is_popular', 'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        """Set created_by to current user."""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class LeaseTemplateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for lease template listings."""
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    template_type_display = serializers.CharField(source='get_template_type_display', read_only=True)
    is_popular = serializers.ReadOnlyField()
    
    class Meta:
        model = LeaseTemplate
        fields = [
            'id', 'name', 'description', 'template_type', 'template_type_display',
            'created_by', 'created_by_name', 'is_public', 'is_default',
            'usage_count', 'is_popular', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_by_name', 'template_type_display', 'usage_count',
            'is_popular', 'created_at', 'updated_at'
        ]

class LeaseTermsSerializer(serializers.ModelSerializer):
    """Serializer for lease terms."""
    
    class Meta:
        model = LeaseTerms
        fields = [
            'id', 'lease', 'rent_amount', 'security_deposit', 'pet_deposit',
            'late_fee', 'grace_period_days', 'rent_due_day', 'lease_break_fee',
            'early_termination_allowed', 'renewal_option', 'rent_increase_percentage',
            'utilities_included', 'maintenance_responsibility', 'pet_policy',
            'smoking_allowed', 'subletting_allowed', 'guest_policy',
            'parking_included', 'storage_included', 'amenities_included',
            'special_terms', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class PaymentScheduleSerializer(serializers.ModelSerializer):
    """Serializer for payment schedules."""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    amount_display = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentSchedule
        fields = [
            'id', 'lease', 'payment_type', 'payment_type_display', 'amount',
            'amount_display', 'due_date', 'paid_date', 'status', 'status_display',
            'payment_method', 'transaction_id', 'notes', 'is_overdue',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status_display', 'payment_type_display', 'amount_display',
            'is_overdue', 'created_at', 'updated_at'
        ]
    
    def get_amount_display(self, obj):
        """Format amount for display."""
        return f"${obj.amount:,.2f}" if obj.amount else "$0.00"
    
    def get_is_overdue(self, obj):
        """Check if payment is overdue."""
        from django.utils import timezone
        return obj.status == 'pending' and obj.due_date < timezone.now().date()

class LeaseListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for lease listings."""
    
    tenant_name = serializers.CharField(source='tenant.get_full_name', read_only=True)
    landlord_name = serializers.CharField(source='landlord.get_full_name', read_only=True)
    property_title = serializers.CharField(source='property_ref.title', read_only=True)
    property_address = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    rent_amount = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()
    next_payment_due = serializers.SerializerMethodField()
    
    class Meta:
        model = Lease
        fields = [
            'id', 'lease_number', 'tenant', 'tenant_name', 'landlord', 'landlord_name',
            'property_ref', 'property_title', 'property_address', 'start_date', 'end_date',
            'status', 'status_display', 'rent_amount', 'days_remaining', 'next_payment_due',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'lease_number', 'tenant_name', 'landlord_name', 'property_title',
            'property_address', 'status_display', 'rent_amount', 'days_remaining',
            'next_payment_due', 'created_at', 'updated_at'
        ]
    
    def get_property_address(self, obj):
        """Get property address."""
        if obj.property_ref:
            parts = [obj.property_ref.address_line_1, obj.property_ref.city, obj.property_ref.state]
            return ", ".join(filter(None, parts))
        return None
    
    def get_rent_amount(self, obj):
        """Get rent amount from lease terms."""
        terms = getattr(obj, 'terms', None)
        if terms:
            return f"${terms.rent_amount:,.2f}" if terms.rent_amount else "$0.00"
        return "Not set"
    
    def get_days_remaining(self, obj):
        """Calculate days remaining in lease."""
        from django.utils import timezone
        if obj.end_date:
            delta = obj.end_date - timezone.now().date()
            return delta.days if delta.days > 0 else 0
        return None
    
    def get_next_payment_due(self, obj):
        """Get next payment due date."""
        next_payment = obj.payment_schedules.filter(
            status='pending'
        ).order_by('due_date').first()
        
        if next_payment:
            return {
                'due_date': next_payment.due_date,
                'amount': f"${next_payment.amount:,.2f}",
                'type': next_payment.get_payment_type_display()
            }
        return None

class LeaseDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for lease details."""
    
    tenant_details = serializers.SerializerMethodField()
    landlord_details = serializers.SerializerMethodField()
    property_details = serializers.SerializerMethodField()
    terms = LeaseTermsSerializer(read_only=True)
    payment_schedules = PaymentScheduleSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    days_remaining = serializers.SerializerMethodField()
    total_payments_made = serializers.SerializerMethodField()
    outstanding_balance = serializers.SerializerMethodField()
    
    class Meta:
        model = Lease
        fields = [
            'id', 'lease_number', 'tenant', 'tenant_details', 'landlord', 'landlord_details',
            'property_ref', 'property_details', 'start_date', 'end_date', 'status', 'status_display',
            'move_in_date', 'move_out_date', 'renewal_date', 'termination_notice_date',
            'terms', 'payment_schedules', 'days_remaining', 'total_payments_made',
            'outstanding_balance', 'notes', 'documents', 'visibility_level',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'lease_number', 'tenant_details', 'landlord_details', 'property_details',
            'status_display', 'terms', 'payment_schedules', 'days_remaining',
            'total_payments_made', 'outstanding_balance', 'created_at', 'updated_at'
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
    
    def get_landlord_details(self, obj):
        """Get landlord details."""
        if obj.landlord:
            return {
                'id': obj.landlord.id,
                'name': obj.landlord.get_full_name(),
                'email': obj.landlord.email,
                'phone': getattr(obj.landlord, 'phone', None)
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
                'bathrooms': obj.property_ref.bathrooms,
                'square_feet': obj.property_ref.square_feet
            }
        return None
    
    def get_days_remaining(self, obj):
        """Calculate days remaining in lease."""
        from django.utils import timezone
        if obj.end_date:
            delta = obj.end_date - timezone.now().date()
            return delta.days if delta.days > 0 else 0
        return None
    
    def get_total_payments_made(self, obj):
        """Calculate total payments made."""
        total = obj.payment_schedules.filter(status='paid').aggregate(
            total=serializers.models.Sum('amount')
        )['total'] or 0
        return f"${total:,.2f}"
    
    def get_outstanding_balance(self, obj):
        """Calculate outstanding balance."""
        total = obj.payment_schedules.filter(status='pending').aggregate(
            total=serializers.models.Sum('amount')
        )['total'] or 0
        return f"${total:,.2f}"

class LeaseCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating leases."""
    
    terms_data = LeaseTermsSerializer(write_only=True, required=False)
    
    class Meta:
        model = Lease
        fields = [
            'tenant', 'landlord', 'property_ref', 'start_date', 'end_date',
            'move_in_date', 'move_out_date', 'renewal_date', 'termination_notice_date',
            'status', 'notes', 'documents', 'visibility_level', 'terms_data'
        ]
    
    def create(self, validated_data):
        """Create lease with terms."""
        terms_data = validated_data.pop('terms_data', None)
        lease = super().create(validated_data)
        
        if terms_data:
            LeaseTerms.objects.create(lease=lease, **terms_data)
        
        return lease
    
    def update(self, instance, validated_data):
        """Update lease with terms."""
        terms_data = validated_data.pop('terms_data', None)
        instance = super().update(instance, validated_data)
        
        if terms_data:
            terms, created = LeaseTerms.objects.get_or_create(
                lease=instance,
                defaults=terms_data
            )
            if not created:
                for key, value in terms_data.items():
                    setattr(terms, key, value)
                terms.save()
        
        return instance
    
    def validate(self, data):
        """Validate lease data."""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(
                "End date must be after start date."
            )
        
        return data

class PaymentScheduleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating payment schedules."""
    
    class Meta:
        model = PaymentSchedule
        fields = [
            'lease', 'payment_type', 'amount', 'due_date', 'paid_date',
            'status', 'payment_method', 'transaction_id', 'notes'
        ]
    
    def validate(self, data):
        """Validate payment schedule data."""
        status = data.get('status')
        paid_date = data.get('paid_date')
        
        if status == 'paid' and not paid_date:
            raise serializers.ValidationError(
                "Paid date is required when status is 'paid'."
            )
        
        if status != 'paid' and paid_date:
            raise serializers.ValidationError(
                "Paid date should only be set when status is 'paid'."
            )
        
        return data