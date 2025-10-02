from celery import shared_task
from django.core.management import call_command
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, name='apps.core.tasks.cleanup_soft_deleted_records')
def cleanup_soft_deleted_records(self, dry_run=False, specific_model=None, override_days=None):
    """
    Celery task to cleanup soft-deleted records based on retention policies.
    
    Args:
        dry_run (bool): If True, only show what would be deleted
        specific_model (str): Specific model to cleanup (e.g., 'properties.Property')
        override_days (int): Override default retention days
    
    Returns:
        dict: Task result with cleanup statistics
    """
    try:
        logger.info(f"Starting cleanup task {'(DRY RUN)' if dry_run else '(LIVE)'}")
        
        # Prepare command arguments
        cmd_args = []
        cmd_kwargs = {}
        
        if dry_run:
            cmd_kwargs['dry_run'] = True
        
        if specific_model:
            cmd_kwargs['model'] = specific_model
        
        if override_days:
            cmd_kwargs['days'] = override_days
        
        # Execute cleanup command
        call_command('cleanup_soft_deleted', *cmd_args, **cmd_kwargs)
        
        result = {
            'status': 'success',
            'message': 'Cleanup completed successfully',
            'dry_run': dry_run,
            'specific_model': specific_model,
            'override_days': override_days,
            'completed_at': timezone.now().isoformat()
        }
        
        logger.info(f"Cleanup task completed: {result}")
        return result
        
    except Exception as exc:
        logger.error(f"Cleanup task failed: {exc}")
        
        # Retry the task up to 3 times with exponential backoff
        if self.request.retries < 3:
            logger.info(f"Retrying cleanup task (attempt {self.request.retries + 1}/3)")
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        
        return {
            'status': 'error',
            'message': str(exc),
            'dry_run': dry_run,
            'specific_model': specific_model,
            'override_days': override_days,
            'failed_at': timezone.now().isoformat()
        }


@shared_task(name='apps.core.tasks.generate_cleanup_report')
def generate_cleanup_report():
    """
    Generate a report of soft-deleted records and their retention status.
    
    Returns:
        dict: Report with statistics for each model
    """
    try:
        from django.apps import apps
        from apps.core.mixins import SoftDeleteMixin
        from datetime import timedelta
        from django.conf import settings
        
        logger.info("Generating cleanup report")
        
        report = {
            'generated_at': timezone.now().isoformat(),
            'models': {},
            'summary': {
                'total_soft_deleted': 0,
                'ready_for_cleanup': 0,
                'retention_policies': 0
            }
        }
        
        # Get retention policies
        retention_policies = getattr(settings, 'SOFT_DELETE_RETENTION_POLICIES', {})
        report['summary']['retention_policies'] = len(retention_policies)
        
        # Analyze each model with SoftDeleteMixin
        for model in apps.get_models():
            if not issubclass(model, SoftDeleteMixin):
                continue
            
            model_name = f"{model._meta.app_label}.{model._meta.model_name}"
            
            # Get retention days
            retention_days = _get_model_retention_days(model, retention_policies)
            
            # Count soft-deleted records
            soft_deleted_count = model.objects.filter(is_deleted=True).count()
            
            # Count records ready for cleanup
            ready_for_cleanup = 0
            if retention_days and soft_deleted_count > 0:
                cutoff_date = timezone.now() - timedelta(days=retention_days)
                ready_for_cleanup = model.objects.filter(
                    is_deleted=True,
                    deleted_at__lt=cutoff_date
                ).count()
            
            report['models'][model_name] = {
                'retention_days': retention_days,
                'soft_deleted_count': soft_deleted_count,
                'ready_for_cleanup': ready_for_cleanup,
                'has_retention_policy': retention_days is not None
            }
            
            # Update summary
            report['summary']['total_soft_deleted'] += soft_deleted_count
            report['summary']['ready_for_cleanup'] += ready_for_cleanup
        
        logger.info(f"Cleanup report generated: {report['summary']}")
        return report
        
    except Exception as exc:
        logger.error(f"Failed to generate cleanup report: {exc}")
        return {
            'status': 'error',
            'message': str(exc),
            'generated_at': timezone.now().isoformat()
        }


def _get_model_retention_days(model, retention_policies):
    """
    Helper function to get retention days for a model.
    """
    # Check if model has retention policy defined
    if hasattr(model, 'RETENTION_DAYS'):
        return model.RETENTION_DAYS
    
    # Check model meta for retention policy
    if hasattr(model._meta, 'retention_days'):
        return model._meta.retention_days
    
    # Check settings for model-specific retention
    model_key = f"{model._meta.app_label}.{model._meta.model_name}"
    
    if model_key in retention_policies:
        return retention_policies[model_key]
    
    # Check for app-level default
    app_key = model._meta.app_label
    if app_key in retention_policies:
        return retention_policies[app_key]
    
    # Check for global default
    if 'default' in retention_policies:
        return retention_policies['default']
    
    return None


@shared_task(name='apps.core.tasks.scheduled_cleanup')
def scheduled_cleanup():
    """
    Scheduled task that runs daily cleanup with reporting.
    This is the main task that should be scheduled in production.
    
    Returns:
        dict: Combined result of report generation and cleanup
    """
    try:
        logger.info("Starting scheduled cleanup with reporting")
        
        # Generate report first
        report = generate_cleanup_report()
        
        # Run cleanup (not dry run)
        cleanup_result = cleanup_soft_deleted_records.delay(dry_run=False)
        
        result = {
            'status': 'success',
            'report': report,
            'cleanup_task_id': cleanup_result.id,
            'scheduled_at': timezone.now().isoformat()
        }
        
        logger.info(f"Scheduled cleanup initiated: {result}")
        return result
        
    except Exception as exc:
        logger.error(f"Scheduled cleanup failed: {exc}")
        return {
            'status': 'error',
            'message': str(exc),
            'scheduled_at': timezone.now().isoformat()
        }