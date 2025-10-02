#!/usr/bin/env python3
"""
Service Manager for Jaston Real Estate Platform

This module provides comprehensive service management capabilities for all
platform services including Django, Celery, Redis, and frontend development server.
It handles service lifecycle, health monitoring, and graceful shutdown.

Author: Douglas Mutethia (Eleso Solutions)
Version: 1.0.0
"""

import asyncio
import json
import logging
import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger(__name__)


class ServiceProcess:
    """Represents a managed service process."""
    
    def __init__(self, name: str, command: List[str], cwd: Optional[Path] = None, 
                 env: Optional[Dict[str, str]] = None, health_check_url: Optional[str] = None):
        """Initialize service process.
        
        Args:
            name: Service name for identification.
            command: Command to start the service.
            cwd: Working directory for the service.
            env: Environment variables for the service.
            health_check_url: URL for health checking (optional).
        """
        self.name = name
        self.command = command
        self.cwd = cwd
        self.env = env or {}
        self.health_check_url = health_check_url
        self.process: Optional[subprocess.Popen] = None
        self.start_time: Optional[float] = None
        self.restart_count = 0
        self.max_restarts = 3
        
    def is_running(self) -> bool:
        """Check if the service process is running.
        
        Returns:
            True if process is running, False otherwise.
        """
        return self.process is not None and self.process.poll() is None
    
    def get_pid(self) -> Optional[int]:
        """Get the process ID.
        
        Returns:
            Process ID if running, None otherwise.
        """
        return self.process.pid if self.process else None
    
    def get_uptime(self) -> Optional[float]:
        """Get service uptime in seconds.
        
        Returns:
            Uptime in seconds if running, None otherwise.
        """
        if self.start_time and self.is_running():
            return time.time() - self.start_time
        return None


class ServiceManager:
    """Comprehensive service manager for the platform."""
    
    def __init__(self, project_root: Path):
        """Initialize service manager.
        
        Args:
            project_root: Path to the project root directory.
        """
        self.project_root = project_root
        self.backend_dir = project_root / "backend"
        self.frontend_dir = project_root / "frontend"
        self.services: Dict[str, ServiceProcess] = {}
        self.shutdown_requested = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals.
        
        Args:
            signum: Signal number.
            frame: Current stack frame.
        """
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True
        asyncio.create_task(self.stop_all_services())
    
    async def register_service(self, service: ServiceProcess) -> None:
        """Register a service for management.
        
        Args:
            service: Service process to register.
        """
        self.services[service.name] = service
        logger.info(f"Registered service: {service.name}")
    
    async def start_service(self, service_name: str) -> bool:
        """Start a specific service.
        
        Args:
            service_name: Name of the service to start.
            
        Returns:
            True if service started successfully, False otherwise.
        """
        if service_name not in self.services:
            logger.error(f"Service '{service_name}' not registered")
            return False
        
        service = self.services[service_name]
        
        if service.is_running():
            logger.info(f"Service '{service_name}' is already running")
            return True
        
        try:
            logger.info(f"Starting service: {service_name}")
            
            # Prepare environment
            env = os.environ.copy()
            env.update(service.env)
            
            # Start the process
            service.process = subprocess.Popen(
                service.command,
                cwd=service.cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid  # Create new process group
            )
            
            service.start_time = time.time()
            
            # Give the service time to start
            await asyncio.sleep(2)
            
            # Check if it's still running
            if service.is_running():
                logger.info(f"✅ Service '{service_name}' started successfully (PID: {service.get_pid()})")
                
                # Perform health check if available
                if service.health_check_url:
                    health_ok = await self._health_check(service)
                    if not health_ok:
                        logger.warning(f"⚠️ Service '{service_name}' started but failed health check")
                        return False
                
                return True
            else:
                # Process died immediately
                stdout, stderr = service.process.communicate(timeout=5)
                logger.error(f"❌ Service '{service_name}' failed to start: {stderr.decode()}")
                service.process = None
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start service '{service_name}': {str(e)}")
            service.process = None
            return False
    
    async def stop_service(self, service_name: str, timeout: int = 10) -> bool:
        """Stop a specific service gracefully.
        
        Args:
            service_name: Name of the service to stop.
            timeout: Timeout in seconds for graceful shutdown.
            
        Returns:
            True if service stopped successfully, False otherwise.
        """
        if service_name not in self.services:
            logger.error(f"Service '{service_name}' not registered")
            return False
        
        service = self.services[service_name]
        
        if not service.is_running():
            logger.info(f"Service '{service_name}' is not running")
            return True
        
        try:
            logger.info(f"Stopping service: {service_name}")
            
            # Send SIGTERM to the process group
            os.killpg(os.getpgid(service.process.pid), signal.SIGTERM)
            
            # Wait for graceful shutdown
            try:
                service.process.wait(timeout=timeout)
                logger.info(f"✅ Service '{service_name}' stopped gracefully")
            except subprocess.TimeoutExpired:
                # Force kill if graceful shutdown failed
                logger.warning(f"⚠️ Service '{service_name}' didn't stop gracefully, force killing...")
                os.killpg(os.getpgid(service.process.pid), signal.SIGKILL)
                service.process.wait()
                logger.info(f"🔪 Service '{service_name}' force killed")
            
            service.process = None
            service.start_time = None
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop service '{service_name}': {str(e)}")
            return False
    
    async def restart_service(self, service_name: str) -> bool:
        """Restart a specific service.
        
        Args:
            service_name: Name of the service to restart.
            
        Returns:
            True if service restarted successfully, False otherwise.
        """
        if service_name not in self.services:
            logger.error(f"Service '{service_name}' not registered")
            return False
        
        service = self.services[service_name]
        
        # Check restart limits
        if service.restart_count >= service.max_restarts:
            logger.error(f"❌ Service '{service_name}' has exceeded maximum restart attempts")
            return False
        
        logger.info(f"Restarting service: {service_name}")
        
        # Stop the service
        stop_success = await self.stop_service(service_name)
        if not stop_success:
            logger.error(f"❌ Failed to stop service '{service_name}' for restart")
            return False
        
        # Wait a moment before restarting
        await asyncio.sleep(1)
        
        # Start the service
        start_success = await self.start_service(service_name)
        if start_success:
            service.restart_count += 1
            logger.info(f"✅ Service '{service_name}' restarted successfully (restart #{service.restart_count})")
        else:
            logger.error(f"❌ Failed to restart service '{service_name}'")
        
        return start_success
    
    async def start_all_services(self) -> Dict[str, bool]:
        """Start all registered services.
        
        Returns:
            Dictionary mapping service names to their start success status.
        """
        logger.info("Starting all services...")
        results = {}
        
        # Start services in dependency order
        service_order = ['redis', 'django', 'celery', 'frontend']
        
        for service_name in service_order:
            if service_name in self.services:
                results[service_name] = await self.start_service(service_name)
                
                # Add delay between service starts
                if results[service_name]:
                    await asyncio.sleep(1)
        
        # Start any remaining services not in the ordered list
        for service_name in self.services:
            if service_name not in results:
                results[service_name] = await self.start_service(service_name)
        
        successful_starts = sum(1 for success in results.values() if success)
        total_services = len(results)
        
        logger.info(f"Service startup complete: {successful_starts}/{total_services} services started")
        
        return results
    
    async def stop_all_services(self) -> Dict[str, bool]:
        """Stop all running services gracefully.
        
        Returns:
            Dictionary mapping service names to their stop success status.
        """
        logger.info("Stopping all services...")
        results = {}
        
        # Stop services in reverse dependency order
        service_order = ['frontend', 'celery', 'django', 'redis']
        
        for service_name in service_order:
            if service_name in self.services:
                results[service_name] = await self.stop_service(service_name)
        
        # Stop any remaining services not in the ordered list
        for service_name in self.services:
            if service_name not in results:
                results[service_name] = await self.stop_service(service_name)
        
        successful_stops = sum(1 for success in results.values() if success)
        total_services = len(results)
        
        logger.info(f"Service shutdown complete: {successful_stops}/{total_services} services stopped")
        
        return results
    
    async def get_service_status(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of a specific service.
        
        Args:
            service_name: Name of the service.
            
        Returns:
            Service status dictionary or None if service not found.
        """
        if service_name not in self.services:
            return None
        
        service = self.services[service_name]
        
        status = {
            'name': service.name,
            'running': service.is_running(),
            'pid': service.get_pid(),
            'uptime': service.get_uptime(),
            'restart_count': service.restart_count,
            'command': ' '.join(service.command),
            'cwd': str(service.cwd) if service.cwd else None,
            'health_check_url': service.health_check_url
        }
        
        # Add health check status if available
        if service.health_check_url and service.is_running():
            status['health_check'] = await self._health_check(service)
        
        return status
    
    async def get_all_service_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all registered services.
        
        Returns:
            Dictionary mapping service names to their status dictionaries.
        """
        status_dict = {}
        
        for service_name in self.services:
            status_dict[service_name] = await self.get_service_status(service_name)
        
        return status_dict
    
    async def _health_check(self, service: ServiceProcess) -> bool:
        """Perform health check on a service.
        
        Args:
            service: Service to health check.
            
        Returns:
            True if health check passed, False otherwise.
        """
        if not service.health_check_url:
            return True  # No health check configured
        
        try:
            import urllib.request
            response = urllib.request.urlopen(service.health_check_url, timeout=10)
            return response.getcode() in [200, 302]
        except Exception as e:
            logger.warning(f"Health check failed for {service.name}: {str(e)}")
            return False
    
    async def monitor_services(self, check_interval: int = 30) -> None:
        """Monitor services and restart failed ones.
        
        Args:
            check_interval: Interval in seconds between health checks.
        """
        logger.info(f"Starting service monitoring (check interval: {check_interval}s)")
        
        while not self.shutdown_requested:
            try:
                for service_name, service in self.services.items():
                    if not service.is_running():
                        logger.warning(f"⚠️ Service '{service_name}' is not running")
                        
                        # Attempt restart if within limits
                        if service.restart_count < service.max_restarts:
                            logger.info(f"🔄 Attempting to restart '{service_name}'...")
                            await self.restart_service(service_name)
                        else:
                            logger.error(f"❌ Service '{service_name}' has exceeded restart limits")
                    
                    elif service.health_check_url:
                        # Perform health check
                        health_ok = await self._health_check(service)
                        if not health_ok:
                            logger.warning(f"⚠️ Health check failed for '{service_name}'")
                            
                            # Restart unhealthy service
                            if service.restart_count < service.max_restarts:
                                logger.info(f"🔄 Restarting unhealthy service '{service_name}'...")
                                await self.restart_service(service_name)
                
                # Wait before next check
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"❌ Error during service monitoring: {str(e)}")
                await asyncio.sleep(check_interval)
    
    async def generate_service_report(self) -> Dict[str, Any]:
        """Generate comprehensive service report.
        
        Returns:
            Service report dictionary.
        """
        status_dict = await self.get_all_service_status()
        
        report = {
            'timestamp': time.time(),
            'total_services': len(self.services),
            'running_services': sum(1 for status in status_dict.values() if status['running']),
            'failed_services': sum(1 for status in status_dict.values() if not status['running']),
            'services': status_dict,
            'system_info': {
                'project_root': str(self.project_root),
                'backend_dir': str(self.backend_dir),
                'frontend_dir': str(self.frontend_dir)
            }
        }
        
        return report
    
    async def save_service_report(self, report_path: Optional[Path] = None) -> Path:
        """Save service report to file.
        
        Args:
            report_path: Path to save the report (optional).
            
        Returns:
            Path where the report was saved.
        """
        if report_path is None:
            reports_dir = self.project_root / "reports"
            reports_dir.mkdir(exist_ok=True)
            report_path = reports_dir / f"service_report_{int(time.time())}.json"
        
        report = await self.generate_service_report()
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Service report saved to: {report_path}")
        return report_path


# Predefined service configurations
def create_django_service(project_root: Path) -> ServiceProcess:
    """Create Django service configuration.
    
    Args:
        project_root: Project root directory.
        
    Returns:
        Configured Django service process.
    """
    backend_dir = project_root / "backend"
    venv_python = backend_dir / "venv" / "bin" / "python"
    
    return ServiceProcess(
        name="django",
        command=[str(venv_python), "manage.py", "runserver", "0.0.0.0:8000"],
        cwd=backend_dir,
        health_check_url="http://localhost:8000/admin/"
    )


def create_celery_service(project_root: Path) -> ServiceProcess:
    """Create Celery service configuration.
    
    Args:
        project_root: Project root directory.
        
    Returns:
        Configured Celery service process.
    """
    backend_dir = project_root / "backend"
    venv_python = backend_dir / "venv" / "bin" / "python"
    
    return ServiceProcess(
        name="celery",
        command=[str(venv_python), "-m", "celery", "worker", "-A", "jaston", "-l", "info"],
        cwd=backend_dir
    )


def create_redis_service() -> ServiceProcess:
    """Create Redis service configuration.
    
    Returns:
        Configured Redis service process.
    """
    return ServiceProcess(
        name="redis",
        command=["redis-server", "--daemonize", "no"],
        health_check_url="redis://localhost:6379"
    )


def create_frontend_service(project_root: Path) -> ServiceProcess:
    """Create frontend service configuration.
    
    Args:
        project_root: Project root directory.
        
    Returns:
        Configured frontend service process.
    """
    frontend_dir = project_root / "frontend"
    
    # Determine package manager
    import shutil
    package_manager = "bun" if shutil.which("bun") else "npm"
    
    return ServiceProcess(
        name="frontend",
        command=[package_manager, "run", "dev", "--", "--host", "0.0.0.0"],
        cwd=frontend_dir,
        health_check_url="http://localhost:5173/"
    )


async def main():
    """Main entry point for testing service manager."""
    project_root = Path(__file__).parent.parent
    
    # Create service manager
    manager = ServiceManager(project_root)
    
    # Register services
    await manager.register_service(create_django_service(project_root))
    await manager.register_service(create_celery_service(project_root))
    await manager.register_service(create_frontend_service(project_root))
    
    try:
        # Start all services
        results = await manager.start_all_services()
        print("Service start results:", results)
        
        # Monitor services
        await manager.monitor_services()
        
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        await manager.stop_all_services()


if __name__ == "__main__":
    asyncio.run(main())