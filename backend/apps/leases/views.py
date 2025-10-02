from django.shortcuts import render

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Sum, Count
from django.shortcuts import get_object_or_404

from .models import Lease, LeaseTerms, PaymentSchedule, LeaseTemplate
from .serializers import (
    LeaseListSerializer, LeaseDetailSerializer, LeaseCreateUpdateSerializer,
    LeaseTermsSerializer, PaymentScheduleSerializer, PaymentScheduleCreateUpdateSerializer,
    LeaseTemplateSerializer, LeaseTemplateListSerializer
)
from apps.core.mixins import VisibilityMixin

class LeaseTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing lease templates."""
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['template_type', 'is_public', 'is_default', 'created_by']
    search_fields = ['name', 'description', 'terms_and_conditions']
    ordering_fields = ['name', 'template_type', 'usage_count', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get lease templates with visibility filtering."""
        queryset = LeaseTemplate.objects.select_related('created_by')
        
        user = self.request.user
        
        # Users can see their own templates and public templates
        queryset = queryset.filter(
            Q(created_by=user) | Q(is_public=True)
        )
        
        # Exclude soft deleted items unless specifically requested
        if not self.request.query_params.get('include_deleted'):
            queryset = queryset.filter(deleted_at__isnull=True)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return LeaseTemplateListSerializer
        return LeaseTemplateSerializer
    
    def perform_create(self, serializer):
        """Create template with current user as creator."""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Update template and handle slug generation."""
        instance = serializer.save()
        
        # Generate slug if name changed
        if 'name' in serializer.validated_data:
            from django.utils.text import slugify
            instance.slug = slugify(instance.name)
            instance.save(update_fields=['slug'])
    
    @action(detail=False, methods=['get'])
    def my_templates(self, request):
        """Get templates created by the current user."""
        queryset = self.get_queryset().filter(created_by=request.user)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def public_templates(self, request):
        """Get public templates available to all users."""
        queryset = self.get_queryset().filter(is_public=True)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular_templates(self, request):
        """Get popular templates based on usage count."""
        queryset = self.get_queryset().filter(usage_count__gte=10).order_by('-usage_count')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def use_template(self, request, pk=None):
        """Mark template as used and increment usage count."""
        template = self.get_object()
        template.increment_usage()
        
        serializer = self.get_serializer(template)
        return Response({
            'message': 'Template usage recorded',
            'template': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Create a copy of an existing template."""
        original_template = self.get_object()
        
        # Create a copy
        new_template = LeaseTemplate.objects.create(
            name=f"Copy of {original_template.name}",
            description=original_template.description,
            template_type=original_template.template_type,
            created_by=request.user,
            is_public=False,  # Copies are private by default
            is_default=False,  # Copies are not default
            default_lease_duration_months=original_template.default_lease_duration_months,
            default_notice_period_days=original_template.default_notice_period_days,
            default_security_deposit_months=original_template.default_security_deposit_months,
            terms_and_conditions=original_template.terms_and_conditions,
            special_clauses=original_template.special_clauses,
            default_max_occupants=original_template.default_max_occupants,
            default_pets_allowed=original_template.default_pets_allowed,
            default_smoking_allowed=original_template.default_smoking_allowed,
            default_subletting_allowed=original_template.default_subletting_allowed,
        )
        
        serializer = self.get_serializer(new_template)
        return Response({
            'message': 'Template duplicated successfully',
            'template': serializer.data
        }, status=status.HTTP_201_CREATED)

class LeaseViewSet(viewsets.ModelViewSet):
    """ViewSet for managing leases with visibility-aware filtering."""
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'tenant', 'landlord', 'property_ref']
    search_fields = ['lease_number', 'tenant__first_name', 'tenant__last_name', 'property_ref__title']
    ordering_fields = ['start_date', 'end_date', 'created_at', 'lease_number']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get leases with visibility filtering and soft deletion support."""
        queryset = Lease.objects.select_related(
            'tenant', 'landlord', 'property_ref', 'terms'
        ).prefetch_related('payment_schedules')
        
        # Apply visibility filtering
        user = self.request.user
        if hasattr(user, 'user_type'):
            if user.user_type == 'tenant':
                queryset = queryset.filter(tenant=user)
            elif user.user_type == 'landlord':
                queryset = queryset.filter(landlord=user)
            elif user.user_type == 'agent':
                # Agents can see leases for properties they manage
                queryset = queryset.filter(
                    Q(property_ref__agent=user) | Q(landlord=user)
                )
        
        # Filter by visibility level
        visibility_levels = ['PUBLIC', 'REGISTERED']
        if hasattr(user, 'user_type'):
            if user.user_type in ['landlord', 'agent']:
                visibility_levels.extend(['AGENCY_ONLY', 'LANDLORD_ONLY'])
            elif user.user_type == 'tenant':
                visibility_levels.append('TENANT_ONLY')
        
        queryset = queryset.filter(visibility_level__in=visibility_levels)
        
        # Exclude soft deleted items unless specifically requested
        if not self.request.query_params.get('include_deleted'):
            queryset = queryset.filter(deleted_at__isnull=True)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return LeaseListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return LeaseCreateUpdateSerializer
        return LeaseDetailSerializer
    
    def perform_create(self, serializer):
        """Create lease with current user as landlord if not specified."""
        if not serializer.validated_data.get('landlord'):
            serializer.save(landlord=self.request.user)
        else:
            serializer.save()
    
    @action(detail=False, methods=['get'])
    def my_leases(self, request):
        """Get leases for the current user."""
        user = request.user
        queryset = self.get_queryset()
        
        if hasattr(user, 'user_type'):
            if user.user_type == 'tenant':
                queryset = queryset.filter(tenant=user)
            elif user.user_type == 'landlord':
                queryset = queryset.filter(landlord=user)
            else:
                queryset = queryset.filter(
                    Q(tenant=user) | Q(landlord=user)
                )
        else:
            queryset = queryset.filter(
                Q(tenant=user) | Q(landlord=user)
            )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = LeaseListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = LeaseListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active_leases(self, request):
        """Get active leases."""
        queryset = self.get_queryset().filter(status='active')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = LeaseListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = LeaseListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Get leases expiring within 30 days."""
        from datetime import timedelta
        
        expiry_date = timezone.now().date() + timedelta(days=30)
        queryset = self.get_queryset().filter(
            status='active',
            end_date__lte=expiry_date,
            end_date__gte=timezone.now().date()
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = LeaseListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = LeaseListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def terminate(self, request, pk=None):
        """Terminate a lease."""
        lease = self.get_object()
        termination_date = request.data.get('termination_date')
        reason = request.data.get('reason', '')
        
        if not termination_date:
            return Response(
                {'error': 'Termination date is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lease.status = 'terminated'
        lease.termination_notice_date = timezone.now().date()
        lease.move_out_date = termination_date
        lease.notes = f"{lease.notes}\n\nTerminated on {timezone.now().date()}: {reason}"
        lease.save()
        
        serializer = LeaseDetailSerializer(lease, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        """Renew a lease."""
        lease = self.get_object()
        new_end_date = request.data.get('new_end_date')
        new_rent_amount = request.data.get('new_rent_amount')
        
        if not new_end_date:
            return Response(
                {'error': 'New end date is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lease.end_date = new_end_date
        lease.renewal_date = timezone.now().date()
        lease.status = 'active'
        lease.save()
        
        # Update rent amount if provided
        if new_rent_amount and hasattr(lease, 'terms'):
            lease.terms.rent_amount = new_rent_amount
            lease.terms.save()
        
        serializer = LeaseDetailSerializer(lease, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def payment_history(self, request, pk=None):
        """Get payment history for a lease."""
        lease = self.get_object()
        payments = lease.payment_schedules.all().order_by('-due_date')
        
        page = self.paginate_queryset(payments)
        if page is not None:
            serializer = PaymentScheduleSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = PaymentScheduleSerializer(payments, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def financial_summary(self, request, pk=None):
        """Get financial summary for a lease."""
        lease = self.get_object()
        
        payments = lease.payment_schedules.aggregate(
            total_paid=Sum('amount', filter=Q(status='paid')),
            total_pending=Sum('amount', filter=Q(status='pending')),
            total_overdue=Sum('amount', filter=Q(
                status='pending',
                due_date__lt=timezone.now().date()
            ))
        )
        
        summary = {
            'lease_id': lease.id,
            'lease_number': lease.lease_number,
            'total_paid': payments['total_paid'] or 0,
            'total_pending': payments['total_pending'] or 0,
            'total_overdue': payments['total_overdue'] or 0,
            'monthly_rent': lease.terms.rent_amount if hasattr(lease, 'terms') else 0,
            'security_deposit': lease.terms.security_deposit if hasattr(lease, 'terms') else 0
        }
        
        return Response(summary)

class PaymentScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing payment schedules."""
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_type', 'lease']
    search_fields = ['lease__lease_number', 'transaction_id']
    ordering_fields = ['due_date', 'amount', 'created_at']
    ordering = ['due_date']
    
    def get_queryset(self):
        """Get payment schedules with visibility filtering."""
        queryset = PaymentSchedule.objects.select_related('lease', 'lease__tenant', 'lease__landlord')
        
        # Apply visibility filtering based on lease access
        user = self.request.user
        if hasattr(user, 'user_type'):
            if user.user_type == 'tenant':
                queryset = queryset.filter(lease__tenant=user)
            elif user.user_type == 'landlord':
                queryset = queryset.filter(lease__landlord=user)
            elif user.user_type == 'agent':
                queryset = queryset.filter(
                    Q(lease__property_ref__agent=user) | Q(lease__landlord=user)
                )
        
        # Exclude soft deleted items
        if not self.request.query_params.get('include_deleted'):
            queryset = queryset.filter(deleted_at__isnull=True)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return PaymentScheduleCreateUpdateSerializer
        return PaymentScheduleSerializer
    
    @action(detail=False, methods=['get'])
    def overdue_payments(self, request):
        """Get overdue payments."""
        queryset = self.get_queryset().filter(
            status='pending',
            due_date__lt=timezone.now().date()
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PaymentScheduleSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = PaymentScheduleSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming_payments(self, request):
        """Get upcoming payments (next 30 days)."""
        from datetime import timedelta
        
        end_date = timezone.now().date() + timedelta(days=30)
        queryset = self.get_queryset().filter(
            status='pending',
            due_date__gte=timezone.now().date(),
            due_date__lte=end_date
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PaymentScheduleSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = PaymentScheduleSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark a payment as paid."""
        payment = self.get_object()
        
        payment.status = 'paid'
        payment.paid_date = timezone.now().date()
        payment.payment_method = request.data.get('payment_method', payment.payment_method)
        payment.transaction_id = request.data.get('transaction_id', payment.transaction_id)
        payment.notes = request.data.get('notes', payment.notes)
        payment.save()
        
        serializer = PaymentScheduleSerializer(payment, context={'request': request})
        return Response(serializer.data)

class LeaseTermsViewSet(viewsets.ModelViewSet):
    """ViewSet for managing lease terms."""
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['lease']
    
    def get_queryset(self):
        """Get lease terms with visibility filtering."""
        queryset = LeaseTerms.objects.select_related('lease', 'lease__tenant', 'lease__landlord')
        
        # Apply visibility filtering based on lease access
        user = self.request.user
        if hasattr(user, 'user_type'):
            if user.user_type == 'tenant':
                queryset = queryset.filter(lease__tenant=user)
            elif user.user_type == 'landlord':
                queryset = queryset.filter(lease__landlord=user)
            elif user.user_type == 'agent':
                queryset = queryset.filter(
                    Q(lease__property_ref__agent=user) | Q(lease__landlord=user)
                )
        
        return queryset
    
    serializer_class = LeaseTermsSerializer
