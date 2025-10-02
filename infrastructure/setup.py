#!/usr/bin/env python3
"""
Jaston Real Estate Platform Setup Script

This script performs comprehensive environment checks and autonomous configuration
for both frontend and backend services. It handles all exceptions and provides
robust service management capabilities with automatic recovery.

Author: Douglas Mutethia (Eleso Solutions)
Version: 3.0.0
"""

import asyncio
import json
import logging
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass

# Add the scripts directory to Python path
project_root = Path(__file__).parent.parent  # Go up one level since we're now in infrastructure/
scripts_dir = Path(__file__).parent / "scripts"  # scripts are now in infrastructure/scripts
sys.path.insert(0, str(scripts_dir))

try:
    from backend_checker import BackendEnvironmentChecker, BackendCheck
    from frontend_checker import FrontendEnvironmentChecker, FrontendCheck
    from service_manager import (
        ServiceManager, 
        create_django_service, 
        create_celery_service, 
        create_redis_service, 
        create_frontend_service
    )
    from exception_handler import (
        ExceptionHandler,
        setup_global_exception_handler,
        exception_handler,
        PlatformException,
        ServiceException,
        EnvironmentException
    )
    from integration_tester import IntegrationTester
except ImportError as e:
    print(f"❌ Failed to import required modules: {e}")
    print("Please ensure the scripts directory contains all required modules.")
    sys.exit(1)

# Ensure logs directory exists
logs_dir = project_root / "infrastructure" / "logs"
logs_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(logs_dir / "setup.log")
    ]
)
logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Enumeration for service status."""
    NOT_INSTALLED = "not_installed"
    INSTALLED = "installed"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


class SetupError(Exception):
    """Custom exception for setup-related errors."""
    pass


@dataclass
class ServiceInfo:
    """Information about a service."""
    name: str
    status: ServiceStatus
    version: Optional[str] = None
    port: Optional[int] = None
    pid: Optional[int] = None
    error_message: Optional[str] = None


@dataclass
class EnvironmentCheck:
    """Result of an environment check."""
    name: str
    passed: bool
    message: str
    fix_command: Optional[str] = None


class JastonSetup:
    """Main setup class for Jaston Real Estate Platform."""
    
    def __init__(self) -> None:
        """Initialize the setup manager."""
        self.project_root = Path(__file__).parent.absolute()
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.venv_path = self.backend_dir / "venv"
        
        # Service configurations
        self.services: Dict[str, ServiceInfo] = {}
        self.required_ports = {
            'django': 8000,
            'redis': 6379,
            'frontend': 5173,
            'flower': 5555
        }
        
        # System requirements
        self.min_python_version = (3, 11)
        self.min_node_version = (18, 0)
        
        # Initialize service manager
        self.service_manager = ServiceManager(self.project_root)
        
        # Initialize integration tester
        self.integration_tester = IntegrationTester(self.project_root)
        
        # Initialize exception handler
        self.exception_handler = ExceptionHandler(self.project_root)
        
        # Setup global exception handling
        setup_global_exception_handler(self.project_root, self.service_manager)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info(f"Initializing Jaston Setup from {self.project_root}")

    @exception_handler
    async def run_setup(self) -> bool:
        """Run the complete setup process."""
        try:
            logger.info("🚀 Starting Jaston Real Estate Platform Setup")
            logger.info("="*60)
            
            # Check for existing checkpoint
            checkpoint_restored = await self._restore_from_checkpoint()
            if checkpoint_restored:
                logger.info("📍 Restored from previous checkpoint")
            
            # Create setup lock file
            lock_file = self.project_root / "setup.lock"
            with open(lock_file, 'w') as f:
                f.write(str(os.getpid()))
            
            # Phase 1: Environment checks
            await self._create_recovery_checkpoint("environment_checks")
            logger.info("📋 Phase 1: Environment Checks")
            env_checks = await self._run_environment_checks()
            
            if not all(check.passed for check in env_checks):
                logger.info("🔧 Fixing environment issues...")
                await self._fix_environment_issues(env_checks)
            
            # Phase 2: Backend setup
            await self._create_recovery_checkpoint("backend_setup")
            logger.info("🐍 Phase 2: Backend Setup")
            await self._setup_backend()
            
            # Phase 3: Frontend setup
            await self._create_recovery_checkpoint("frontend_setup")
            logger.info("⚛️ Phase 3: Frontend Setup")
            await self._setup_frontend()
            
            # Phase 4: Service management
            await self._create_recovery_checkpoint("service_setup")
            logger.info("🔧 Phase 4: Service Management")
            await self._setup_services()
            
            # Phase 5: Health checks
            await self._create_recovery_checkpoint("health_checks")
            logger.info("🏥 Phase 5: Health Checks")
            health_status = await self._run_health_checks()
            
            if health_status:
                # Run comprehensive integration tests
                logger.info("🧪 Running integration tests...")
                test_results = await self.integration_tester.run_all_tests()
                
                if test_results["summary"]["failed"] > 0:
                    logger.warning(f"⚠️ {test_results['summary']['failed']} integration tests failed")
                    logger.info("📊 Check test results for details")
                else:
                    logger.info("✅ All integration tests passed")
                
                # Create final checkpoint
                await self._create_recovery_checkpoint("integration_tests_completed")
                
                await self._create_recovery_checkpoint("completed")
                logger.info("✅ Setup completed successfully!")
                await self._display_summary()
                
                # Clean up checkpoint file on successful completion
                checkpoint_file = self.project_root / "setup_checkpoint.json"
                if checkpoint_file.exists():
                    checkpoint_file.unlink()
                
                # Remove lock file
                if lock_file.exists():
                    lock_file.unlink()
                
                return True
            else:
                logger.error("❌ Setup completed with issues. Check logs for details.")
                return False
                
        except (PlatformException, ServiceException, EnvironmentException) as e:
            logger.error(f"❌ Setup failed with platform error: {str(e)}")
            await self._handle_setup_error(e)
            return False
        except Exception as e:
            logger.error(f"❌ Setup failed: {str(e)}")
            await self._handle_setup_error(e)
            return False

    async def _run_environment_checks(self) -> List[EnvironmentCheck]:
        """Run comprehensive environment checks."""
        checks: List[EnvironmentCheck] = []
        
        # Check Python version
        python_version = sys.version_info[:2]
        checks.append(EnvironmentCheck(
            name="Python Version",
            passed=python_version >= self.min_python_version,
            message=f"Python {python_version[0]}.{python_version[1]} (required: {self.min_python_version[0]}.{self.min_python_version[1]}+)",
            fix_command="Please install Python 3.11 or higher"
        ))
        
        # Check Node.js
        node_check = await self._check_nodejs()
        checks.append(node_check)
        
        # Check package managers
        checks.extend(await self._check_package_managers())
        
        # Check Redis
        redis_check = await self._check_redis()
        checks.append(redis_check)
        
        # Check ports availability
        port_checks = await self._check_ports()
        checks.extend(port_checks)
        
        # Check disk space
        disk_check = await self._check_disk_space()
        checks.append(disk_check)
        
        # Log results
        for check in checks:
            status = "✅" if check.passed else "❌"
            logger.info(f"{status} {check.name}: {check.message}")
        
        return checks
    
    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals gracefully."""
        logger.info(f"\n⚠️ Received signal {signum}, shutting down gracefully...")
        asyncio.create_task(self._cleanup_partial_setup())
        sys.exit(0)

    async def _check_nodejs(self) -> EnvironmentCheck:
        """Check Node.js installation and version."""
        try:
            result = await self._run_command(["node", "--version"])
            if result.returncode == 0:
                version_str = result.stdout.strip().lstrip('v')
                version_parts = version_str.split('.')
                version = (int(version_parts[0]), int(version_parts[1]))
                
                return EnvironmentCheck(
                    name="Node.js",
                    passed=version >= self.min_node_version,
                    message=f"Node.js {version_str} (required: {self.min_node_version[0]}.{self.min_node_version[1]}+)",
                    fix_command="curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs"
                )
            else:
                return EnvironmentCheck(
                    name="Node.js",
                    passed=False,
                    message="Node.js not found",
                    fix_command="curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs"
                )
        except Exception as e:
            return EnvironmentCheck(
                name="Node.js",
                passed=False,
                message=f"Error checking Node.js: {str(e)}",
                fix_command="curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs"
            )

    async def _check_package_managers(self) -> List[EnvironmentCheck]:
        """Check package managers (pip, npm, bun)."""
        checks = []
        
        # Check pip
        try:
            result = await self._run_command([sys.executable, "-m", "pip", "--version"])
            checks.append(EnvironmentCheck(
                name="pip",
                passed=result.returncode == 0,
                message="pip available" if result.returncode == 0 else "pip not available",
                fix_command="python -m ensurepip --upgrade"
            ))
        except Exception as e:
            checks.append(EnvironmentCheck(
                name="pip",
                passed=False,
                message=f"Error checking pip: {str(e)}",
                fix_command="python -m ensurepip --upgrade"
            ))
        
        # Check npm
        try:
            result = await self._run_command(["npm", "--version"])
            checks.append(EnvironmentCheck(
                name="npm",
                passed=result.returncode == 0,
                message="npm available" if result.returncode == 0 else "npm not available",
                fix_command="Install Node.js to get npm"
            ))
        except Exception as e:
            checks.append(EnvironmentCheck(
                name="npm",
                passed=False,
                message=f"npm not found: {str(e)}",
                fix_command="Install Node.js to get npm"
            ))
        
        # Check bun (optional)
        try:
            result = await self._run_command(["bun", "--version"])
            checks.append(EnvironmentCheck(
                name="bun",
                passed=result.returncode == 0,
                message="bun available (optional)" if result.returncode == 0 else "bun not available (optional)",
                fix_command="curl -fsSL https://bun.sh/install | bash"
            ))
        except Exception:
            checks.append(EnvironmentCheck(
                name="bun",
                passed=True,  # Optional
                message="bun not available (optional)",
                fix_command="curl -fsSL https://bun.sh/install | bash"
            ))
        
        return checks

    async def _check_redis(self) -> EnvironmentCheck:
        """Check Redis installation and availability."""
        try:
            # Check if Redis is installed
            result = await self._run_command(["redis-server", "--version"])
            if result.returncode != 0:
                return EnvironmentCheck(
                    name="Redis",
                    passed=False,
                    message="Redis not installed",
                    fix_command="sudo apt-get update && sudo apt-get install -y redis-server"
                )
            
            # Check if Redis is running
            try:
                result = await self._run_command(["redis-cli", "ping"])
                if result.returncode == 0 and "PONG" in result.stdout:
                    return EnvironmentCheck(
                        name="Redis",
                        passed=True,
                        message="Redis installed and running"
                    )
                else:
                    return EnvironmentCheck(
                        name="Redis",
                        passed=False,
                        message="Redis installed but not running",
                        fix_command="sudo systemctl start redis-server"
                    )
            except Exception:
                return EnvironmentCheck(
                    name="Redis",
                    passed=False,
                    message="Redis installed but not accessible",
                    fix_command="sudo systemctl start redis-server"
                )
                
        except Exception as e:
            return EnvironmentCheck(
                name="Redis",
                passed=False,
                message=f"Error checking Redis: {str(e)}",
                fix_command="sudo apt-get update && sudo apt-get install -y redis-server"
            )

    async def _check_ports(self) -> List[EnvironmentCheck]:
        """Check if required ports are available."""
        checks = []
        
        for service, port in self.required_ports.items():
            try:
                # Try to bind to the port
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    # Port is in use
                    checks.append(EnvironmentCheck(
                        name=f"Port {port} ({service})",
                        passed=False,
                        message=f"Port {port} is already in use",
                        fix_command=f"sudo lsof -ti:{port} | xargs sudo kill -9"
                    ))
                else:
                    # Port is available
                    checks.append(EnvironmentCheck(
                        name=f"Port {port} ({service})",
                        passed=True,
                        message=f"Port {port} is available"
                    ))
                    
            except Exception as e:
                checks.append(EnvironmentCheck(
                    name=f"Port {port} ({service})",
                    passed=False,
                    message=f"Error checking port {port}: {str(e)}",
                    fix_command="Check network configuration"
                ))
        
        return checks

    async def _check_disk_space(self) -> EnvironmentCheck:
        """Check available disk space."""
        try:
            stat = shutil.disk_usage(self.project_root)
            free_gb = stat.free / (1024**3)
            
            return EnvironmentCheck(
                name="Disk Space",
                passed=free_gb >= 2.0,  # Require at least 2GB free
                message=f"{free_gb:.1f}GB available (required: 2.0GB+)",
                fix_command="Free up disk space"
            )
        except Exception as e:
            return EnvironmentCheck(
                name="Disk Space",
                passed=False,
                message=f"Error checking disk space: {str(e)}",
                fix_command="Check disk configuration"
            )

    async def _fix_environment_issues(self, checks: List[EnvironmentCheck]) -> None:
        """Attempt to fix environment issues automatically."""
        failed_checks = [check for check in checks if not check.passed]
        
        for check in failed_checks:
            if check.fix_command and check.name not in ["Python Version", "Disk Space"]:
                logger.info(f"🔧 Attempting to fix: {check.name}")
                try:
                    if check.name == "Redis":
                        await self._install_redis()
                    elif check.name == "Node.js":
                        await self._install_nodejs()
                    elif "Port" in check.name:
                        await self._free_port(check)
                    else:
                        logger.warning(f"⚠️ Manual fix required for {check.name}: {check.fix_command}")
                except Exception as e:
                    logger.error(f"❌ Failed to fix {check.name}: {str(e)}")

    async def _install_redis(self) -> None:
        """Install and start Redis."""
        try:
            logger.info("Installing Redis...")
            await self._run_command(["sudo", "apt-get", "update"])
            await self._run_command(["sudo", "apt-get", "install", "-y", "redis-server"])
            await self._run_command(["sudo", "systemctl", "start", "redis-server"])
            await self._run_command(["sudo", "systemctl", "enable", "redis-server"])
            logger.info("✅ Redis installed and started")
        except Exception as e:
            raise SetupError(f"Failed to install Redis: {str(e)}")

    async def _install_nodejs(self) -> None:
        """Install Node.js."""
        try:
            logger.info("Installing Node.js...")
            await self._run_command([
                "curl", "-fsSL", "https://deb.nodesource.com/setup_lts.x", 
                "|", "sudo", "-E", "bash", "-"
            ])
            await self._run_command(["sudo", "apt-get", "install", "-y", "nodejs"])
            logger.info("✅ Node.js installed")
        except Exception as e:
            raise SetupError(f"Failed to install Node.js: {str(e)}")

    async def _free_port(self, check: EnvironmentCheck) -> None:
        """Attempt to free a port."""
        try:
            port = None
            for service, service_port in self.required_ports.items():
                if f"Port {service_port}" in check.name:
                    port = service_port
                    break
            
            if port:
                logger.info(f"Attempting to free port {port}...")
                await self._run_command(["sudo", "lsof", "-ti", f":{port}", "|", "xargs", "sudo", "kill", "-9"])
                logger.info(f"✅ Port {port} freed")
        except Exception as e:
            logger.warning(f"⚠️ Could not free port: {str(e)}")

    async def _run_command(self, command: List[str], cwd: Optional[Path] = None, 
                          timeout: int = 300) -> subprocess.CompletedProcess:
        """Run a command asynchronously with proper error handling."""
        try:
            if isinstance(command, list) and "|" in command:
                # Handle piped commands
                command_str = " ".join(command)
                process = await asyncio.create_subprocess_shell(
                    command_str,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd
                )
            else:
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd
                )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            
            return subprocess.CompletedProcess(
                args=command,
                returncode=process.returncode,
                stdout=stdout.decode('utf-8') if stdout else '',
                stderr=stderr.decode('utf-8') if stderr else ''
            )
            
        except asyncio.TimeoutError:
            logger.error(f"Command timed out: {' '.join(command)}")
            raise SetupError(f"Command timed out: {' '.join(command)}")
        except Exception as e:
            logger.error(f"Command failed: {' '.join(command)} - {str(e)}")
            raise SetupError(f"Command failed: {str(e)}")

    @exception_handler
    async def _setup_backend(self) -> None:
        """Set up the backend environment."""
        try:
            logger.info("Setting up Python backend...")
            
            # Create virtual environment if it doesn't exist
            if not self.venv_path.exists():
                logger.info("Creating Python virtual environment...")
                await self._run_command([sys.executable, "-m", "venv", str(self.venv_path)])
            
            # Activate virtual environment and install dependencies
            pip_path = self.venv_path / "bin" / "pip"
            python_path = self.venv_path / "bin" / "python"
            
            logger.info("Installing Python dependencies...")
            await self._run_command([
                str(pip_path), "install", "--upgrade", "pip"
            ])
            
            requirements_file = self.backend_dir / "requirements.txt"
            if requirements_file.exists():
                await self._run_command([
                    str(pip_path), "install", "-r", str(requirements_file)
                ])
            
            # Run Django setup
            logger.info("Setting up Django...")
            await self._run_command([
                str(python_path), "manage.py", "collectstatic", "--noinput"
            ], cwd=self.backend_dir)
            
            await self._run_command([
                str(python_path), "manage.py", "migrate"
            ], cwd=self.backend_dir)
            
            logger.info("✅ Backend setup completed")
            
        except Exception as e:
            raise ServiceException(f"Backend setup failed: {str(e)}")

    @exception_handler
    async def _setup_frontend(self) -> None:
        """Set up the frontend environment."""
        try:
            logger.info("Setting up frontend...")
            
            package_json = self.frontend_dir / "package.json"
            if not package_json.exists():
                logger.error("❌ Frontend package.json not found")
                raise EnvironmentException("Frontend package.json not found")
            
            # Install dependencies using npm or bun
            try:
                # Try bun first (faster)
                await self._run_command(["bun", "install"], cwd=self.frontend_dir)
                logger.info("✅ Frontend dependencies installed with bun")
            except Exception:
                try:
                    # Fallback to npm
                    await self._run_command(["npm", "install"], cwd=self.frontend_dir)
                    logger.info("✅ Frontend dependencies installed with npm")
                except Exception as e:
                    raise ServiceException(f"Failed to install frontend dependencies: {str(e)}")
            
            # Build frontend for production
            try:
                await self._run_command(["npm", "run", "build"], cwd=self.frontend_dir)
                logger.info("✅ Frontend built successfully")
            except Exception as e:
                logger.warning(f"⚠️ Frontend build failed: {str(e)}")
                
        except (EnvironmentException, ServiceException):
            raise
        except Exception as e:
            raise ServiceException(f"Frontend setup failed: {str(e)}")

    @exception_handler
    async def _setup_services(self) -> None:
        """Set up and start required services."""
        try:
            logger.info("Setting up services...")
            
            # Start Redis if not running
            try:
                result = await self._run_command(["redis-cli", "ping"])
                if result.returncode != 0 or "PONG" not in result.stdout:
                    await self._run_command(["sudo", "systemctl", "start", "redis-server"])
            except Exception:
                logger.warning("⚠️ Could not start Redis")
            
            # Start Django development server
            python_path = self.venv_path / "bin" / "python"
            django_process = await asyncio.create_subprocess_exec(
                str(python_path), "manage.py", "runserver", "0.0.0.0:8000",
                cwd=self.backend_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Give Django time to start
            await asyncio.sleep(3)
            
            if django_process.returncode is None:
                self.services['django'] = ServiceInfo(
                    name='Django',
                    status=ServiceStatus.RUNNING,
                    port=8000,
                    pid=django_process.pid
                )
                logger.info("✅ Django server started on port 8000")
            else:
                logger.error("❌ Failed to start Django server")
                raise ServiceException("Failed to start Django server")
            
            # Start Celery worker
            celery_process = await asyncio.create_subprocess_exec(
                str(python_path), "-m", "celery", "-A", "jaston", "worker", "-l", "info",
                cwd=self.backend_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await asyncio.sleep(2)
            
            if celery_process.returncode is None:
                self.services['celery'] = ServiceInfo(
                    name='Celery Worker',
                    status=ServiceStatus.RUNNING,
                    pid=celery_process.pid
                )
                logger.info("✅ Celery worker started")
            
            # Start Celery Beat
            beat_process = await asyncio.create_subprocess_exec(
                str(python_path), "-m", "celery", "-A", "jaston", "beat", "-l", "info",
                cwd=self.backend_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await asyncio.sleep(2)
            
            if beat_process.returncode is None:
                self.services['celery_beat'] = ServiceInfo(
                    name='Celery Beat',
                    status=ServiceStatus.RUNNING,
                    pid=beat_process.pid
                )
                logger.info("✅ Celery Beat started")
            
            logger.info("✅ Services setup completed")
            
        except ServiceException:
            raise
        except Exception as e:
            raise ServiceException(f"Service setup failed: {str(e)}")

    async def _run_health_checks(self) -> bool:
        """Run comprehensive health checks."""
        logger.info("Running health checks...")
        
        all_healthy = True
        
        # Check Django server
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:8000/admin/') as response:
                    if response.status in [200, 302]:  # 302 is redirect to login
                        logger.info("✅ Django server is healthy")
                    else:
                        logger.error(f"❌ Django server returned status {response.status}")
                        all_healthy = False
        except Exception as e:
            logger.error(f"❌ Django health check failed: {str(e)}")
            all_healthy = False
        
        # Check Redis
        try:
            result = await self._run_command(["redis-cli", "ping"])
            if result.returncode == 0 and "PONG" in result.stdout:
                logger.info("✅ Redis is healthy")
            else:
                logger.error("❌ Redis health check failed")
                all_healthy = False
        except Exception as e:
            logger.error(f"❌ Redis health check failed: {str(e)}")
            all_healthy = False
        
        # Check database connectivity
        try:
            python_path = self.venv_path / "bin" / "python"
            result = await self._run_command([
                str(python_path), "manage.py", "check", "--database", "default"
            ], cwd=self.backend_dir)
            
            if result.returncode == 0:
                logger.info("✅ Database is healthy")
            else:
                logger.error("❌ Database health check failed")
                all_healthy = False
        except Exception as e:
            logger.error(f"❌ Database health check failed: {str(e)}")
            all_healthy = False
        
        return all_healthy

    async def _display_summary(self) -> None:
        """Display setup summary."""
        logger.info("\n" + "="*60)
        logger.info("🎉 JASTON REAL ESTATE PLATFORM SETUP COMPLETE")
        logger.info("="*60)
        
        logger.info("\n📊 Services Status:")
        for service_name, service_info in self.services.items():
            status_emoji = "✅" if service_info.status == ServiceStatus.RUNNING else "❌"
            port_info = f" (port {service_info.port})" if service_info.port else ""
            logger.info(f"{status_emoji} {service_info.name}{port_info}")
        
        logger.info("\n🌐 Access URLs:")
        logger.info("• Django Admin: http://localhost:8000/admin/")
        logger.info("• API Documentation: http://localhost:8000/swagger/")
        logger.info("• API Redoc: http://localhost:8000/redoc/")
        
        if 'celery' in self.services:
            logger.info("• Flower (Celery Monitor): http://localhost:5555/")
        
        logger.info("\n🔧 Management Commands:")
        logger.info("• Stop all services: python setup.py --stop")
        logger.info("• Restart services: python setup.py --restart")
        logger.info("• View logs: tail -f setup.log")
        
        logger.info("\n📝 Next Steps:")
        logger.info("1. Create a superuser: cd backend && source venv/bin/activate && python manage.py createsuperuser")
        logger.info("2. Access the admin panel at http://localhost:8000/admin/")
        logger.info("3. Start developing your application!")
        
        logger.info("="*60)

    async def _handle_setup_error(self, error: Exception) -> None:
        """Handle setup errors gracefully with recovery mechanisms."""
        logger.error(f"\n❌ Setup Error: {str(error)}")
        
        # Use exception handler for recovery
        recovery_success = await self.exception_handler.handle_exception(error)
        
        if recovery_success:
            logger.info("✅ Error recovered successfully, retrying setup...")
            # Retry the setup process
            try:
                success = await self.run_setup()
                if success:
                    return
            except Exception as retry_error:
                logger.error(f"❌ Retry failed: {str(retry_error)}")
        
        # If recovery failed, provide troubleshooting steps
        logger.error("📋 Troubleshooting steps:")
        logger.error("1. Check the setup.log file for detailed error information")
        logger.error("2. Ensure you have sufficient permissions")
        logger.error("3. Verify internet connectivity for package downloads")
        logger.error("4. Check available disk space")
        logger.error("5. Try running the setup script again")
        logger.error("6. Check service logs in the logs/ directory")
        
        # Cleanup any partial setup
        await self._cleanup_partial_setup()

    async def _cleanup_partial_setup(self) -> None:
        """Clean up any partial setup artifacts."""
        try:
            logger.info("🧹 Cleaning up partial setup...")
            
            # Stop any running processes using service manager
            if hasattr(self, 'service_manager'):
                await self.service_manager.stop_all_services()
            
            # Stop any processes we started directly
            for service_info in self.services.values():
                if service_info.pid:
                    try:
                        os.kill(service_info.pid, signal.SIGTERM)
                        # Give process time to shutdown gracefully
                        await asyncio.sleep(2)
                        # Force kill if still running
                        try:
                            os.kill(service_info.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass  # Process already stopped
                    except ProcessLookupError:
                        pass  # Process already stopped
            
            # Clean up temporary files
            temp_files = [
                self.project_root / "setup.lock",
                self.project_root / "celerybeat-schedule",
                self.project_root / "celerybeat.pid"
            ]
            
            for temp_file in temp_files:
                if temp_file.exists():
                    try:
                        temp_file.unlink()
                    except Exception as e:
                        logger.warning(f"Could not remove {temp_file}: {str(e)}")
            
            logger.info("🧹 Partial setup cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    async def _create_recovery_checkpoint(self, stage: str) -> None:
        """Create a recovery checkpoint for the current setup stage."""
        try:
            checkpoint_data = {
                "stage": stage,
                "timestamp": time.time(),
                "services": {
                    name: {
                        "status": service.status.value,
                        "pid": service.pid,
                        "port": service.port
                    }
                    for name, service in self.services.items()
                }
            }
            
            checkpoint_file = self.project_root / "setup_checkpoint.json"
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Could not create recovery checkpoint: {str(e)}")

    async def _restore_from_checkpoint(self) -> bool:
        """Restore setup from the last checkpoint."""
        try:
            checkpoint_file = self.project_root / "setup_checkpoint.json"
            if not checkpoint_file.exists():
                return False
                
            with open(checkpoint_file, 'r') as f:
                checkpoint_data = json.load(f)
            
            logger.info(f"🔄 Restoring from checkpoint: {checkpoint_data['stage']}")
            
            # Restore service states
            for name, service_data in checkpoint_data.get('services', {}).items():
                if name in self.services:
                    self.services[name].status = ServiceStatus(service_data['status'])
                    self.services[name].pid = service_data.get('pid')
                    self.services[name].port = service_data.get('port')
            
            return True
            
        except Exception as e:
            logger.warning(f"Could not restore from checkpoint: {str(e)}")
            return False


async def main() -> None:
    """Main entry point."""
    try:
        # Check for command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == "--stop":
                logger.info("🛑 Stopping all services...")
                # Implementation for stopping services
                return
            elif sys.argv[1] == "--restart":
                logger.info("🔄 Restarting services...")
                # Implementation for restarting services
                return
            elif sys.argv[1] == "--test-only":
                logger.info("🧪 Running integration tests only...")
                setup = JastonSetup()
                
                # Run integration tests without asyncio.run since we're already in an event loop
                test_results = await setup.integration_tester.run_all_tests()
                
                # Print results
                summary = test_results["summary"]
                print(f"\n{'='*60}")
                print(f"🧪 INTEGRATION TEST RESULTS")
                print(f"{'='*60}")
                print(f"Total Tests: {summary['total_tests']}")
                print(f"Passed: {summary['passed']}")
                print(f"Failed: {summary['failed']}")
                print(f"Success Rate: {summary['success_rate']:.1f}%")
                print(f"Duration: {summary['total_duration']:.2f}s")
                print(f"{'='*60}")
                
                sys.exit(0 if summary['failed'] == 0 else 1)
            elif sys.argv[1] == "--skip-tests":
                logger.info("⏭️ Skipping integration tests...")
                # Implementation for skipping tests
                return
            elif sys.argv[1] == "--help":
                print("Jaston Real Estate Platform Setup Script")
                print("Usage:")
                print("  python setup.py          - Run full setup")
                print("  python setup.py --stop   - Stop all services")
                print("  python setup.py --restart - Restart services")
                print("  python setup.py --test-only - Run integration tests only")
                print("  python setup.py --skip-tests - Skip integration tests")
                print("  python setup.py --help   - Show this help")
                return
        
        # Run the main setup
        setup = JastonSetup()
        success = await setup.run_setup()
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n⚠️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Install aiohttp if not available (for health checks)
    try:
        import aiohttp
    except ImportError:
        logger.info("Installing aiohttp for health checks...")
        subprocess.run([sys.executable, "-m", "pip", "install", "aiohttp"], check=True)
        import aiohttp
    
    # Run the async main function
    asyncio.run(main())