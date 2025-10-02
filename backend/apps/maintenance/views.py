from django.shortcuts import render

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Avg, Count
from django.shortcuts import get_object_or_404

from .models import MaintenanceRequest, Contractor, WorkOrder
from .serializers import (
    MaintenanceRequestListSerializer, MaintenanceRequestDetailSerializer,
    MaintenanceRequestCreateUpdateSerializer, ContractorSerializer,
    WorkOrderSerializer, WorkOrderCreateUpdateSerializer
)
from apps.core.mixins import VisibilityMixin

class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for managing maintenance requests with visibility-aware filtering."""
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'category', 'property_ref', 'tenant']
    search_fields = ['request_number', 'title', 'description', 'tenant__first_name', 'tenant__last_name']
    ordering_fields = ['created_at', 'priority', 'status', 'request_number']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get maintenance requests with visibility filtering and soft deletion support."""
        queryset = MaintenanceRequest.objects.select_related(
            'tenant', 'property_ref', 'landlord'
        ).prefetch_related('work_orders')
        
        # Apply visibility filtering
        user = self.request.user
        if hasattr(user, 'role'):
            if user.role == 'tenant':
                queryset = queryset.filter(tenant=user)
            elif user.role == 'landlord':
                queryset = queryset.filter(property_ref__landlord=user)
            elif user.role == 'agent':
                queryset = queryset.filter(
                    Q(property_ref__agent=user) | Q(property_ref__landlord=user)
                )
            elif user.role == 'contractor':
                # Contractors can see requests assigned to them through work orders
                queryset = queryset.filter(work_orders__contractor__user=user)
        
        # Filter by visibility level
        visibility_levels = ['PUBLIC', 'REGISTERED']
        if hasattr(user, 'role'):
            if user.role in ['landlord', 'agent']:
                visibility_levels.extend(['AGENCY_ONLY', 'LANDLORD_ONLY'])
            elif user.role == 'tenant':
                visibility_levels.append('TENANT_ONLY')
        
        queryset = queryset.filter(visibility_level__in=visibility_levels)
        
        # Exclude soft deleted items unless specifically requested
        if not self.request.query_params.get('include_deleted'):
            queryset = queryset.filter(deleted_at__isnull=True)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return MaintenanceRequestListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return MaintenanceRequestCreateUpdateSerializer
        return MaintenanceRequestDetailSerializer
    
    def perform_create(self, serializer):
        """Create maintenance request with current user as tenant if not specified."""
        if not serializer.validated_data.get('tenant') and hasattr(self.request.user, 'role'):
            if self.request.user.role == 'tenant':
                serializer.save(tenant=self.request.user)
            else:
                serializer.save()
        else:
            serializer.save()
    
    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Get maintenance requests for the current user."""
        user = request.user
        queryset = self.get_queryset()
        
        if hasattr(user, 'role'):
            if user.role == 'tenant':
                queryset = queryset.filter(tenant=user)
            elif user.role == 'landlord':
                queryset = queryset.filter(property_ref__landlord=user)
            elif user.role == 'contractor':
                queryset = queryset.filter(work_orders__contractor__user=user)
            else:
                queryset = queryset.none()
        else:
            queryset = queryset.none()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = MaintenanceRequestListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = MaintenanceRequestListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def urgent_requests(self, request):
        """Get urgent maintenance requests."""
        queryset = self.get_queryset().filter(
            priority='high',
            status__in=['pending', 'in_progress']
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = MaintenanceRequestListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = MaintenanceRequestListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue_requests(self, request):
        """Get overdue maintenance requests."""
        queryset = self.get_queryset().filter(
            status__in=['pending', 'in_progress'],
            expected_completion_date__lt=timezone.now().date()
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = MaintenanceRequestListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = MaintenanceRequestListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign_contractor(self, request, pk=None):
        """Assign a contractor to a maintenance request by creating a work order."""
        maintenance_request = self.get_object()
        contractor_id = request.data.get('contractor_id')
        
        if not contractor_id:
            return Response(
                {'error': 'Contractor ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            contractor = Contractor.objects.get(id=contractor_id)
        except Contractor.DoesNotExist:
            return Response(
                {'error': 'Contractor not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create a work order to assign the contractor
        work_order = WorkOrder.objects.create(
            maintenance_request=maintenance_request,
            contractor=contractor,
            title=maintenance_request.title,
            description=maintenance_request.description,
            status='assigned'
        )
        
        # Update maintenance request status
        maintenance_request.status = 'assigned'
        maintenance_request.save()
        
        serializer = MaintenanceRequestDetailSerializer(maintenance_request, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update the status of a maintenance request."""
        maintenance_request = self.get_object()
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        
        if not new_status:
            return Response(
                {'error': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        valid_statuses = ['pending', 'assigned', 'in_progress', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        maintenance_request.status = new_status
        if new_status == 'completed':
            maintenance_request.completion_date = timezone.now().date()
        
        if notes:
            maintenance_request.notes = f"{maintenance_request.notes}\n\n{timezone.now().date()}: {notes}"
        
        maintenance_request.save()
        
        serializer = MaintenanceRequestDetailSerializer(maintenance_request, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def work_orders(self, request, pk=None):
        """Get work orders for a maintenance request."""
        maintenance_request = self.get_object()
        work_orders = maintenance_request.work_orders.all().order_by('-created_at')
        
        page = self.paginate_queryset(work_orders)
        if page is not None:
            serializer = WorkOrderSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = WorkOrderSerializer(work_orders, many=True, context={'request': request})
        return Response(serializer.data)

class ContractorViewSet(viewsets.ModelViewSet):
    """ViewSet for managing contractors."""
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['specialties', 'is_active', 'rating']
    search_fields = ['company_name', 'contact_person', 'phone', 'email']
    ordering_fields = ['company_name', 'rating', 'created_at']
    ordering = ['company_name']
    serializer_class = ContractorSerializer
    
    def get_queryset(self):
        """Get contractors with visibility filtering."""
        queryset = Contractor.objects.all()
        
        # Apply visibility filtering
        user = self.request.user
        if hasattr(user, 'role'):
            if user.role == 'contractor':
                # Contractors can only see their own profile
                queryset = queryset.filter(user=user)
            elif user.role not in ['landlord', 'agent', 'admin']:
                # Regular users can only see active contractors
                queryset = queryset.filter(is_active=True)
        
        # Exclude soft deleted items
        if not self.request.query_params.get('include_deleted'):
            queryset = queryset.filter(deleted_at__isnull=True)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def available_contractors(self, request):
        """Get available contractors for assignment."""
        queryset = self.get_queryset().filter(is_active=True)
        
        # Filter by specialty if provided
        specialty = request.query_params.get('specialty')
        if specialty:
            queryset = queryset.filter(specialties__icontains=specialty)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ContractorSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ContractorSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        """Get top-rated contractors."""
        queryset = self.get_queryset().filter(
            is_active=True,
            rating__gte=4.0
        ).order_by('-rating')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ContractorSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ContractorSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def maintenance_history(self, request, pk=None):
        """Get maintenance history for a contractor."""
        contractor = self.get_object()
        requests = MaintenanceRequest.objects.filter(
            assigned_contractor=contractor
        ).order_by('-created_at')
        
        page = self.paginate_queryset(requests)
        if page is not None:
            serializer = MaintenanceRequestListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = MaintenanceRequestListSerializer(requests, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def performance_stats(self, request, pk=None):
        """Get performance statistics for a contractor."""
        contractor = self.get_object()
        
        stats = MaintenanceRequest.objects.filter(
            assigned_contractor=contractor
        ).aggregate(
            total_requests=Count('id'),
            completed_requests=Count('id', filter=Q(status='completed')),
            avg_completion_time=Avg('completion_date') # This would need custom calculation
        )
        
        performance = {
            'contractor_id': contractor.id,
            'company_name': contractor.company_name,
            'rating': contractor.rating,
            'total_requests': stats['total_requests'] or 0,
            'completed_requests': stats['completed_requests'] or 0,
            'completion_rate': (
                (stats['completed_requests'] / stats['total_requests'] * 100)
                if stats['total_requests'] > 0 else 0
            ),
            'specialties': contractor.specialties
        }
        
        return Response(performance)

class WorkOrderViewSet(viewsets.ModelViewSet):
    """ViewSet for managing work orders."""
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'maintenance_request', 'contractor']
    search_fields = ['work_order_number', 'description', 'contractor__company_name']
    ordering_fields = ['scheduled_date', 'created_at', 'work_order_number']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get work orders with visibility filtering."""
        queryset = WorkOrder.objects.select_related(
            'maintenance_request', 'contractor', 'maintenance_request__tenant'
        )
        
        # Apply visibility filtering based on maintenance request access
        user = self.request.user
        if hasattr(user, 'role'):
            if user.role == 'tenant':
                queryset = queryset.filter(maintenance_request__tenant=user)
            elif user.role == 'landlord':
                queryset = queryset.filter(maintenance_request__property_ref__landlord=user)
            elif user.role == 'agent':
                queryset = queryset.filter(
                    Q(maintenance_request__property_ref__agent=user) |
                    Q(maintenance_request__property_ref__landlord=user)
                )
            elif user.role == 'contractor':
                queryset = queryset.filter(contractor__user=user)
        
        # Exclude soft deleted items
        if not self.request.query_params.get('include_deleted'):
            queryset = queryset.filter(deleted_at__isnull=True)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return WorkOrderCreateUpdateSerializer
        return WorkOrderSerializer
    
    @action(detail=False, methods=['get'])
    def scheduled_today(self, request):
        """Get work orders scheduled for today."""
        today = timezone.now().date()
        queryset = self.get_queryset().filter(
            scheduled_date=today,
            status__in=['scheduled', 'in_progress']
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = WorkOrderSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = WorkOrderSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming_work(self, request):
        """Get upcoming work orders (next 7 days)."""
        from datetime import timedelta
        
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=7)
        
        queryset = self.get_queryset().filter(
            scheduled_date__gte=start_date,
            scheduled_date__lte=end_date,
            status__in=['scheduled', 'in_progress']
        ).order_by('scheduled_date')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = WorkOrderSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = WorkOrderSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def start_work(self, request, pk=None):
        """Start a work order."""
        work_order = self.get_object()
        
        work_order.status = 'in_progress'
        work_order.actual_start_date = timezone.now().date()
        work_order.save()
        
        # Update maintenance request status
        if work_order.maintenance_request.status != 'in_progress':
            work_order.maintenance_request.status = 'in_progress'
            work_order.maintenance_request.save()
        
        serializer = WorkOrderSerializer(work_order, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete_work(self, request, pk=None):
        """Complete a work order."""
        work_order = self.get_object()
        completion_notes = request.data.get('completion_notes', '')
        
        work_order.status = 'completed'
        work_order.actual_completion_date = timezone.now().date()
        work_order.completion_notes = completion_notes
        work_order.save()
        
        # Check if all work orders for the maintenance request are completed
        maintenance_request = work_order.maintenance_request
        all_work_orders = maintenance_request.work_orders.all()
        
        if all(wo.status == 'completed' for wo in all_work_orders):
            maintenance_request.status = 'completed'
            maintenance_request.completion_date = timezone.now().date()
            maintenance_request.save()
        
        serializer = WorkOrderSerializer(work_order, context={'request': request})
        return Response(serializer.data)
