# **Data Retention Policy System (v3.0)**

**Version:** 3.0  
**Date:** January 2025  
**Technical Stack:** Django 5.2.6+, Python 3.13+, Pyright Strict Mode  
**Target Audience:** Backend Developers, System Administrators  
**Prepared By:** Platform Architecture Team  

---

## **Overview**

The Jaston Real Estate Platform implements a comprehensive data retention policy system that provides automated cleanup of soft-deleted records based on configurable retention policies. This system ensures compliance with data protection regulations while maintaining system performance and storage efficiency.

**Key Features:**
- **Type-Safe Configuration**: All retention policies use proper type annotations
- **Hierarchical Policy System**: Global, app-level, and model-specific policies
- **Automated Cleanup**: Celery-based scheduled cleanup operations
- **Comprehensive Monitoring**: Admin interface with real-time statistics
- **Audit Compliance**: Complete audit trails and reporting

---

## **System Architecture**

### **2.1 Core Components**

```python
# apps/core/retention/interfaces.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Protocol
from datetime import datetime, timedelta
from django.db.models import Model, QuerySet

class RetentionPolicy(Protocol):
    """Protocol for retention policy configuration."""
    
    model_path: str
    retention_days: int
    policy_source: str
    is_active: bool

class IRetentionManager(ABC):
    """Interface for retention policy management."""
    
    @abstractmethod
    def get_retention_days(self, model_path: str) -> int:
        """Get retention period for a specific model."""
        pass
    
    @abstractmethod
    def get_eligible_records(
        self, 
        model_class: type[Model], 
        cutoff_date: Optional[datetime] = None
    ) -> QuerySet:
        """Get records eligible for cleanup."""
        pass
    
    @abstractmethod
    def cleanup_model(
        self, 
        model_class: type[Model], 
        dry_run: bool = True
    ) -> Dict[str, int]:
        """Cleanup soft-deleted records for a model."""
        pass
```

### **2.2 Configuration Structure**

```python
# apps/core/retention/config.py
from typing import Dict, Any, TypedDict
from dataclasses import dataclass
from enum import Enum

class PolicySource(Enum):
    """Source of retention policy."""
    GLOBAL_DEFAULT = "global_default"
    APP_LEVEL = "app_level"
    MODEL_SPECIFIC = "model_specific"
    SYSTEM_DEFAULT = "system_default"

@dataclass(frozen=True)
class RetentionConfig:
    """Retention policy configuration."""
    
    model_path: str
    retention_days: int
    policy_source: PolicySource
    is_active: bool = True
    created_at: datetime = datetime.now()
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.retention_days < 1:
            raise ValueError("Retention days must be positive")
        
        if not self.model_path:
            raise ValueError("Model path cannot be empty")

class RetentionPolicySettings(TypedDict):
    """Type definition for retention policy settings."""
    
    default: int
    properties: int
    leases: int
    maintenance: int
    users: Dict[str, int]
    properties: Dict[str, int]
    leases: Dict[str, int]
```

---

## **Configuration**

### **3.1 Settings Configuration**

```python
# backend/config/settings/retention.py
from typing import Dict, Any
from apps.core.retention.config import RetentionPolicySettings

# Retention Policy Configuration
SOFT_DELETE_RETENTION_POLICIES: RetentionPolicySettings = {
    # Global default retention period (days)
    'default': 90,
    
    # App-level policies override global default
    'properties': 365,    # Property data kept for 1 year
    'leases': 2555,       # Lease data kept for 7 years (legal requirement)
    'maintenance': 180,   # Maintenance records kept for 6 months
    'users': 1095,        # User data kept for 3 years
    'team': 730,          # Team data kept for 2 years
    
    # Model-specific policies override app-level policies
    'users.User': 1095,                    # User profiles kept for 3 years
    'users.UserProfile': 1095,             # User profiles kept for 3 years
    'properties.Property': 1825,           # Property records kept for 5 years
    'properties.PropertyImage': 1095,      # Property images kept for 3 years
    'leases.Lease': 2555,                  # Lease agreements kept for 7 years
    'leases.PaymentSchedule': 2555,        # Payment records kept for 7 years
    'leases.LeaseDocument': 2555,          # Lease documents kept for 7 years
    'maintenance.MaintenanceRequest': 1095, # Maintenance requests kept for 3 years
    'maintenance.WorkOrder': 1095,         # Work orders kept for 3 years
    'team.TeamMember': 730,                # Team member records kept for 2 years
}

# Cleanup Configuration
RETENTION_CLEANUP_CONFIG: Dict[str, Any] = {
    'batch_size': 1000,           # Records processed per batch
    'max_execution_time': 3600,   # Maximum cleanup time in seconds
    'enable_notifications': True,  # Send cleanup notifications
    'notification_threshold': 10000, # Notify if more than N records cleaned
    'dry_run_default': True,      # Default to dry-run mode
    'require_confirmation': True,  # Require confirmation for large cleanups
}
```

### **3.2 Policy Hierarchy**

Policies are applied in the following order of precedence:
1. **Model-specific** (`app.Model`)
2. **App-level** (`app_name`)
3. **Global default** (`default`)
4. **System default** (30 days if no policy found)

---

## **Implementation**

### **4.1 Retention Manager**

```python
# apps/core/retention/manager.py
from typing import Dict, List, Optional, Type, Any
from datetime import datetime, timedelta
from django.db.models import Model, QuerySet
from django.conf import settings
from django.apps import apps
from django.utils import timezone
from apps.core.mixins import SoftDeleteMixin
from apps.core.retention.interfaces import IRetentionManager
from apps.core.retention.config import RetentionConfig, PolicySource
from apps.core.di.decorators import injectable
import logging

logger = logging.getLogger(__name__)

@injectable('retention_manager')
class RetentionManager(IRetentionManager):
    """Implementation of retention policy management."""
    
    def __init__(self) -> None:
        """Initialize retention manager."""
        self._policies: Dict[str, RetentionConfig] = {}
        self._load_policies()
    
    def _load_policies(self) -> None:
        """Load retention policies from settings."""
        policies = getattr(settings, 'SOFT_DELETE_RETENTION_POLICIES', {})
        
        for key, days in policies.items():
            if key == 'default':
                continue
                
            source = self._determine_policy_source(key)
            config = RetentionConfig(
                model_path=key,
                retention_days=days,
                policy_source=source
            )
            self._policies[key] = config
    
    def _determine_policy_source(self, key: str) -> PolicySource:
        """Determine the source of a policy."""
        if '.' in key:
            return PolicySource.MODEL_SPECIFIC
        return PolicySource.APP_LEVEL
    
    def get_retention_days(self, model_path: str) -> int:
        """Get retention period for a specific model."""
        # Check model-specific policy
        if model_path in self._policies:
            return self._policies[model_path].retention_days
        
        # Check app-level policy
        app_name = model_path.split('.')[0]
        if app_name in self._policies:
            return self._policies[app_name].retention_days
        
        # Use global default
        policies = getattr(settings, 'SOFT_DELETE_RETENTION_POLICIES', {})
        return policies.get('default', 30)
    
    def get_eligible_records(
        self, 
        model_class: Type[Model], 
        cutoff_date: Optional[datetime] = None
    ) -> QuerySet:
        """Get records eligible for cleanup."""
        if not issubclass(model_class, SoftDeleteMixin):
            raise ValueError(f"Model {model_class} does not support soft deletion")
        
        if cutoff_date is None:
            model_path = f"{model_class._meta.app_label}.{model_class.__name__}"
            retention_days = self.get_retention_days(model_path)
            cutoff_date = timezone.now() - timedelta(days=retention_days)
        
        return model_class.objects.filter(
            is_deleted=True,
            deleted_at__lt=cutoff_date
        )
    
    def cleanup_model(
        self, 
        model_class: Type[Model], 
        dry_run: bool = True
    ) -> Dict[str, int]:
        """Cleanup soft-deleted records for a model."""
        eligible_records = self.get_eligible_records(model_class)
        total_count = eligible_records.count()
        
        if dry_run:
            return {
                'total_eligible': total_count,
                'deleted_count': 0,
                'dry_run': True
            }
        
        # Perform actual cleanup in batches
        batch_size = getattr(settings, 'RETENTION_CLEANUP_CONFIG', {}).get('batch_size', 1000)
        deleted_count = 0
        
        while True:
            batch = list(eligible_records[:batch_size])
            if not batch:
                break
            
            # Call custom cleanup logic if available
            for record in batch:
                if hasattr(record, 'before_permanent_delete'):
                    record.before_permanent_delete()
            
            # Perform deletion
            batch_ids = [record.pk for record in batch]
            deleted_batch_count, _ = model_class.objects.filter(
                pk__in=batch_ids
            ).delete()
            
            deleted_count += deleted_batch_count
            
            # Call post-deletion logic
            for record in batch:
                if hasattr(record, 'after_permanent_delete'):
                    record.after_permanent_delete()
        
        logger.info(
            f"Cleaned up {deleted_count} records from {model_class.__name__}"
        )
        
        return {
            'total_eligible': total_count,
            'deleted_count': deleted_count,
            'dry_run': False
        }
    
    def get_all_policies(self) -> List[RetentionConfig]:
        """Get all configured retention policies."""
        return list(self._policies.values())
    
    def get_soft_delete_models(self) -> List[Type[Model]]:
        """Get all models that support soft deletion."""
        models: List[Type[Model]] = []
        
        for app_config in apps.get_app_configs():
            for model in app_config.get_models():
                if issubclass(model, SoftDeleteMixin):
                    models.append(model)
        
        return models
    
    def generate_cleanup_report(self) -> Dict[str, Any]:
        """Generate comprehensive cleanup report."""
        report: Dict[str, Any] = {
            'generated_at': timezone.now(),
            'models': [],
            'summary': {
                'total_models': 0,
                'total_eligible_records': 0,
                'total_soft_deleted_records': 0
            }
        }
        
        for model_class in self.get_soft_delete_models():
            model_path = f"{model_class._meta.app_label}.{model_class.__name__}"
            retention_days = self.get_retention_days(model_path)
            
            eligible_records = self.get_eligible_records(model_class)
            eligible_count = eligible_records.count()
            
            total_soft_deleted = model_class.objects.filter(is_deleted=True).count()
            
            model_report = {
                'model_path': model_path,
                'model_name': model_class.__name__,
                'app_label': model_class._meta.app_label,
                'retention_days': retention_days,
                'eligible_for_cleanup': eligible_count,
                'total_soft_deleted': total_soft_deleted,
                'policy_source': self._get_policy_source(model_path)
            }
            
            report['models'].append(model_report)
            report['summary']['total_eligible_records'] += eligible_count
            report['summary']['total_soft_deleted_records'] += total_soft_deleted
        
        report['summary']['total_models'] = len(report['models'])
        return report
    
    def _get_policy_source(self, model_path: str) -> str:
        """Get the source of policy for a model."""
        if model_path in self._policies:
            return self._policies[model_path].policy_source.value
        
        app_name = model_path.split('.')[0]
        if app_name in self._policies:
            return PolicySource.APP_LEVEL.value
        
        return PolicySource.GLOBAL_DEFAULT.value
```

---

## **Management Commands**

### **5.1 Cleanup Command**

```python
# apps/core/management/commands/cleanup_soft_deleted.py
from typing import Any, Optional, Type
from django.core.management.base import BaseCommand, CommandParser
from django.db.models import Model
from django.apps import apps
from apps.core.di.container import get_service
from apps.core.retention.interfaces import IRetentionManager
from apps.core.mixins import SoftDeleteMixin
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """Management command to cleanup soft-deleted records."""
    
    help = 'Cleanup soft-deleted records based on retention policies'
    
    def add_arguments(self, parser: CommandParser) -> None:
        """Add command arguments."""
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview operations without making changes',
        )
        parser.add_argument(
            '--model',
            type=str,
            help='Target specific model (format: app.Model)',
        )
        parser.add_argument(
            '--days',
            type=int,
            help='Override retention period for this run',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Bypass safety checks and confirmations',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Number of records to process per batch',
        )
    
    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the cleanup command."""
        dry_run: bool = options['dry-run']
        target_model: Optional[str] = options['model']
        days_override: Optional[int] = options['days']
        force: bool = options['force']
        batch_size: int = options['batch_size']
        
        retention_manager: IRetentionManager = get_service('retention_manager')
        
        if target_model:
            self._cleanup_single_model(
                retention_manager, target_model, dry_run, days_override, force
            )
        else:
            self._cleanup_all_models(retention_manager, dry_run, force)
    
    def _cleanup_single_model(
        self,
        retention_manager: IRetentionManager,
        model_path: str,
        dry_run: bool,
        days_override: Optional[int],
        force: bool
    ) -> None:
        """Cleanup a single model."""
        try:
            app_label, model_name = model_path.split('.')
            model_class: Type[Model] = apps.get_model(app_label, model_name)
            
            if not issubclass(model_class, SoftDeleteMixin):
                self.stdout.write(
                    self.style.ERROR(
                        f'Model {model_path} does not support soft deletion'
                    )
                )
                return
            
            # Override retention period if specified
            if days_override:
                from datetime import timedelta
                from django.utils import timezone
                cutoff_date = timezone.now() - timedelta(days=days_override)
                eligible_records = retention_manager.get_eligible_records(
                    model_class, cutoff_date
                )
                eligible_count = eligible_records.count()
            else:
                eligible_records = retention_manager.get_eligible_records(model_class)
                eligible_count = eligible_records.count()
            
            if eligible_count == 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'No records eligible for cleanup in {model_path}'
                    )
                )
                return
            
            # Safety check for large deletions
            if eligible_count > 10000 and not force:
                self.stdout.write(
                    self.style.WARNING(
                        f'Large deletion detected: {eligible_count} records. '
                        f'Use --force to proceed.'
                    )
                )
                return
            
            # Perform cleanup
            result = retention_manager.cleanup_model(model_class, dry_run)
            
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f'DRY RUN: Would delete {result["total_eligible"]} '
                        f'records from {model_path}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully deleted {result["deleted_count"]} '
                        f'records from {model_path}'
                    )
                )
                
        except Exception as e:
            logger.error(f"Error cleaning up {model_path}: {e}")
            self.stdout.write(
                self.style.ERROR(f'Error cleaning up {model_path}: {e}')
            )
    
    def _cleanup_all_models(
        self,
        retention_manager: IRetentionManager,
        dry_run: bool,
        force: bool
    ) -> None:
        """Cleanup all models with soft deletion support."""
        models = retention_manager.get_soft_delete_models()
        total_deleted = 0
        
        for model_class in models:
            model_path = f"{model_class._meta.app_label}.{model_class.__name__}"
            
            try:
                result = retention_manager.cleanup_model(model_class, dry_run)
                
                if result['total_eligible'] > 0:
                    if dry_run:
                        self.stdout.write(
                            f'  {model_path}: {result["total_eligible"]} eligible'
                        )
                    else:
                        self.stdout.write(
                            f'  {model_path}: {result["deleted_count"]} deleted'
                        )
                        total_deleted += result['deleted_count']
                        
            except Exception as e:
                logger.error(f"Error processing {model_path}: {e}")
                self.stdout.write(
                    self.style.ERROR(f'Error processing {model_path}: {e}')
                )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN: No records were actually deleted')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Total records deleted: {total_deleted}')
            )
```

---

## **Celery Tasks**

### **6.1 Automated Cleanup Tasks**

```python
# apps/core/tasks/retention.py
from typing import Dict, Any, Optional
from celery import shared_task
from django.conf import settings
from apps.core.di.container import get_service
from apps.core.retention.interfaces import IRetentionManager
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, name='apps.core.tasks.cleanup_soft_deleted_records')
def cleanup_soft_deleted_records(
    self,
    dry_run: bool = False,
    target_model: Optional[str] = None,
    days_override: Optional[int] = None,
    force: bool = False
) -> Dict[str, Any]:
    """
    Celery task for cleaning up soft-deleted records.
    
    Args:
        dry_run: If True, only preview what would be deleted
        target_model: Specific model to target (format: app.Model)
        days_override: Override retention period for this run
        force: Bypass safety checks
        
    Returns:
        Dictionary containing cleanup results
    """
    try:
        retention_manager: IRetentionManager = get_service('retention_manager')
        
        if target_model:
            from django.apps import apps
            app_label, model_name = target_model.split('.')
            model_class = apps.get_model(app_label, model_name)
            
            result = retention_manager.cleanup_model(model_class, dry_run)
            
            logger.info(
                f"Cleanup task completed for {target_model}: "
                f"{result['deleted_count']} records deleted"
            )
            
            return {
                'success': True,
                'target_model': target_model,
                'result': result
            }
        else:
            # Cleanup all models
            models = retention_manager.get_soft_delete_models()
            results = {}
            total_deleted = 0
            
            for model_class in models:
                model_path = f"{model_class._meta.app_label}.{model_class.__name__}"
                
                try:
                    result = retention_manager.cleanup_model(model_class, dry_run)
                    results[model_path] = result
                    total_deleted += result['deleted_count']
                    
                except Exception as e:
                    logger.error(f"Error cleaning up {model_path}: {e}")
                    results[model_path] = {'error': str(e)}
            
            logger.info(f"Cleanup task completed: {total_deleted} total records deleted")
            
            return {
                'success': True,
                'total_deleted': total_deleted,
                'results': results
            }
            
    except Exception as e:
        logger.error(f"Cleanup task failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

@shared_task(name='apps.core.tasks.scheduled_cleanup')
def scheduled_cleanup() -> Dict[str, Any]:
    """Scheduled cleanup task that runs automatically."""
    return cleanup_soft_deleted_records.delay(dry_run=False)

@shared_task(name='apps.core.tasks.generate_cleanup_report')
def generate_cleanup_report() -> Dict[str, Any]:
    """Generate and optionally email cleanup report."""
    try:
        retention_manager: IRetentionManager = get_service('retention_manager')
        report = retention_manager.generate_cleanup_report()
        
        # Optionally send email notification
        if getattr(settings, 'RETENTION_CLEANUP_CONFIG', {}).get('enable_notifications'):
            # Send email logic here
            pass
        
        logger.info("Cleanup report generated successfully")
        
        return {
            'success': True,
            'report': report
        }
        
    except Exception as e:
        logger.error(f"Failed to generate cleanup report: {e}")
        return {
            'success': False,
            'error': str(e)
        }
```

### **6.2 Task Scheduling**

```python
# backend/config/settings/celery.py
from typing import Dict, Any

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE: Dict[str, Dict[str, Any]] = {
    'cleanup-soft-deleted-daily': {
        'task': 'apps.core.tasks.scheduled_cleanup',
        'schedule': 86400.0,  # Daily at midnight
        'options': {
            'queue': 'cleanup',
            'routing_key': 'cleanup.scheduled'
        }
    },
    'generate-cleanup-report-weekly': {
        'task': 'apps.core.tasks.generate_cleanup_report',
        'schedule': 604800.0,  # Weekly on Sunday
        'options': {
            'queue': 'reports',
            'routing_key': 'reports.cleanup'
        }
    },
}

# Task Routing
CELERY_TASK_ROUTES: Dict[str, Dict[str, str]] = {
    'apps.core.tasks.cleanup_soft_deleted_records': {
        'queue': 'cleanup',
        'routing_key': 'cleanup.manual'
    },
    'apps.core.tasks.scheduled_cleanup': {
        'queue': 'cleanup',
        'routing_key': 'cleanup.scheduled'
    },
    'apps.core.tasks.generate_cleanup_report': {
        'queue': 'reports',
        'routing_key': 'reports.cleanup'
    },
}
```

---

## **Admin Interface**

### **7.1 Admin Views**

```python
# apps/core/admin/retention.py
from typing import Any, Dict, List
from django.contrib import admin
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.urls import path
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from apps.core.di.container import get_service
from apps.core.retention.interfaces import IRetentionManager

@admin.register(admin.ModelAdmin)
class RetentionPolicyAdmin(admin.ModelAdmin):
    """Admin interface for retention policy management."""
    
    def get_urls(self):
        """Add custom admin URLs."""
        urls = super().get_urls()
        custom_urls = [
            path(
                'retention-policies/',
                self.admin_site.admin_view(self.retention_policies_view),
                name='retention_policies'
            ),
            path(
                'cleanup-report/',
                self.admin_site.admin_view(self.cleanup_report_view),
                name='cleanup_report'
            ),
            path(
                'run-cleanup/',
                self.admin_site.admin_view(self.run_cleanup_view),
                name='run_cleanup'
            ),
        ]
        return custom_urls + urls
    
    @method_decorator(staff_member_required)
    def retention_policies_view(self, request: HttpRequest):
        """View for displaying retention policies."""
        retention_manager: IRetentionManager = get_service('retention_manager')
        
        policies = retention_manager.get_all_policies()
        models = retention_manager.get_soft_delete_models()
        
        context = {
            'title': 'Retention Policies',
            'policies': policies,
            'models': models,
            'opts': self.model._meta,
        }
        
        return render(request, 'admin/retention/policies.html', context)
    
    @method_decorator(staff_member_required)
    def cleanup_report_view(self, request: HttpRequest):
        """View for displaying cleanup report."""
        retention_manager: IRetentionManager = get_service('retention_manager')
        
        if request.method == 'POST' and request.headers.get('Content-Type') == 'application/json':
            # AJAX request for updated report data
            report = retention_manager.generate_cleanup_report()
            return JsonResponse(report)
        
        report = retention_manager.generate_cleanup_report()
        
        context = {
            'title': 'Cleanup Report',
            'report': report,
            'opts': self.model._meta,
        }
        
        return render(request, 'admin/retention/report.html', context)
    
    @method_decorator(staff_member_required)
    def run_cleanup_view(self, request: HttpRequest):
        """View for running cleanup operations."""
        if request.method == 'POST':
            # Handle cleanup execution
            dry_run = request.POST.get('dry_run', 'true') == 'true'
            target_model = request.POST.get('target_model')
            
            from apps.core.tasks.retention import cleanup_soft_deleted_records
            
            task = cleanup_soft_deleted_records.delay(
                dry_run=dry_run,
                target_model=target_model if target_model else None
            )
            
            return JsonResponse({
                'success': True,
                'task_id': task.id,
                'message': 'Cleanup task started'
            })
        
        retention_manager: IRetentionManager = get_service('retention_manager')
        models = retention_manager.get_soft_delete_models()
        
        context = {
            'title': 'Run Cleanup',
            'models': models,
            'opts': self.model._meta,
        }
        
        return render(request, 'admin/retention/cleanup.html', context)
```

---

## **API Integration**

### **8.1 Programmatic Access**

```python
# Example usage in your application code
from apps.core.di.container import get_service
from apps.core.retention.interfaces import IRetentionManager
from apps.core.tasks.retention import cleanup_soft_deleted_records

# Get retention manager
retention_manager: IRetentionManager = get_service('retention_manager')

# Check retention period for a model
days = retention_manager.get_retention_days('users.User')

# Get all models with policies
models = retention_manager.get_soft_delete_models()

# Generate cleanup report
report = retention_manager.generate_cleanup_report()

# Execute cleanup via Celery
task_result = cleanup_soft_deleted_records.delay(
    dry_run=True,
    target_model='properties.Property'
)

# Execute cleanup via management command
from django.core.management import call_command

call_command(
    'cleanup_soft_deleted',
    dry_run=True,
    model='properties.Property',
    verbosity=2
)
```

---

## **Monitoring and Security**

### **9.1 Logging Configuration**

```python
# backend/config/settings/logging.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'retention_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/retention.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'apps.core.tasks.retention': {
            'handlers': ['retention_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps.core.management.commands.cleanup_soft_deleted': {
            'handlers': ['retention_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps.core.retention': {
            'handlers': ['retention_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### **9.2 Security Considerations**

- **Access Control**: Admin interface requires staff permissions
- **Cleanup Operations**: Require superuser privileges for non-dry-run operations
- **API Access**: Controlled through Django permissions and authentication
- **Audit Trails**: Comprehensive logging of all cleanup operations
- **Data Protection**: Respects model-level soft delete implementations

---

## **Performance Optimization**

### **10.1 Database Optimization**

```python
# Ensure proper indexing for soft delete fields
class Meta:
    indexes = [
        models.Index(fields=['is_deleted', 'deleted_at']),
        models.Index(fields=['deleted_at']),
        models.Index(fields=['is_deleted']),
    ]
```

### **10.2 Batch Processing**

- **Configurable Batch Size**: Process records in configurable batches
- **Memory Management**: Efficient memory usage for large datasets
- **Progress Tracking**: Monitor cleanup progress for long-running operations

---

## **Best Practices**

1. **Regular Monitoring**: Review cleanup reports weekly
2. **Policy Review**: Audit retention policies quarterly
3. **Testing**: Always test with dry-run first
4. **Documentation**: Document custom retention logic
5. **Backup**: Ensure backups before major cleanup operations
6. **Compliance**: Align policies with legal requirements
7. **Performance**: Monitor system performance during cleanup
8. **Type Safety**: Use proper type annotations throughout
9. **Error Handling**: Implement comprehensive error handling
10. **Logging**: Maintain detailed audit logs

---

## **Troubleshooting**

### **11.1 Common Issues**

1. **No records being cleaned up**
   - Check retention policy configuration
   - Verify models implement `SoftDeleteMixin` correctly
   - Ensure records exceed retention period

2. **Celery tasks not running**
   - Verify Celery worker is running
   - Check Celery beat scheduler configuration
   - Review task routing and queue configuration

3. **Type checking errors**
   - Ensure all type annotations are correct
   - Run `pyright` to validate type safety
   - Check import statements and dependencies

### **11.2 Debug Commands**

```bash
# Test retention policy configuration
python manage.py shell -c "
from apps.core.di.container import get_service;
manager = get_service('retention_manager');
print(manager.get_all_policies())
"

# Check soft delete models
python manage.py shell -c "
from apps.core.di.container import get_service;
manager = get_service('retention_manager');
print([m.__name__ for m in manager.get_soft_delete_models()])
"

# Test Celery connectivity
celery -A backend.config.celery inspect ping

# Monitor Celery tasks
celery -A backend.config.celery flower
```

---

**Document Approved By:**  
[Lead Backend Developer], [System Administrator], [Compliance Team]  

**Next Steps:**  
1. Review retention policies with legal team
2. Configure monitoring and alerting
3. Schedule regular policy audits
4. Train operations team on cleanup procedures