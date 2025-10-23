from django.db import migrations


def create_interval_schedule(apps, schema_editor):
    """Create or get an IntervalSchedule with the given seconds."""
    IntervalSchedule = apps.get_model('django_celery_beat', 'IntervalSchedule')

    def get_or_create(seconds):
        # Try to find an existing schedule with the same every/period
        obj = IntervalSchedule.objects.filter(every=seconds, period='seconds').first()
        if obj:
            return obj
        return IntervalSchedule.objects.create(every=seconds, period='seconds')

    return get_or_create


def seed_periodic_tasks(apps, schema_editor):
    PeriodicTask = apps.get_model('django_celery_beat', 'PeriodicTask')
    IntervalSchedule = apps.get_model('django_celery_beat', 'IntervalSchedule')
    CrontabSchedule = apps.get_model('django_celery_beat', 'CrontabSchedule')

    # Import settings safely
    from django.conf import settings
    cfg = getattr(settings, 'CELERY_CONFIG', {}) or {}
    beat = cfg.get('beat_schedule', {})

    for name, entry in beat.items():
        task_name = entry.get('task')
        schedule_val = entry.get('schedule')
        options = entry.get('options', {}) or {}
        kwargs = entry.get('kwargs', {}) or {}

        # Only support numeric interval schedules here (seconds)
        if isinstance(schedule_val, (int, float)):
            seconds = int(schedule_val)
            # find or create IntervalSchedule
            interval = IntervalSchedule.objects.filter(every=seconds, period='seconds').first()
            if not interval:
                interval = IntervalSchedule.objects.create(every=seconds, period='seconds')

            # Create or update PeriodicTask
            pt, created = PeriodicTask.objects.update_or_create(
                name=name,
                defaults={
                    'task': task_name,
                    'interval': interval,
                    'enabled': True,
                    'kwargs': json_dump(kwargs),
                    'expires': options.get('expires'),
                }
            )
        else:
            # For non-numeric schedules (e.g., crontab), try to handle dict/cron spec
            # Support: {'minute': '0', 'hour': '0'} etc.
            if isinstance(schedule_val, dict):
                cron_spec = schedule_val
                crontab, _ = CrontabSchedule.objects.get_or_create(
                    minute=cron_spec.get('minute', '*'),
                    hour=cron_spec.get('hour', '*'),
                    day_of_week=cron_spec.get('day_of_week', '*'),
                    day_of_month=cron_spec.get('day_of_month', '*'),
                    month_of_year=cron_spec.get('month_of_year', '*'),
                )
                pt, created = PeriodicTask.objects.update_or_create(
                    name=name,
                    defaults={
                        'task': task_name,
                        'crontab': crontab,
                        'enabled': True,
                        'kwargs': json_dump(kwargs),
                        'expires': options.get('expires'),
                    }
                )
            else:
                # Unsupported schedule type; skip
                continue


def json_dump(obj):
    import json

    if not obj:
        return '{}'
    return json.dumps(obj)


class Migration(migrations.Migration):

    dependencies = [
('django_celery_beat', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_periodic_tasks, reverse_code=migrations.RunPython.noop),
    ]
