#!/usr/bin/env python3
"""
Daemon Service Manager for Jaston Real Estate Platform

This module provides comprehensive daemon service management for all platform
services including Django, Celery, Redis using systemd. It handles service
installation, lifecycle management, health monitoring, and logging.

Author: Douglas Mutethia (Eleso Solutions)
Version: 1.0.0
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import subprocess
import sys
import time
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Import our service generator
from systemd.service_generator import ServiceGenerator, ServiceGeneratorError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/home/douglas/jaston-real-estate/infrastructure/logs/daemon-manager.log')
    ]
)
logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    UNKNOWN = "unknown"


class DaemonService:
    """Represents a systemd daemon service."""
    
    def __init__(self: DaemonService, name: str, service_file: str, description: str) -> None:
        """Initialize daemon service.
        
        Args:
            name: Service name identifier.
            service_file: Path to systemd service file.
            description: Human-readable service description.
        """
        self.name = name
        self.service_file = service_file
        self.description = description
        self.systemd_name = f"jaston-{name}.service"


class DaemonManager:
    """Manages all Jaston Real Estate platform daemon services."""
    
    def __init__(self: DaemonManager, project_root: Path, environment: str = "development") -> None:
        """Initialize daemon manager.
        
        Args:
            project_root: Project root directory path.
            environment: Environment name (development, production).
        """
        self.project_root = project_root
        self.environment = environment
        self.systemd_dir = project_root / "infrastructure" / "systemd"
        self.generated_dir = self.systemd_dir / "generated"
        
        # Initialize service generator
        self.service_generator = ServiceGenerator(
            config_dir=self.systemd_dir / "configs",
            template_dir=self.systemd_dir / "templates",
            output_dir=self.generated_dir
        )
        
        # Service definitions - now using generated files
        self.services: Dict[str, DaemonService] = {
            "redis": DaemonService(
                "redis",
                str(self.generated_dir / "jaston-redis.service"),
                "Redis Server for caching and message broker"
            ),
            "django": DaemonService(
                "django", 
                str(self.generated_dir / "jaston-django.service"),
                "Django Backend API Server"
            ),
            "celery-worker": DaemonService(
                "celery-worker",
                str(self.generated_dir / "jaston-celery-worker.service"), 
                "Celery Background Task Worker"
            ),
            "celery-beat": DaemonService(
                "celery-beat",
                str(self.generated_dir / "jaston-celery-beat.service"),
                "Celery Periodic Task Scheduler"
            )
        }
    
    async def _run_command(self: DaemonManager, command: List[str], check: bool = True) -> subprocess.CompletedProcess[str]:
        """Run a system command asynchronously.
        
        Args:
            command: Command and arguments to execute.
            check: Whether to raise exception on non-zero exit code.
            
        Returns:
            Completed process result.
            
        Raises:
            subprocess.CalledProcessError: If command fails and check=True.
        """
        try:
            logger.debug(f"Executing command: {' '.join(command)}")
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            result = subprocess.CompletedProcess(
                command, process.returncode, stdout.decode(), stderr.decode()
            )
            
            if check and result.returncode != 0:
                logger.error(f"Command failed: {' '.join(command)}")
                logger.error(f"Exit code: {result.returncode}")
                logger.error(f"Stderr: {result.stderr}")
                raise subprocess.CalledProcessError(result.returncode, command, result.stdout, result.stderr)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing command {' '.join(command)}: {str(e)}")
            raise
    
    async def generate_services(self: DaemonManager) -> bool:
        """Generate all systemd service files from templates.
        
        Returns:
            True if all services generated successfully, False otherwise.
        """
        try:
            logger.info("🔧 Generating systemd service files from templates...")
            
            # Generate each service
            services = ["redis", "django", "celery-worker", "celery-beat"]
            
            for service_name in services:
                logger.info(f"📝 Generating {service_name} service...")
                
                try:
                    self.service_generator.generate_service(service_name)
                    logger.info(f"✅ Generated jaston-{service_name}.service")
                    
                except ServiceGeneratorError as e:
                    logger.error(f"❌ Failed to generate {service_name}: {str(e)}")
                    return False
            
            logger.info("✅ All service files generated successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to generate services: {str(e)}")
            return False

    async def install_services(self: DaemonManager) -> bool:
        """Install all systemd service files.
        
        Returns:
            True if all services installed successfully, False otherwise.
        """
        try:
            # First generate the service files from templates
            if not await self.generate_services():
                return False
            
            logger.info("🔧 Installing systemd service files...")
            
            # Copy service files to systemd directory
            for service in self.services.values():
                source_path = Path(service.service_file)
                target_path = Path(f"/etc/systemd/system/{service.systemd_name}")
                
                if not source_path.exists():
                    logger.error(f"❌ Service file not found: {source_path}")
                    return False
                
                # Copy service file with sudo
                await self._run_command([
                    "sudo", "cp", str(source_path), str(target_path)
                ])
                logger.info(f"✅ Installed {service.systemd_name}")
            
            # Reload systemd daemon
            await self._run_command(["sudo", "systemctl", "daemon-reload"])
            logger.info("✅ Systemd daemon reloaded")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to install services: {str(e)}")
            return False
    
    async def get_service_status(self: DaemonManager, service_name: str) -> ServiceStatus:
        """Get the status of a specific service.
        
        Args:
            service_name: Name of the service to check.
            
        Returns:
            Current service status.
        """
        try:
            service = self.services.get(service_name)
            if not service:
                return ServiceStatus.UNKNOWN
            
            result = await self._run_command([
                "systemctl", "is-active", service.systemd_name
            ], check=False)
            
            status_map = {
                "active": ServiceStatus.ACTIVE,
                "inactive": ServiceStatus.INACTIVE,
                "failed": ServiceStatus.FAILED
            }
            
            return status_map.get(result.stdout.strip(), ServiceStatus.UNKNOWN)
            
        except Exception as e:
            logger.error(f"Error checking service status for {service_name}: {str(e)}")
            return ServiceStatus.UNKNOWN
    
    async def start_service(self: DaemonManager, service_name: str) -> bool:
        """Start a specific service.
        
        Args:
            service_name: Name of the service to start.
            
        Returns:
            True if service started successfully, False otherwise.
        """
        try:
            service = self.services.get(service_name)
            if not service:
                logger.error(f"❌ Unknown service: {service_name}")
                return False
            
            logger.info(f"🚀 Starting {service.description}...")
            await self._run_command(["sudo", "systemctl", "start", service.systemd_name])
            
            # Wait a moment and check status
            await asyncio.sleep(2)
            status = await self.get_service_status(service_name)
            
            if status == ServiceStatus.ACTIVE:
                logger.info(f"✅ {service.description} started successfully")
                return True
            else:
                logger.error(f"❌ Failed to start {service.description}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting {service_name}: {str(e)}")
            return False
    
    async def stop_service(self: DaemonManager, service_name: str) -> bool:
        """Stop a specific service.
        
        Args:
            service_name: Name of the service to stop.
            
        Returns:
            True if service stopped successfully, False otherwise.
        """
        try:
            service = self.services.get(service_name)
            if not service:
                logger.error(f"❌ Unknown service: {service_name}")
                return False
            
            logger.info(f"🛑 Stopping {service.description}...")
            await self._run_command(["sudo", "systemctl", "stop", service.systemd_name])
            
            # Wait a moment and check status
            await asyncio.sleep(2)
            status = await self.get_service_status(service_name)
            
            if status == ServiceStatus.INACTIVE:
                logger.info(f"✅ {service.description} stopped successfully")
                return True
            else:
                logger.warning(f"⚠️ {service.description} may not have stopped cleanly")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error stopping {service_name}: {str(e)}")
            return False
    
    async def restart_service(self: DaemonManager, service_name: str) -> bool:
        """Restart a specific service.
        
        Args:
            service_name: Name of the service to restart.
            
        Returns:
            True if service restarted successfully, False otherwise.
        """
        try:
            service = self.services.get(service_name)
            if not service:
                logger.error(f"❌ Unknown service: {service_name}")
                return False
            
            logger.info(f"🔄 Restarting {service.description}...")
            await self._run_command(["sudo", "systemctl", "restart", service.systemd_name])
            
            # Wait a moment and check status
            await asyncio.sleep(3)
            status = await self.get_service_status(service_name)
            
            if status == ServiceStatus.ACTIVE:
                logger.info(f"✅ {service.description} restarted successfully")
                return True
            else:
                logger.error(f"❌ Failed to restart {service.description}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error restarting {service_name}: {str(e)}")
            return False
    
    async def enable_service(self: DaemonManager, service_name: str) -> bool:
        """Enable a service to start automatically on boot.
        
        Args:
            service_name: Name of the service to enable.
            
        Returns:
            True if service enabled successfully, False otherwise.
        """
        try:
            service = self.services.get(service_name)
            if not service:
                logger.error(f"❌ Unknown service: {service_name}")
                return False
            
            logger.info(f"⚡ Enabling {service.description} for auto-start...")
            await self._run_command(["sudo", "systemctl", "enable", service.systemd_name])
            logger.info(f"✅ {service.description} enabled for auto-start")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error enabling {service_name}: {str(e)}")
            return False
    
    async def disable_service(self: DaemonManager, service_name: str) -> bool:
        """Disable a service from starting automatically on boot.
        
        Args:
            service_name: Name of the service to disable.
            
        Returns:
            True if service disabled successfully, False otherwise.
        """
        try:
            service = self.services.get(service_name)
            if not service:
                logger.error(f"❌ Unknown service: {service_name}")
                return False
            
            logger.info(f"🚫 Disabling {service.description} auto-start...")
            await self._run_command(["sudo", "systemctl", "disable", service.systemd_name])
            logger.info(f"✅ {service.description} disabled from auto-start")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error disabling {service_name}: {str(e)}")
            return False
    
    async def status_all(self: DaemonManager) -> Dict[str, ServiceStatus]:
        """Get status of all services.
        
        Returns:
            Dictionary mapping service names to their current status.
        """
        statuses = {}
        for service_name in self.services.keys():
            statuses[service_name] = await self.get_service_status(service_name)
        return statuses
    
    async def start_all(self: DaemonManager) -> bool:
        """Start all services in proper dependency order.
        
        Returns:
            True if all services started successfully, False otherwise.
        """
        # Start services in dependency order
        service_order = ["redis", "django", "celery-worker", "celery-beat"]
        
        logger.info("🚀 Starting all Jaston Real Estate services...")
        
        for service_name in service_order:
            success = await self.start_service(service_name)
            if not success:
                logger.error(f"❌ Failed to start {service_name}, stopping startup process")
                return False
            
            # Brief pause between service starts
            await asyncio.sleep(1)
        
        logger.info("✅ All services started successfully")
        return True
    
    async def stop_all(self: DaemonManager) -> bool:
        """Stop all services in reverse dependency order.
        
        Returns:
            True if all services stopped successfully, False otherwise.
        """
        # Stop services in reverse dependency order
        service_order = ["celery-beat", "celery-worker", "django", "redis"]
        
        logger.info("🛑 Stopping all Jaston Real Estate services...")
        
        success = True
        for service_name in service_order:
            if not await self.stop_service(service_name):
                success = False
            
            # Brief pause between service stops
            await asyncio.sleep(1)
        
        if success:
            logger.info("✅ All services stopped successfully")
        else:
            logger.warning("⚠️ Some services may not have stopped cleanly")
        
        return success
    
    async def restart_all(self: DaemonManager) -> bool:
        """Restart all services.
        
        Returns:
            True if all services restarted successfully, False otherwise.
        """
        logger.info("🔄 Restarting all Jaston Real Estate services...")
        
        # Stop all services first
        await self.stop_all()
        await asyncio.sleep(2)
        
        # Start all services
        return await self.start_all()
    
    async def enable_all(self: DaemonManager) -> bool:
        """Enable all services for auto-start on boot.
        
        Returns:
            True if all services enabled successfully, False otherwise.
        """
        logger.info("⚡ Enabling all services for auto-start...")
        
        success = True
        for service_name in self.services.keys():
            if not await self.enable_service(service_name):
                success = False
        
        if success:
            logger.info("✅ All services enabled for auto-start")
        else:
            logger.warning("⚠️ Some services may not have been enabled")
        
        return success
    
    def print_status(self: DaemonManager, statuses: Dict[str, ServiceStatus]) -> None:
        """Print formatted service status information.
        
        Args:
            statuses: Dictionary of service statuses.
        """
        print("\n" + "="*60)
        print("🏗️  JASTON REAL ESTATE PLATFORM - SERVICE STATUS")
        print("="*60)
        
        for service_name, status in statuses.items():
            service = self.services[service_name]
            status_icon = {
                ServiceStatus.ACTIVE: "🟢",
                ServiceStatus.INACTIVE: "🔴", 
                ServiceStatus.FAILED: "❌",
                ServiceStatus.UNKNOWN: "❓"
            }.get(status, "❓")
            
            print(f"{status_icon} {service.description:<35} {status.value.upper()}")
        
        print("="*60)


async def main() -> None:
    """Main entry point for daemon manager."""
    parser = argparse.ArgumentParser(
        description="Jaston Real Estate Platform Daemon Service Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s install              # Install all systemd service files
  %(prog)s start --all          # Start all services
  %(prog)s stop django          # Stop Django service
  %(prog)s restart celery-worker # Restart Celery worker
  %(prog)s status               # Show status of all services
  %(prog)s enable --all         # Enable all services for auto-start
        """
    )
    
    parser.add_argument(
        "action",
        choices=["install", "start", "stop", "restart", "status", "enable", "disable"],
        help="Action to perform"
    )
    
    parser.add_argument(
        "service",
        nargs="?",
        choices=["redis", "django", "celery-worker", "celery-beat"],
        help="Specific service to manage (optional)"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Apply action to all services"
    )
    
    args = parser.parse_args()
    
    # Initialize daemon manager
    project_root = Path(__file__).parent.parent
    
    # Determine environment from command line or default to development
    environment = "development"  # Could be extended to accept --env flag
    
    manager = DaemonManager(project_root, environment)
    
    try:
        if args.action == "install":
            success = await manager.install_services()
            sys.exit(0 if success else 1)
        
        elif args.action == "status":
            statuses = await manager.status_all()
            manager.print_status(statuses)
            sys.exit(0)
        
        elif args.action == "start":
            if args.all:
                success = await manager.start_all()
            elif args.service:
                success = await manager.start_service(args.service)
            else:
                parser.error("Must specify --all or a specific service")
            sys.exit(0 if success else 1)
        
        elif args.action == "stop":
            if args.all:
                success = await manager.stop_all()
            elif args.service:
                success = await manager.stop_service(args.service)
            else:
                parser.error("Must specify --all or a specific service")
            sys.exit(0 if success else 1)
        
        elif args.action == "restart":
            if args.all:
                success = await manager.restart_all()
            elif args.service:
                success = await manager.restart_service(args.service)
            else:
                parser.error("Must specify --all or a specific service")
            sys.exit(0 if success else 1)
        
        elif args.action == "enable":
            if args.all:
                success = await manager.enable_all()
            elif args.service:
                success = await manager.enable_service(args.service)
            else:
                parser.error("Must specify --all or a specific service")
            sys.exit(0 if success else 1)
        
        elif args.action == "disable":
            if args.service:
                success = await manager.disable_service(args.service)
            else:
                parser.error("Must specify a specific service")
            sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())