#!/usr/bin/env python3
"""
Backend Environment Checker for Jaston Real Estate Platform

This module provides comprehensive backend environment validation including:
- Python version and virtual environment checks
- Django configuration validation
- Database connectivity and migration status
- Required package dependency verification
- Service availability checks (Redis, Celery)

Author: Douglas Mutethia (Eleso Solutions)
Version: 1.0.0
"""

from __future__ import annotations

import asyncio
import importlib
import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class BackendCheck:
    """Result of a backend environment check."""
    name: str
    passed: bool
    message: str
    severity: str = "error"  # error, warning, info
    fix_suggestion: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class BackendEnvironmentChecker:
    """Comprehensive backend environment checker."""
    
    def __init__(self, project_root: Path) -> None:
        """Initialize the backend checker.
        
        Args:
            project_root: Path to the project root directory.
        """
        self.project_root = project_root
        self.backend_dir = project_root / "backend"
        self.venv_path = self.backend_dir / "venv"
        self.requirements_file = self.backend_dir / "requirements.txt"
        self.manage_py = self.backend_dir / "manage.py"
        
        # Required Python version
        self.min_python_version = (3, 11)
        self.recommended_python_version = (3, 13)
        
        # Critical Django apps that must be properly configured
        self.critical_apps = [
            'apps.core',
            'apps.users', 
            'apps.properties',
            'apps.leases',
            'apps.maintenance',
            'apps.media'
        ]

    async def run_all_checks(self) -> List[BackendCheck]:
        """Run all backend environment checks.
        
        Returns:
            List of check results.
        """
        logger.info("🐍 Running comprehensive backend environment checks...")
        
        checks: List[BackendCheck] = []
        
        # Core Python checks
        checks.extend(await self._check_python_environment())
        
        # Virtual environment checks
        checks.extend(await self._check_virtual_environment())
        
        # Dependencies checks
        checks.extend(await self._check_dependencies())
        
        # Django configuration checks
        checks.extend(await self._check_django_configuration())
        
        # Database checks
        checks.extend(await self._check_database())
        
        # Service checks
        checks.extend(await self._check_services())
        
        # Security checks
        checks.extend(await self._check_security_configuration())
        
        # Performance checks
        checks.extend(await self._check_performance_settings())
        
        return checks

    async def _check_python_environment(self) -> List[BackendCheck]:
        """Check Python version and environment."""
        checks = []
        
        # Check Python version
        current_version = sys.version_info[:2]
        
        if current_version < self.min_python_version:
            checks.append(BackendCheck(
                name="Python Version",
                passed=False,
                message=f"Python {current_version[0]}.{current_version[1]} is below minimum required version {self.min_python_version[0]}.{self.min_python_version[1]}",
                severity="error",
                fix_suggestion=f"Install Python {self.recommended_python_version[0]}.{self.recommended_python_version[1]} or higher"
            ))
        elif current_version < self.recommended_python_version:
            checks.append(BackendCheck(
                name="Python Version",
                passed=True,
                message=f"Python {current_version[0]}.{current_version[1]} (recommended: {self.recommended_python_version[0]}.{self.recommended_python_version[1]}+)",
                severity="warning",
                fix_suggestion=f"Consider upgrading to Python {self.recommended_python_version[0]}.{self.recommended_python_version[1]} for better performance"
            ))
        else:
            checks.append(BackendCheck(
                name="Python Version",
                passed=True,
                message=f"Python {current_version[0]}.{current_version[1]} ✅",
                severity="info"
            ))
        
        # Check Python executable location
        python_executable = sys.executable
        checks.append(BackendCheck(
            name="Python Executable",
            passed=True,
            message=f"Using Python at: {python_executable}",
            severity="info",
            details={"executable_path": python_executable}
        ))
        
        return checks

    async def _check_virtual_environment(self) -> List[BackendCheck]:
        """Check virtual environment setup."""
        checks = []
        
        # Check if virtual environment exists
        if not self.venv_path.exists():
            checks.append(BackendCheck(
                name="Virtual Environment",
                passed=False,
                message="Virtual environment not found",
                severity="error",
                fix_suggestion=f"Create virtual environment: python -m venv {self.venv_path}"
            ))
            return checks
        
        # Check virtual environment structure
        venv_python = self.venv_path / "bin" / "python"
        venv_pip = self.venv_path / "bin" / "pip"
        
        if not venv_python.exists():
            checks.append(BackendCheck(
                name="Virtual Environment Python",
                passed=False,
                message="Python executable not found in virtual environment",
                severity="error",
                fix_suggestion="Recreate virtual environment"
            ))
        else:
            checks.append(BackendCheck(
                name="Virtual Environment Python",
                passed=True,
                message="Virtual environment Python executable found",
                severity="info"
            ))
        
        if not venv_pip.exists():
            checks.append(BackendCheck(
                name="Virtual Environment Pip",
                passed=False,
                message="Pip not found in virtual environment",
                severity="error",
                fix_suggestion="Reinstall pip in virtual environment"
            ))
        else:
            checks.append(BackendCheck(
                name="Virtual Environment Pip",
                passed=True,
                message="Virtual environment pip found",
                severity="info"
            ))
        
        # Check if we're currently in the virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        checks.append(BackendCheck(
            name="Virtual Environment Active",
            passed=in_venv,
            message="Virtual environment is active" if in_venv else "Virtual environment not active",
            severity="warning" if not in_venv else "info",
            fix_suggestion="Activate virtual environment: source backend/venv/bin/activate" if not in_venv else None
        ))
        
        return checks

    async def _check_dependencies(self) -> List[BackendCheck]:
        """Check Python package dependencies."""
        checks = []
        
        # Check if requirements.txt exists
        if not self.requirements_file.exists():
            checks.append(BackendCheck(
                name="Requirements File",
                passed=False,
                message="requirements.txt not found",
                severity="error",
                fix_suggestion="Create requirements.txt with project dependencies"
            ))
            return checks
        
        checks.append(BackendCheck(
            name="Requirements File",
            passed=True,
            message="requirements.txt found",
            severity="info"
        ))
        
        # Parse requirements
        try:
            with open(self.requirements_file, 'r') as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            checks.append(BackendCheck(
                name="Requirements Parsing",
                passed=True,
                message=f"Found {len(requirements)} dependencies",
                severity="info",
                details={"dependency_count": len(requirements)}
            ))
        except Exception as e:
            checks.append(BackendCheck(
                name="Requirements Parsing",
                passed=False,
                message=f"Error parsing requirements.txt: {str(e)}",
                severity="error",
                fix_suggestion="Fix syntax errors in requirements.txt"
            ))
            return checks
        
        # Check critical dependencies
        critical_packages = {
            'Django': 'django',
            'Django REST Framework': 'djangorestframework',
            'Django CORS Headers': 'django-cors-headers',
            'Channels': 'channels',
            'Celery': 'celery',
            'Redis': 'redis',
            'Pillow': 'pillow',
            'psycopg2': 'psycopg2-binary'
        }
        
        for package_name, import_name in critical_packages.items():
            try:
                # Try to import the package
                importlib.import_module(import_name.replace('-', '_'))
                checks.append(BackendCheck(
                    name=f"Package: {package_name}",
                    passed=True,
                    message=f"{package_name} is installed",
                    severity="info"
                ))
            except ImportError:
                checks.append(BackendCheck(
                    name=f"Package: {package_name}",
                    passed=False,
                    message=f"{package_name} not installed",
                    severity="error",
                    fix_suggestion=f"Install {package_name}: pip install {import_name}"
                ))
        
        return checks

    async def _check_django_configuration(self) -> List[BackendCheck]:
        """Check Django configuration and setup."""
        checks = []
        
        # Check if manage.py exists
        if not self.manage_py.exists():
            checks.append(BackendCheck(
                name="Django manage.py",
                passed=False,
                message="manage.py not found",
                severity="error",
                fix_suggestion="Ensure Django project is properly initialized"
            ))
            return checks
        
        checks.append(BackendCheck(
            name="Django manage.py",
            passed=True,
            message="manage.py found",
            severity="info"
        ))
        
        # Try to import Django settings
        try:
            # Add backend directory to Python path
            sys.path.insert(0, str(self.backend_dir))
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jaston.settings')
            
            import django
            from django.conf import settings
            django.setup()
            
            checks.append(BackendCheck(
                name="Django Settings",
                passed=True,
                message="Django settings loaded successfully",
                severity="info"
            ))
            
            # Check critical settings
            if hasattr(settings, 'SECRET_KEY') and settings.SECRET_KEY:
                if 'django-insecure' in settings.SECRET_KEY:
                    checks.append(BackendCheck(
                        name="Django Secret Key",
                        passed=True,
                        message="Secret key found (using default insecure key)",
                        severity="warning",
                        fix_suggestion="Set a secure SECRET_KEY in production"
                    ))
                else:
                    checks.append(BackendCheck(
                        name="Django Secret Key",
                        passed=True,
                        message="Secret key configured",
                        severity="info"
                    ))
            else:
                checks.append(BackendCheck(
                    name="Django Secret Key",
                    passed=False,
                    message="Secret key not configured",
                    severity="error",
                    fix_suggestion="Set SECRET_KEY in settings"
                ))
            
            # Check installed apps
            if hasattr(settings, 'INSTALLED_APPS'):
                installed_apps = settings.INSTALLED_APPS
                missing_apps = []
                
                for app in self.critical_apps:
                    if app not in installed_apps:
                        missing_apps.append(app)
                
                if missing_apps:
                    checks.append(BackendCheck(
                        name="Django Apps Configuration",
                        passed=False,
                        message=f"Missing critical apps: {', '.join(missing_apps)}",
                        severity="error",
                        fix_suggestion="Add missing apps to INSTALLED_APPS in settings"
                    ))
                else:
                    checks.append(BackendCheck(
                        name="Django Apps Configuration",
                        passed=True,
                        message="All critical apps are installed",
                        severity="info"
                    ))
            
            # Check database configuration
            if hasattr(settings, 'DATABASES') and 'default' in settings.DATABASES:
                db_config = settings.DATABASES['default']
                checks.append(BackendCheck(
                    name="Database Configuration",
                    passed=True,
                    message=f"Database configured: {db_config.get('ENGINE', 'Unknown')}",
                    severity="info",
                    details={"database_engine": db_config.get('ENGINE')}
                ))
            else:
                checks.append(BackendCheck(
                    name="Database Configuration",
                    passed=False,
                    message="Database not configured",
                    severity="error",
                    fix_suggestion="Configure DATABASES in settings"
                ))
            
        except Exception as e:
            checks.append(BackendCheck(
                name="Django Configuration",
                passed=False,
                message=f"Error loading Django settings: {str(e)}",
                severity="error",
                fix_suggestion="Fix Django configuration errors"
            ))
        
        return checks

    async def _check_database(self) -> List[BackendCheck]:
        """Check database connectivity and migrations."""
        checks = []
        
        try:
            from django.core.management import execute_from_command_line
            from django.db import connection
            from django.core.management.commands.migrate import Command as MigrateCommand
            
            # Test database connection
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    if result:
                        checks.append(BackendCheck(
                            name="Database Connectivity",
                            passed=True,
                            message="Database connection successful",
                            severity="info"
                        ))
                    else:
                        checks.append(BackendCheck(
                            name="Database Connectivity",
                            passed=False,
                            message="Database connection failed",
                            severity="error",
                            fix_suggestion="Check database configuration and ensure database server is running"
                        ))
            except Exception as e:
                checks.append(BackendCheck(
                    name="Database Connectivity",
                    passed=False,
                    message=f"Database connection error: {str(e)}",
                    severity="error",
                    fix_suggestion="Check database configuration and ensure database server is running"
                ))
            
            # Check for pending migrations
            try:
                from django.core.management.commands.showmigrations import Command as ShowMigrationsCommand
                from io import StringIO
                
                # Capture output of showmigrations command
                output = StringIO()
                cmd = ShowMigrationsCommand()
                cmd.stdout = output
                cmd.handle(verbosity=0)
                
                migration_output = output.getvalue()
                
                # Check if there are unapplied migrations (marked with [ ])
                if '[ ]' in migration_output:
                    checks.append(BackendCheck(
                        name="Database Migrations",
                        passed=False,
                        message="Pending migrations found",
                        severity="warning",
                        fix_suggestion="Run: python manage.py migrate"
                    ))
                else:
                    checks.append(BackendCheck(
                        name="Database Migrations",
                        passed=True,
                        message="All migrations applied",
                        severity="info"
                    ))
                    
            except Exception as e:
                checks.append(BackendCheck(
                    name="Database Migrations",
                    passed=False,
                    message=f"Error checking migrations: {str(e)}",
                    severity="warning",
                    fix_suggestion="Run: python manage.py showmigrations to check migration status"
                ))
                
        except ImportError:
            checks.append(BackendCheck(
                name="Database Checks",
                passed=False,
                message="Django not properly configured for database checks",
                severity="error",
                fix_suggestion="Ensure Django is properly installed and configured"
            ))
        
        return checks

    async def _check_services(self) -> List[BackendCheck]:
        """Check external service dependencies."""
        checks = []
        
        # Check Redis connectivity
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=5)
            r.ping()
            checks.append(BackendCheck(
                name="Redis Service",
                passed=True,
                message="Redis is running and accessible",
                severity="info"
            ))
        except redis.ConnectionError:
            checks.append(BackendCheck(
                name="Redis Service",
                passed=False,
                message="Redis connection failed",
                severity="error",
                fix_suggestion="Start Redis server: sudo systemctl start redis-server"
            ))
        except ImportError:
            checks.append(BackendCheck(
                name="Redis Service",
                passed=False,
                message="Redis Python client not installed",
                severity="error",
                fix_suggestion="Install redis: pip install redis"
            ))
        except Exception as e:
            checks.append(BackendCheck(
                name="Redis Service",
                passed=False,
                message=f"Redis check error: {str(e)}",
                severity="error",
                fix_suggestion="Check Redis configuration and ensure it's running"
            ))
        
        return checks

    async def _check_security_configuration(self) -> List[BackendCheck]:
        """Check security-related configuration."""
        checks = []
        
        try:
            from django.conf import settings
            
            # Check DEBUG setting
            if hasattr(settings, 'DEBUG'):
                if settings.DEBUG:
                    checks.append(BackendCheck(
                        name="Debug Mode",
                        passed=True,
                        message="DEBUG=True (development mode)",
                        severity="info",
                        fix_suggestion="Set DEBUG=False in production"
                    ))
                else:
                    checks.append(BackendCheck(
                        name="Debug Mode",
                        passed=True,
                        message="DEBUG=False (production mode)",
                        severity="info"
                    ))
            
            # Check ALLOWED_HOSTS
            if hasattr(settings, 'ALLOWED_HOSTS'):
                if not settings.ALLOWED_HOSTS or settings.ALLOWED_HOSTS == ['*']:
                    checks.append(BackendCheck(
                        name="Allowed Hosts",
                        passed=True,
                        message="ALLOWED_HOSTS configured (permissive)",
                        severity="warning",
                        fix_suggestion="Configure specific allowed hosts for production"
                    ))
                else:
                    checks.append(BackendCheck(
                        name="Allowed Hosts",
                        passed=True,
                        message=f"ALLOWED_HOSTS configured: {len(settings.ALLOWED_HOSTS)} hosts",
                        severity="info"
                    ))
            
            # Check CORS configuration
            if 'corsheaders' in settings.INSTALLED_APPS:
                checks.append(BackendCheck(
                    name="CORS Configuration",
                    passed=True,
                    message="CORS headers configured",
                    severity="info"
                ))
            else:
                checks.append(BackendCheck(
                    name="CORS Configuration",
                    passed=False,
                    message="CORS headers not configured",
                    severity="warning",
                    fix_suggestion="Add 'corsheaders' to INSTALLED_APPS"
                ))
                
        except Exception as e:
            checks.append(BackendCheck(
                name="Security Configuration",
                passed=False,
                message=f"Error checking security settings: {str(e)}",
                severity="warning"
            ))
        
        return checks

    async def _check_performance_settings(self) -> List[BackendCheck]:
        """Check performance-related settings."""
        checks = []
        
        try:
            from django.conf import settings
            
            # Check cache configuration
            if hasattr(settings, 'CACHES') and 'default' in settings.CACHES:
                cache_backend = settings.CACHES['default']['BACKEND']
                if 'redis' in cache_backend.lower():
                    checks.append(BackendCheck(
                        name="Cache Configuration",
                        passed=True,
                        message="Redis cache configured",
                        severity="info"
                    ))
                elif 'locmem' in cache_backend.lower():
                    checks.append(BackendCheck(
                        name="Cache Configuration",
                        passed=True,
                        message="Local memory cache configured",
                        severity="warning",
                        fix_suggestion="Consider using Redis cache for better performance"
                    ))
                else:
                    checks.append(BackendCheck(
                        name="Cache Configuration",
                        passed=True,
                        message=f"Cache configured: {cache_backend}",
                        severity="info"
                    ))
            else:
                checks.append(BackendCheck(
                    name="Cache Configuration",
                    passed=False,
                    message="Cache not configured",
                    severity="warning",
                    fix_suggestion="Configure caching for better performance"
                ))
            
            # Check Celery configuration
            celery_settings = [
                'CELERY_BROKER_URL',
                'CELERY_RESULT_BACKEND',
                'CELERY_TASK_SERIALIZER'
            ]
            
            celery_configured = all(hasattr(settings, setting) for setting in celery_settings)
            
            if celery_configured:
                checks.append(BackendCheck(
                    name="Celery Configuration",
                    passed=True,
                    message="Celery task queue configured",
                    severity="info"
                ))
            else:
                checks.append(BackendCheck(
                    name="Celery Configuration",
                    passed=False,
                    message="Celery not fully configured",
                    severity="warning",
                    fix_suggestion="Configure Celery for background task processing"
                ))
                
        except Exception as e:
            checks.append(BackendCheck(
                name="Performance Settings",
                passed=False,
                message=f"Error checking performance settings: {str(e)}",
                severity="warning"
            ))
        
        return checks

    def generate_report(self, checks: List[BackendCheck]) -> Dict[str, Any]:
        """Generate a comprehensive report from check results.
        
        Args:
            checks: List of check results.
            
        Returns:
            Dictionary containing the report data.
        """
        passed_checks = [c for c in checks if c.passed]
        failed_checks = [c for c in checks if not c.passed]
        
        error_checks = [c for c in failed_checks if c.severity == "error"]
        warning_checks = [c for c in failed_checks if c.severity == "warning"]
        
        report = {
            "summary": {
                "total_checks": len(checks),
                "passed": len(passed_checks),
                "failed": len(failed_checks),
                "errors": len(error_checks),
                "warnings": len(warning_checks),
                "success_rate": (len(passed_checks) / len(checks)) * 100 if checks else 0
            },
            "checks": [
                {
                    "name": check.name,
                    "passed": check.passed,
                    "message": check.message,
                    "severity": check.severity,
                    "fix_suggestion": check.fix_suggestion,
                    "details": check.details
                }
                for check in checks
            ],
            "recommendations": [
                check.fix_suggestion for check in failed_checks 
                if check.fix_suggestion and check.severity == "error"
            ]
        }
        
        return report


async def main() -> None:
    """Main entry point for standalone execution."""
    project_root = Path(__file__).parent.parent
    checker = BackendEnvironmentChecker(project_root)
    
    checks = await checker.run_all_checks()
    report = checker.generate_report(checks)
    
    # Print summary
    print("\n" + "="*60)
    print("🐍 BACKEND ENVIRONMENT CHECK REPORT")
    print("="*60)
    
    summary = report["summary"]
    print(f"Total Checks: {summary['total_checks']}")
    print(f"Passed: {summary['passed']} ✅")
    print(f"Failed: {summary['failed']} ❌")
    print(f"Errors: {summary['errors']} 🚨")
    print(f"Warnings: {summary['warnings']} ⚠️")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    
    # Print failed checks
    if summary['failed'] > 0:
        print("\n❌ Failed Checks:")
        for check in checks:
            if not check.passed:
                severity_emoji = "🚨" if check.severity == "error" else "⚠️"
                print(f"{severity_emoji} {check.name}: {check.message}")
                if check.fix_suggestion:
                    print(f"   💡 Fix: {check.fix_suggestion}")
    
    # Save detailed report
    report_file = project_root / "backend_check_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_file}")


if __name__ == "__main__":
    asyncio.run(main())