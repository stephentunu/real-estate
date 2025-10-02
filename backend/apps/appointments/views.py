from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import models
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, timedelta
from .models import Appointment, AppointmentType, AppointmentReminder
from .serializers import (
    AppointmentTypeSerializer, AppointmentTypeCreateUpdateSerializer,
    AppointmentListSerializer, AppointmentDetailSerializer,
    AppointmentCreateUpdateSerializer, AppointmentRescheduleSerializer,
    AppointmentCancelSerializer, AppointmentCompleteSerializer,
    AppointmentReminderSerializer, AppointmentStatsSerializer,
    AgentAvailabilitySerializer
)
from apps.core.permissions import IsOwnerOrReadOnly
from django_filters import FilterSet


class AppointmentTypeFilter(FilterSet):
    """
    Filter for AppointmentType
    """
    
    class Meta:
        model = AppointmentType
        fields = {
            'name': ['icontains'],
            'is_active': ['exact'],
            'requires_property': ['exact'],
            'duration_minutes': ['exact', 'gte', 'lte'],
        }


class AppointmentTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing appointment types
    """
    
    queryset = AppointmentType.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = AppointmentTypeFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'duration_minutes', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ['create', 'update', 'partial_update']:
            return AppointmentTypeCreateUpdateSerializer
        return AppointmentTypeSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        
        # Add annotation for appointment counts
        queryset = queryset.annotate(
            appointment_count=Count('appointments'),
            active_appointment_count=Count(
                'appointments',
                filter=Q(appointments__status__in=['pending', 'confirmed'])
            )
        )
        
        # Filter active types for non-staff users
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set created_by when creating"""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Set updated_by when updating"""
        serializer.save(updated_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active appointment types"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle active status of appointment type"""
        appointment_type = self.get_object()
        appointment_type.is_active = not appointment_type.is_active
        appointment_type.updated_by = request.user
        appointment_type.save()
        
        serializer = self.get_serializer(appointment_type)
        return Response(serializer.data)


class AppointmentFilter(FilterSet):
    """
    Filter for Appointment
    """
    
    class Meta:
        model = Appointment
        fields = {
            'appointment_type': ['exact'],
            'client': ['exact'],
            'agent': ['exact'],
            'property_ref': ['exact'],
            'status': ['exact', 'in'],
            'priority': ['exact', 'in'],
            'scheduled_date': ['exact', 'gte', 'lte'],
            'created_at': ['date', 'date__gte', 'date__lte'],
        }


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing appointments
    """
    
    queryset = Appointment.objects.select_related(
        'appointment_type', 'client', 'agent', 'cancelled_by'
    ).prefetch_related('reminders')
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = AppointmentFilter
    search_fields = ['title', 'description', 'client__username', 'agent__username']
    ordering_fields = ['scheduled_date', 'scheduled_time', 'created_at', 'priority']
    ordering = ['-scheduled_date', '-scheduled_time']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ['create', 'update', 'partial_update']:
            return AppointmentCreateUpdateSerializer
        elif self.action == 'retrieve':
            return AppointmentDetailSerializer
        elif self.action == 'reschedule':
            return AppointmentRescheduleSerializer
        elif self.action == 'cancel':
            return AppointmentCancelSerializer
        elif self.action == 'complete':
            return AppointmentCompleteSerializer
        return AppointmentListSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if not user.is_authenticated:
            return queryset.none()

        # Filter based on user role
        if user.is_staff or user.is_superuser:
            # Staff can see all appointments
            pass
        elif hasattr(user, 'agent_profile'):
            # Agents can see their own appointments
            queryset = queryset.filter(agent=user)
        else:
            # Clients can see their own appointments
            queryset = queryset.filter(client=user)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set created_by when creating"""
        # If no client specified and user is not staff, set client to current user
        if not serializer.validated_data.get('client') and not self.request.user.is_staff:
            serializer.validated_data['client'] = self.request.user
        
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Set updated_by when updating"""
        serializer.save(updated_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_appointments(self, request):
        """Get current user's appointments"""
        user = request.user
        
        if hasattr(user, 'agent_profile'):
            queryset = self.get_queryset().filter(agent=user)
        else:
            queryset = self.get_queryset().filter(client=user)
        
        # Apply filters
        queryset = self.filter_queryset(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's appointments"""
        today = timezone.now().date()
        queryset = self.get_queryset().filter(scheduled_date=today)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming appointments"""
        now = timezone.now()
        queryset = self.get_queryset().filter(
            scheduled_date__gte=now.date(),
            status__in=['pending', 'confirmed']
        )
        
        # If it's today, filter by time as well
        today_appointments = queryset.filter(scheduled_date=now.date())
        future_appointments = queryset.filter(scheduled_date__gt=now.date())
        
        # For today's appointments, only include those in the future
        today_future = today_appointments.filter(scheduled_time__gt=now.time())
        
        # Combine querysets
        final_queryset = today_future.union(future_appointments)
        
        serializer = self.get_serializer(final_queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def past(self, request):
        """Get past appointments"""
        now = timezone.now()
        queryset = self.get_queryset().filter(
            models.Q(scheduled_date__lt=now.date()) |
            models.Q(
                scheduled_date=now.date(),
                scheduled_time__lt=now.time()
            )
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Get appointments by status"""
        status_param = request.query_params.get('status')
        if not status_param:
            return Response(
                {'error': 'Status parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(status=status_param)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
        """Reschedule an appointment"""
        appointment = self.get_object()
        
        # Check if appointment can be rescheduled
        if not appointment.can_be_rescheduled:
            return Response(
                {'error': 'This appointment cannot be rescheduled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Create new appointment with new datetime
            new_appointment = Appointment.objects.create(
                title=appointment.title,
                description=appointment.description,
                appointment_type=appointment.appointment_type,
                client=appointment.client,
                agent=appointment.agent,
                property=appointment.property,
                scheduled_date=serializer.validated_data['new_date'],
                scheduled_time=serializer.validated_data['new_time'],
                duration_minutes=appointment.duration_minutes,
                timezone=appointment.timezone,
                priority=appointment.priority,
                client_phone=appointment.client_phone,
                client_email=appointment.client_email,
                meeting_location=appointment.meeting_location,
                meeting_link=appointment.meeting_link,
                agent_notes=appointment.agent_notes,
                client_notes=appointment.client_notes,
                original_appointment=appointment.original_appointment or appointment,
                reschedule_count=(appointment.reschedule_count or 0) + 1,
                created_by=request.user
            )
            
            # Cancel original appointment
            appointment.status = 'cancelled'
            appointment.cancelled_at = timezone.now()
            appointment.cancelled_by = request.user
            appointment.cancellation_reason = serializer.validated_data.get(
                'reason', 'Rescheduled'
            )
            appointment.updated_by = request.user
            appointment.save()
            
            # Return new appointment
            response_serializer = AppointmentDetailSerializer(new_appointment)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an appointment"""
        appointment = self.get_object()
        
        # Check if appointment can be cancelled
        if not appointment.can_be_cancelled:
            return Response(
                {'error': 'This appointment cannot be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            appointment.status = 'cancelled'
            appointment.cancelled_at = timezone.now()
            appointment.cancelled_by = request.user
            appointment.cancellation_reason = serializer.validated_data.get('reason', '')
            appointment.updated_by = request.user
            appointment.save()
            
            response_serializer = AppointmentDetailSerializer(appointment)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm an appointment"""
        appointment = self.get_object()
        
        if appointment.status != 'pending':
            return Response(
                {'error': 'Only pending appointments can be confirmed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = 'confirmed'
        appointment.updated_by = request.user
        appointment.save()
        
        serializer = AppointmentDetailSerializer(appointment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark appointment as completed"""
        appointment = self.get_object()
        
        if appointment.status not in ['confirmed', 'in_progress']:
            return Response(
                {'error': 'Only confirmed or in-progress appointments can be completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            appointment.status = 'completed'
            appointment.completion_notes = serializer.validated_data.get('completion_notes', '')
            appointment.updated_by = request.user
            appointment.save()
            
            response_serializer = AppointmentDetailSerializer(appointment)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get appointment statistics"""
        queryset = self.get_queryset()
        
        # Basic counts
        total_appointments = queryset.count()
        pending_appointments = queryset.filter(status='pending').count()
        confirmed_appointments = queryset.filter(status='confirmed').count()
        completed_appointments = queryset.filter(status='completed').count()
        cancelled_appointments = queryset.filter(status='cancelled').count()
        
        # Today's appointments
        today = timezone.now().date()
        today_appointments = queryset.filter(scheduled_date=today).count()
        
        # Upcoming appointments
        now = timezone.now()
        upcoming_appointments = queryset.filter(
            models.Q(scheduled_date__gt=now.date()) |
            models.Q(
                scheduled_date=now.date(),
                scheduled_time__gt=now.time()
            ),
            status__in=['pending', 'confirmed']
        ).count()
        
        # Overdue appointments
        overdue_appointments = queryset.filter(
            models.Q(scheduled_date__lt=now.date()) |
            models.Q(
                scheduled_date=now.date(),
                scheduled_time__lt=now.time()
            ),
            status__in=['pending', 'confirmed']
        ).count()
        
        # Status breakdown
        status_breakdown = dict(
            queryset.values('status').annotate(count=Count('id')).values_list('status', 'count')
        )
        
        # Type breakdown
        type_breakdown = dict(
            queryset.values('appointment_type__name').annotate(
                count=Count('id')
            ).values_list('appointment_type__name', 'count')
        )
        
        # Agent breakdown (if user is staff)
        agent_breakdown = {}
        if request.user.is_staff:
            agent_breakdown = dict(
                queryset.values('agent__username').annotate(
                    count=Count('id')
                ).values_list('agent__username', 'count')
            )
        
        # Monthly trends (last 12 months)
        monthly_trends = []
        for i in range(12):
            month_start = (timezone.now() - timedelta(days=30*i)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            month_count = queryset.filter(
                scheduled_date__gte=month_start.date(),
                scheduled_date__lte=month_end.date()
            ).count()
            
            monthly_trends.append({
                'month': month_start.strftime('%Y-%m'),
                'count': month_count
            })
        
        monthly_trends.reverse()
        
        stats_data = {
            'total_appointments': total_appointments,
            'pending_appointments': pending_appointments,
            'confirmed_appointments': confirmed_appointments,
            'completed_appointments': completed_appointments,
            'cancelled_appointments': cancelled_appointments,
            'today_appointments': today_appointments,
            'upcoming_appointments': upcoming_appointments,
            'overdue_appointments': overdue_appointments,
            'status_breakdown': status_breakdown,
            'type_breakdown': type_breakdown,
            'agent_breakdown': agent_breakdown,
            'monthly_trends': monthly_trends,
        }
        
        serializer = AppointmentStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def check_availability(self, request):
        """Check agent availability for a specific date/time"""
        serializer = AgentAvailabilitySerializer(data=request.data)
        if serializer.is_valid():
            agent_id = serializer.validated_data['agent_id']
            check_date = serializer.validated_data['date']
            start_time = serializer.validated_data.get('start_time')
            end_time = serializer.validated_data.get('end_time')
            
            # Get agent's appointments for the date
            agent_appointments = Appointment.objects.filter(
                agent_id=agent_id,
                scheduled_date=check_date,
                status__in=['pending', 'confirmed']
            ).order_by('scheduled_time')
            
            # Generate busy slots
            busy_slots = []
            for appointment in agent_appointments:
                busy_slots.append({
                    'start_time': appointment.scheduled_time.strftime('%H:%M'),
                    'end_time': appointment.end_datetime.time().strftime('%H:%M'),
                    'appointment_id': appointment.id,
                    'title': appointment.title
                })
            
            # Generate available slots (simplified - assumes 9 AM to 6 PM working hours)
            available_slots = []
            work_start = datetime.strptime('09:00', '%H:%M').time()
            work_end = datetime.strptime('18:00', '%H:%M').time()
            
            # This is a simplified implementation
            # In a real application, you'd want to consider:
            # - Agent's working hours
            # - Break times
            # - Buffer time between appointments
            # - Minimum appointment duration
            
            current_time = work_start
            slot_duration = timedelta(minutes=30)  # 30-minute slots
            
            while current_time < work_end:
                slot_end = (datetime.combine(check_date, current_time) + slot_duration).time()
                if slot_end > work_end:
                    break
                
                # Check if this slot conflicts with any appointment
                is_available = True
                for appointment in agent_appointments:
                    if (current_time < appointment.end_datetime.time() and
                        slot_end > appointment.scheduled_time):
                        is_available = False
                        break
                
                if is_available:
                    available_slots.append({
                        'start_time': current_time.strftime('%H:%M'),
                        'end_time': slot_end.strftime('%H:%M')
                    })
                
                current_time = slot_end
            
            response_data = serializer.validated_data.copy()
            response_data['available_slots'] = available_slots
            response_data['busy_slots'] = busy_slots
            
            response_serializer = AgentAvailabilitySerializer(response_data)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppointmentReminderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing appointment reminders
    """
    
    queryset = AppointmentReminder.objects.select_related('appointment')
    serializer_class = AppointmentReminderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['appointment', 'reminder_type', 'is_sent']
    search_fields = ['subject', 'message']
    ordering_fields = ['scheduled_for', 'created_at']
    ordering = ['-scheduled_for']
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if not user.is_authenticated:
            return queryset.none()
            
        # Filter based on user role
        if user.is_staff or user.is_superuser:
            # Staff can see all reminders
            pass
        elif hasattr(user, 'agent_profile'):
            # Agents can see reminders for their appointments
            queryset = queryset.filter(appointment__agent=user)
        else:
            # Clients can see reminders for their appointments
            queryset = queryset.filter(appointment__client=user)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set created_by when creating"""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Set updated_by when updating"""
        serializer.save(updated_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending reminders"""
        queryset = self.get_queryset().filter(
            is_sent=False,
            scheduled_for__lte=timezone.now()
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_sent(self, request, pk=None):
        """Mark reminder as sent"""
        reminder = self.get_object()
        reminder.is_sent = True
        reminder.sent_at = timezone.now()
        reminder.save()
        
        serializer = self.get_serializer(reminder)
        return Response(serializer.data)
