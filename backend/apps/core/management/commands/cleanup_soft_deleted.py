from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Management command to cleanup soft-deleted records based on retention policies.
    
    Usage:
        python manage.py cleanup_soft_deleted
        python manage.py cleanup_soft_deleted --dry-run
        python manage.py cleanup_soft_deleted --model properties.Property
        python manage.py cleanup_soft_deleted --days 90
    """
    
    help = 'Cleanup soft-deleted records based on retention policies'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--model',
            type=str,
            help='Specific model to cleanup (e.g., properties.Property)',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=None,
            help='Override default retention days for all models',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force cleanup even for models with no retention policy',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        specific_model = options['model']
        override_days = options['days']
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Starting cleanup {'(DRY RUN)' if dry_run else '(LIVE)'}"
            )
        )
        
        total_deleted = 0
        
        # Get all models that use SoftDeleteMixin
        soft_delete_models = self._get_soft_delete_models()
        
        if specific_model:
            # Filter to specific model
            try:
                app_label, model_name = specific_model.split('.')
                model = apps.get_model(app_label, model_name)
                if model in soft_delete_models:
                    soft_delete_models = [model]
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Model {specific_model} does not use SoftDeleteMixin"
                        )
                    )
                    return
            except (ValueError, LookupError):
                self.stdout.write(
                    self.style.ERROR(
                        f"Invalid model format: {specific_model}. Use app.Model format."
                    )
                )
                return
        
        for model in soft_delete_models:
            deleted_count = self._cleanup_model(
                model, dry_run, override_days, force
            )
            total_deleted += deleted_count
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Cleanup completed. Total records {'would be' if dry_run else ''} "
                f"deleted: {total_deleted}"
            )
        )
    
    def _get_soft_delete_models(self):
        """Get all models that use SoftDeleteMixin"""
        from apps.core.mixins import SoftDeleteMixin
        
        soft_delete_models = []
        
        for model in apps.get_models():
            if issubclass(model, SoftDeleteMixin):
                soft_delete_models.append(model)
        
        return soft_delete_models
    
    def _cleanup_model(self, model, dry_run=False, override_days=None, force=False):
        """Cleanup soft-deleted records for a specific model"""
        model_name = f"{model._meta.app_label}.{model._meta.model_name}"
        
        # Get retention policy
        retention_days = self._get_retention_days(model, override_days)
        
        if retention_days is None and not force:
            self.stdout.write(
                self.style.WARNING(
                    f"Skipping {model_name}: No retention policy defined. "
                    f"Use --force to cleanup anyway."
                )
            )
            return 0
        
        # Default to 90 days if no policy and force is used
        if retention_days is None and force:
            retention_days = 90
            self.stdout.write(
                self.style.WARNING(
                    f"Using default 90 days retention for {model_name}"
                )
            )
        
        # Calculate cutoff date
        cutoff_date = timezone.now() - timedelta(days=retention_days)
        
        # Get soft-deleted records older than cutoff
        queryset = model.objects.filter(
            is_deleted=True,
            deleted_at__lt=cutoff_date
        )
        
        count = queryset.count()
        
        if count == 0:
            self.stdout.write(
                f"No records to cleanup for {model_name}"
            )
            return 0
        
        self.stdout.write(
            f"Found {count} records to cleanup for {model_name} "
            f"(older than {retention_days} days)"
        )
        
        if not dry_run:
            # Perform hard delete
            deleted_count, _ = queryset.delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Deleted {deleted_count} records from {model_name}"
                )
            )
            
            # Log the cleanup
            logger.info(
                f"Cleanup: Deleted {deleted_count} soft-deleted records "
                f"from {model_name} (retention: {retention_days} days)"
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Would delete {count} records from {model_name}"
                )
            )
        
        return count
    
    def _get_retention_days(self, model, override_days=None):
        """Get retention days for a model"""
        if override_days is not None:
            return override_days
        
        # Check if model has retention policy defined
        if hasattr(model, 'RETENTION_DAYS'):
            return model.RETENTION_DAYS
        
        # Check model meta for retention policy
        if hasattr(model._meta, 'retention_days'):
            return model._meta.retention_days
        
        # Check settings for model-specific retention
        from django.conf import settings
        retention_policies = getattr(settings, 'SOFT_DELETE_RETENTION_POLICIES', {})
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