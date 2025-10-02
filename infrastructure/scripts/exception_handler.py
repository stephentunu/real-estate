#!/usr/bin/env python3
"""
Exception Handler for Jaston Real Estate Platform

This module provides comprehensive exception handling, recovery mechanisms,
logging, and notification capabilities for robust error management across
the entire platform infrastructure.

Author: Douglas Mutethia (Eleso Solutions)
Version: 1.0.0
"""

import asyncio
import functools
import json
import logging
import os
import smtplib
import sys
import traceback
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union

logger = logging.getLogger(__name__)


class PlatformException(Exception):
    """Base exception class for platform-specific errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 context: Optional[Dict[str, Any]] = None, recoverable: bool = True):
        """Initialize platform exception.
        
        Args:
            message: Human-readable error message.
            error_code: Unique error code for categorization.
            context: Additional context information.
            recoverable: Whether the error is recoverable.
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "PLATFORM_ERROR"
        self.context = context or {}
        self.recoverable = recoverable
        self.timestamp = datetime.now()


class EnvironmentException(PlatformException):
    """Exception for environment-related errors."""
    
    def __init__(self, message: str, missing_component: str, **kwargs):
        """Initialize environment exception.
        
        Args:
            message: Error message.
            missing_component: Name of missing component.
            **kwargs: Additional arguments for PlatformException.
        """
        super().__init__(message, error_code="ENV_ERROR", **kwargs)
        self.missing_component = missing_component


class ServiceException(PlatformException):
    """Exception for service-related errors."""
    
    def __init__(self, message: str, service_name: str, **kwargs):
        """Initialize service exception.
        
        Args:
            message: Error message.
            service_name: Name of the affected service.
            **kwargs: Additional arguments for PlatformException.
        """
        super().__init__(message, error_code="SERVICE_ERROR", **kwargs)
        self.service_name = service_name


class ConfigurationException(PlatformException):
    """Exception for configuration-related errors."""
    
    def __init__(self, message: str, config_file: Optional[str] = None, **kwargs):
        """Initialize configuration exception.
        
        Args:
            message: Error message.
            config_file: Path to problematic configuration file.
            **kwargs: Additional arguments for PlatformException.
        """
        super().__init__(message, error_code="CONFIG_ERROR", **kwargs)
        self.config_file = config_file


class DependencyException(PlatformException):
    """Exception for dependency-related errors."""
    
    def __init__(self, message: str, dependency_name: str, **kwargs):
        """Initialize dependency exception.
        
        Args:
            message: Error message.
            dependency_name: Name of the problematic dependency.
            **kwargs: Additional arguments for PlatformException.
        """
        super().__init__(message, error_code="DEPENDENCY_ERROR", **kwargs)
        self.dependency_name = dependency_name


class RecoveryStrategy:
    """Base class for error recovery strategies."""
    
    def __init__(self, name: str, max_attempts: int = 3):
        """Initialize recovery strategy.
        
        Args:
            name: Strategy name.
            max_attempts: Maximum recovery attempts.
        """
        self.name = name
        self.max_attempts = max_attempts
        self.attempt_count = 0
    
    async def can_recover(self, exception: Exception) -> bool:
        """Check if this strategy can recover from the given exception.
        
        Args:
            exception: Exception to check.
            
        Returns:
            True if recovery is possible, False otherwise.
        """
        return (
            self.attempt_count < self.max_attempts and
            isinstance(exception, PlatformException) and
            exception.recoverable
        )
    
    async def recover(self, exception: Exception, context: Dict[str, Any]) -> bool:
        """Attempt to recover from the exception.
        
        Args:
            exception: Exception to recover from.
            context: Recovery context information.
            
        Returns:
            True if recovery was successful, False otherwise.
        """
        self.attempt_count += 1
        logger.info(f"Attempting recovery with strategy '{self.name}' (attempt {self.attempt_count}/{self.max_attempts})")
        
        try:
            return await self._execute_recovery(exception, context)
        except Exception as recovery_error:
            logger.error(f"Recovery strategy '{self.name}' failed: {str(recovery_error)}")
            return False
    
    async def _execute_recovery(self, exception: Exception, context: Dict[str, Any]) -> bool:
        """Execute the actual recovery logic.
        
        Args:
            exception: Exception to recover from.
            context: Recovery context information.
            
        Returns:
            True if recovery was successful, False otherwise.
        """
        raise NotImplementedError("Subclasses must implement _execute_recovery")


class ServiceRestartStrategy(RecoveryStrategy):
    """Recovery strategy that restarts failed services."""
    
    def __init__(self, service_manager, **kwargs):
        """Initialize service restart strategy.
        
        Args:
            service_manager: Service manager instance.
            **kwargs: Additional arguments for RecoveryStrategy.
        """
        super().__init__("service_restart", **kwargs)
        self.service_manager = service_manager
    
    async def can_recover(self, exception: Exception) -> bool:
        """Check if service restart can recover from the exception.
        
        Args:
            exception: Exception to check.
            
        Returns:
            True if recovery is possible, False otherwise.
        """
        return (
            await super().can_recover(exception) and
            isinstance(exception, ServiceException)
        )
    
    async def _execute_recovery(self, exception: Exception, context: Dict[str, Any]) -> bool:
        """Restart the failed service.
        
        Args:
            exception: Service exception.
            context: Recovery context.
            
        Returns:
            True if service restarted successfully, False otherwise.
        """
        if not isinstance(exception, ServiceException):
            return False
        
        logger.info(f"Attempting to restart service: {exception.service_name}")
        
        # Stop the service first
        stop_success = await self.service_manager.stop_service(exception.service_name)
        if not stop_success:
            logger.error(f"Failed to stop service {exception.service_name}")
            return False
        
        # Wait a moment before restarting
        await asyncio.sleep(2)
        
        # Start the service
        start_success = await self.service_manager.start_service(exception.service_name)
        if start_success:
            logger.info(f"✅ Successfully restarted service: {exception.service_name}")
            return True
        else:
            logger.error(f"❌ Failed to restart service: {exception.service_name}")
            return False


class DependencyInstallStrategy(RecoveryStrategy):
    """Recovery strategy that installs missing dependencies."""
    
    def __init__(self, **kwargs):
        """Initialize dependency install strategy.
        
        Args:
            **kwargs: Additional arguments for RecoveryStrategy.
        """
        super().__init__("dependency_install", **kwargs)
    
    async def can_recover(self, exception: Exception) -> bool:
        """Check if dependency installation can recover from the exception.
        
        Args:
            exception: Exception to check.
            
        Returns:
            True if recovery is possible, False otherwise.
        """
        return (
            await super().can_recover(exception) and
            isinstance(exception, DependencyException)
        )
    
    async def _execute_recovery(self, exception: Exception, context: Dict[str, Any]) -> bool:
        """Install the missing dependency.
        
        Args:
            exception: Dependency exception.
            context: Recovery context.
            
        Returns:
            True if dependency installed successfully, False otherwise.
        """
        if not isinstance(exception, DependencyException):
            return False
        
        dependency_name = exception.dependency_name
        logger.info(f"Attempting to install missing dependency: {dependency_name}")
        
        try:
            # Determine installation method based on context
            if context.get('environment') == 'python':
                # Install Python package
                import subprocess
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", dependency_name
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info(f"✅ Successfully installed Python package: {dependency_name}")
                    return True
                else:
                    logger.error(f"❌ Failed to install Python package {dependency_name}: {result.stderr}")
                    return False
            
            elif context.get('environment') == 'node':
                # Install Node.js package
                import subprocess
                package_manager = context.get('package_manager', 'npm')
                
                result = subprocess.run([
                    package_manager, "install", dependency_name
                ], capture_output=True, text=True, cwd=context.get('cwd'))
                
                if result.returncode == 0:
                    logger.info(f"✅ Successfully installed Node.js package: {dependency_name}")
                    return True
                else:
                    logger.error(f"❌ Failed to install Node.js package {dependency_name}: {result.stderr}")
                    return False
            
            else:
                logger.error(f"Unknown environment for dependency installation: {context.get('environment')}")
                return False
                
        except Exception as install_error:
            logger.error(f"❌ Exception during dependency installation: {str(install_error)}")
            return False


class ConfigurationRepairStrategy(RecoveryStrategy):
    """Recovery strategy that repairs configuration issues."""
    
    def __init__(self, **kwargs):
        """Initialize configuration repair strategy.
        
        Args:
            **kwargs: Additional arguments for RecoveryStrategy.
        """
        super().__init__("configuration_repair", **kwargs)
    
    async def can_recover(self, exception: Exception) -> bool:
        """Check if configuration repair can recover from the exception.
        
        Args:
            exception: Exception to check.
            
        Returns:
            True if recovery is possible, False otherwise.
        """
        return (
            await super().can_recover(exception) and
            isinstance(exception, ConfigurationException)
        )
    
    async def _execute_recovery(self, exception: Exception, context: Dict[str, Any]) -> bool:
        """Repair the configuration issue.
        
        Args:
            exception: Configuration exception.
            context: Recovery context.
            
        Returns:
            True if configuration repaired successfully, False otherwise.
        """
        if not isinstance(exception, ConfigurationException):
            return False
        
        config_file = exception.config_file
        logger.info(f"Attempting to repair configuration: {config_file}")
        
        try:
            # Create backup of existing config
            if config_file and Path(config_file).exists():
                backup_path = f"{config_file}.backup.{int(datetime.now().timestamp())}"
                Path(config_file).rename(backup_path)
                logger.info(f"Created backup: {backup_path}")
            
            # Apply default configuration based on context
            default_config = context.get('default_config')
            if default_config and config_file:
                with open(config_file, 'w') as f:
                    if config_file.endswith('.json'):
                        json.dump(default_config, f, indent=2)
                    else:
                        f.write(str(default_config))
                
                logger.info(f"✅ Applied default configuration to: {config_file}")
                return True
            
            logger.error("No default configuration provided for repair")
            return False
            
        except Exception as repair_error:
            logger.error(f"❌ Exception during configuration repair: {str(repair_error)}")
            return False


class ExceptionHandler:
    """Comprehensive exception handler with recovery capabilities."""
    
    def __init__(self, project_root: Path):
        """Initialize exception handler.
        
        Args:
            project_root: Project root directory.
        """
        self.project_root = project_root
        self.recovery_strategies: List[RecoveryStrategy] = []
        self.error_log_path = project_root / "logs" / "errors.log"
        self.notification_config = {}
        
        # Ensure logs directory exists
        self.error_log_path.parent.mkdir(exist_ok=True)
        
        # Setup error logging
        self._setup_error_logging()
    
    def _setup_error_logging(self) -> None:
        """Setup error logging configuration."""
        error_handler = logging.FileHandler(self.error_log_path)
        error_handler.setLevel(logging.ERROR)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        error_handler.setFormatter(formatter)
        
        # Add handler to root logger
        logging.getLogger().addHandler(error_handler)
    
    def add_recovery_strategy(self, strategy: RecoveryStrategy) -> None:
        """Add a recovery strategy.
        
        Args:
            strategy: Recovery strategy to add.
        """
        self.recovery_strategies.append(strategy)
        logger.info(f"Added recovery strategy: {strategy.name}")
    
    def configure_notifications(self, config: Dict[str, Any]) -> None:
        """Configure error notifications.
        
        Args:
            config: Notification configuration.
        """
        self.notification_config = config
        logger.info("Configured error notifications")
    
    async def handle_exception(self, exception: Exception, context: Optional[Dict[str, Any]] = None) -> bool:
        """Handle an exception with recovery attempts.
        
        Args:
            exception: Exception to handle.
            context: Additional context information.
            
        Returns:
            True if exception was handled successfully, False otherwise.
        """
        context = context or {}
        
        # Log the exception
        error_info = self._extract_error_info(exception)
        logger.error(f"Handling exception: {error_info['message']}")
        
        # Save detailed error report
        await self._save_error_report(exception, context)
        
        # Attempt recovery
        recovery_success = await self._attempt_recovery(exception, context)
        
        # Send notifications if configured
        if not recovery_success:
            await self._send_notifications(exception, context)
        
        return recovery_success
    
    async def _attempt_recovery(self, exception: Exception, context: Dict[str, Any]) -> bool:
        """Attempt to recover from the exception using available strategies.
        
        Args:
            exception: Exception to recover from.
            context: Recovery context.
            
        Returns:
            True if recovery was successful, False otherwise.
        """
        for strategy in self.recovery_strategies:
            if await strategy.can_recover(exception):
                logger.info(f"Attempting recovery with strategy: {strategy.name}")
                
                recovery_success = await strategy.recover(exception, context)
                if recovery_success:
                    logger.info(f"✅ Recovery successful with strategy: {strategy.name}")
                    return True
                else:
                    logger.warning(f"⚠️ Recovery failed with strategy: {strategy.name}")
        
        logger.error("❌ All recovery strategies failed")
        return False
    
    def _extract_error_info(self, exception: Exception) -> Dict[str, Any]:
        """Extract comprehensive error information.
        
        Args:
            exception: Exception to extract info from.
            
        Returns:
            Dictionary containing error information.
        """
        error_info = {
            'type': type(exception).__name__,
            'message': str(exception),
            'timestamp': datetime.now().isoformat(),
            'traceback': traceback.format_exc()
        }
        
        # Add platform-specific information
        if isinstance(exception, PlatformException):
            error_info.update({
                'error_code': exception.error_code,
                'context': exception.context,
                'recoverable': exception.recoverable
            })
        
        return error_info
    
    async def _save_error_report(self, exception: Exception, context: Dict[str, Any]) -> None:
        """Save detailed error report to file.
        
        Args:
            exception: Exception to report.
            context: Error context.
        """
        error_info = self._extract_error_info(exception)
        error_info['context'] = context
        
        # Create error reports directory
        reports_dir = self.project_root / "reports" / "errors"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Save error report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = reports_dir / f"error_report_{timestamp}.json"
        
        with open(report_path, 'w') as f:
            json.dump(error_info, f, indent=2, default=str)
        
        logger.info(f"📄 Error report saved to: {report_path}")
    
    async def _send_notifications(self, exception: Exception, context: Dict[str, Any]) -> None:
        """Send error notifications if configured.
        
        Args:
            exception: Exception to notify about.
            context: Error context.
        """
        if not self.notification_config:
            return
        
        try:
            # Email notifications
            if 'email' in self.notification_config:
                await self._send_email_notification(exception, context)
            
            # Webhook notifications
            if 'webhook' in self.notification_config:
                await self._send_webhook_notification(exception, context)
                
        except Exception as notification_error:
            logger.error(f"Failed to send notifications: {str(notification_error)}")
    
    async def _send_email_notification(self, exception: Exception, context: Dict[str, Any]) -> None:
        """Send email notification about the error.
        
        Args:
            exception: Exception to notify about.
            context: Error context.
        """
        email_config = self.notification_config['email']
        
        msg = MIMEMultipart()
        msg['From'] = email_config['from']
        msg['To'] = ', '.join(email_config['to'])
        msg['Subject'] = f"Jaston Real Estate Platform Error: {type(exception).__name__}"
        
        # Create email body
        error_info = self._extract_error_info(exception)
        body = f"""
        An error occurred in the Jaston Real Estate Platform:
        
        Error Type: {error_info['type']}
        Message: {error_info['message']}
        Timestamp: {error_info['timestamp']}
        
        Context: {json.dumps(context, indent=2)}
        
        Traceback:
        {error_info['traceback']}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        if email_config.get('use_tls'):
            server.starttls()
        if email_config.get('username'):
            server.login(email_config['username'], email_config['password'])
        
        server.send_message(msg)
        server.quit()
        
        logger.info("📧 Email notification sent")
    
    async def _send_webhook_notification(self, exception: Exception, context: Dict[str, Any]) -> None:
        """Send webhook notification about the error.
        
        Args:
            exception: Exception to notify about.
            context: Error context.
        """
        webhook_config = self.notification_config['webhook']
        
        error_info = self._extract_error_info(exception)
        payload = {
            'error': error_info,
            'context': context,
            'platform': 'Jaston Real Estate'
        }
        
        import urllib.request
        import urllib.parse
        
        data = urllib.parse.urlencode({'payload': json.dumps(payload)}).encode()
        req = urllib.request.Request(webhook_config['url'], data=data)
        
        response = urllib.request.urlopen(req)
        if response.getcode() == 200:
            logger.info("🔗 Webhook notification sent")
        else:
            logger.error(f"Failed to send webhook notification: {response.getcode()}")


def exception_handler(handler: ExceptionHandler, context: Optional[Dict[str, Any]] = None):
    """Decorator for automatic exception handling.
    
    Args:
        handler: Exception handler instance.
        context: Additional context for error handling.
        
    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                recovery_success = await handler.handle_exception(e, context)
                if not recovery_success:
                    raise  # Re-raise if recovery failed
                
                # Retry the function after successful recovery
                return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Run async handler in event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    recovery_success = loop.run_until_complete(
                        handler.handle_exception(e, context)
                    )
                    if not recovery_success:
                        raise  # Re-raise if recovery failed
                    
                    # Retry the function after successful recovery
                    return func(*args, **kwargs)
                finally:
                    loop.close()
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


# Global exception handler instance
_global_handler: Optional[ExceptionHandler] = None


def setup_global_exception_handler(project_root: Path, service_manager=None) -> ExceptionHandler:
    """Setup global exception handler with default strategies.
    
    Args:
        project_root: Project root directory.
        service_manager: Service manager instance (optional).
        
    Returns:
        Configured exception handler.
    """
    global _global_handler
    
    _global_handler = ExceptionHandler(project_root)
    
    # Add default recovery strategies
    if service_manager:
        _global_handler.add_recovery_strategy(ServiceRestartStrategy(service_manager))
    
    _global_handler.add_recovery_strategy(DependencyInstallStrategy())
    _global_handler.add_recovery_strategy(ConfigurationRepairStrategy())
    
    # Setup global exception hook
    def global_exception_hook(exc_type, exc_value, exc_traceback):
        if _global_handler:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    _global_handler.handle_exception(exc_value)
                )
            finally:
                loop.close()
        
        # Call default exception hook
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = global_exception_hook
    
    return _global_handler


def get_global_exception_handler() -> Optional[ExceptionHandler]:
    """Get the global exception handler instance.
    
    Returns:
        Global exception handler or None if not setup.
    """
    return _global_handler