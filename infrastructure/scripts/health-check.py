#!/usr/bin/env python3
"""
Health Check Monitor for Jaston Real Estate Platform

This module provides comprehensive health monitoring for all platform services
including API endpoints, database connectivity, Redis connectivity, Celery
workers, and system resources. It can be used for monitoring dashboards,
alerting systems, and automated health checks.

Author: Douglas Mutethia (Eleso Solutions)
Version: 1.0.0
"""

from __future__ import annotations

import asyncio
import json
import logging
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import urllib.request
import urllib.error

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health check status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check operation."""
    service: str
    status: HealthStatus
    message: str
    response_time_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self: HealthCheckResult) -> None:
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class HealthChecker:
    """Comprehensive health checker for Jaston Real Estate platform."""
    
    def __init__(self: HealthChecker, base_url: str = "http://localhost:8000") -> None:
        """Initialize health checker.
        
        Args:
            base_url: Base URL for API health checks.
        """
        self.base_url = base_url
        self.timeout = 10  # seconds
        
    async def _run_command(self: HealthChecker, command: List[str]) -> subprocess.CompletedProcess[str]:
        """Run a system command asynchronously.
        
        Args:
            command: Command and arguments to execute.
            
        Returns:
            Completed process result.
        """
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            return subprocess.CompletedProcess(
                command, process.returncode, stdout.decode(), stderr.decode()
            )
            
        except Exception as e:
            logger.error(f"Error executing command {' '.join(command)}: {str(e)}")
            raise
    
    async def check_systemd_service(self: HealthChecker, service_name: str) -> HealthCheckResult:
        """Check the status of a systemd service.
        
        Args:
            service_name: Name of the systemd service to check.
            
        Returns:
            Health check result for the service.
        """
        start_time = time.time()
        
        try:
            # Check if service is active
            result = await self._run_command([
                "systemctl", "is-active", f"jaston-{service_name}.service"
            ])
            
            response_time = (time.time() - start_time) * 1000
            
            if result.returncode == 0 and result.stdout.strip() == "active":
                return HealthCheckResult(
                    service=f"systemd-{service_name}",
                    status=HealthStatus.HEALTHY,
                    message=f"Service {service_name} is active and running",
                    response_time_ms=response_time
                )
            else:
                # Get more detailed status
                status_result = await self._run_command([
                    "systemctl", "status", f"jaston-{service_name}.service", "--no-pager", "-l"
                ])
                
                return HealthCheckResult(
                    service=f"systemd-{service_name}",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Service {service_name} is not active: {result.stdout.strip()}",
                    response_time_ms=response_time,
                    details={"status_output": status_result.stdout[:500]}
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                service=f"systemd-{service_name}",
                status=HealthStatus.UNKNOWN,
                message=f"Error checking service {service_name}: {str(e)}",
                response_time_ms=response_time
            )
    
    async def check_http_endpoint(self: HealthChecker, endpoint: str, expected_status: int = 200) -> HealthCheckResult:
        """Check HTTP endpoint health.
        
        Args:
            endpoint: API endpoint to check (relative to base_url).
            expected_status: Expected HTTP status code.
            
        Returns:
            Health check result for the endpoint.
        """
        start_time = time.time()
        url = f"{self.base_url}{endpoint}"
        
        try:
            request = urllib.request.Request(url)
            request.add_header('User-Agent', 'Jaston-HealthChecker/1.0')
            
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                response_time = (time.time() - start_time) * 1000
                status_code = response.getcode()
                
                if status_code == expected_status:
                    return HealthCheckResult(
                        service=f"http-{endpoint.replace('/', '-')}",
                        status=HealthStatus.HEALTHY,
                        message=f"Endpoint {endpoint} returned expected status {status_code}",
                        response_time_ms=response_time
                    )
                else:
                    return HealthCheckResult(
                        service=f"http-{endpoint.replace('/', '-')}",
                        status=HealthStatus.DEGRADED,
                        message=f"Endpoint {endpoint} returned status {status_code}, expected {expected_status}",
                        response_time_ms=response_time
                    )
                    
        except urllib.error.HTTPError as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                service=f"http-{endpoint.replace('/', '-')}",
                status=HealthStatus.UNHEALTHY,
                message=f"HTTP error for {endpoint}: {e.code} {e.reason}",
                response_time_ms=response_time
            )
            
        except urllib.error.URLError as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                service=f"http-{endpoint.replace('/', '-')}",
                status=HealthStatus.UNHEALTHY,
                message=f"Connection error for {endpoint}: {str(e.reason)}",
                response_time_ms=response_time
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                service=f"http-{endpoint.replace('/', '-')}",
                status=HealthStatus.UNKNOWN,
                message=f"Unexpected error for {endpoint}: {str(e)}",
                response_time_ms=response_time
            )
    
    async def check_redis_connectivity(self: HealthChecker) -> HealthCheckResult:
        """Check Redis server connectivity.
        
        Returns:
            Health check result for Redis.
        """
        start_time = time.time()
        
        try:
            # Use redis-cli to ping Redis server
            result = await self._run_command([
                "redis-cli", "-h", "localhost", "-p", "6379", "ping"
            ])
            
            response_time = (time.time() - start_time) * 1000
            
            if result.returncode == 0 and "PONG" in result.stdout:
                # Get additional Redis info
                info_result = await self._run_command([
                    "redis-cli", "-h", "localhost", "-p", "6379", "info", "server"
                ])
                
                return HealthCheckResult(
                    service="redis-connectivity",
                    status=HealthStatus.HEALTHY,
                    message="Redis server is responding to ping",
                    response_time_ms=response_time,
                    details={"info": info_result.stdout[:200] if info_result.returncode == 0 else None}
                )
            else:
                return HealthCheckResult(
                    service="redis-connectivity",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Redis ping failed: {result.stdout.strip()}",
                    response_time_ms=response_time
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                service="redis-connectivity",
                status=HealthStatus.UNKNOWN,
                message=f"Error checking Redis connectivity: {str(e)}",
                response_time_ms=response_time
            )
    
    async def check_database_connectivity(self: HealthChecker) -> HealthCheckResult:
        """Check database connectivity through Django.
        
        Returns:
            Health check result for database.
        """
        start_time = time.time()
        
        try:
            # Use Django management command to check database
            project_root = Path(__file__).parent.parent.parent
            backend_dir = project_root / "backend"
            
            result = await self._run_command([
                "python3", "manage.py", "check", "--database", "default"
            ])
            
            response_time = (time.time() - start_time) * 1000
            
            if result.returncode == 0:
                return HealthCheckResult(
                    service="database-connectivity",
                    status=HealthStatus.HEALTHY,
                    message="Database connectivity check passed",
                    response_time_ms=response_time
                )
            else:
                return HealthCheckResult(
                    service="database-connectivity",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Database check failed: {result.stderr.strip()}",
                    response_time_ms=response_time
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                service="database-connectivity",
                status=HealthStatus.UNKNOWN,
                message=f"Error checking database connectivity: {str(e)}",
                response_time_ms=response_time
            )
    
    async def check_celery_workers(self: HealthChecker) -> HealthCheckResult:
        """Check Celery worker status.
        
        Returns:
            Health check result for Celery workers.
        """
        start_time = time.time()
        
        try:
            # Use celery inspect to check active workers
            project_root = Path(__file__).parent.parent.parent
            backend_dir = project_root / "backend"
            
            result = await self._run_command([
                "celery", "-A", "jaston", "inspect", "active", "--timeout=5"
            ])
            
            response_time = (time.time() - start_time) * 1000
            
            if result.returncode == 0:
                # Parse output to check for active workers
                if "OK" in result.stdout or "active" in result.stdout.lower():
                    return HealthCheckResult(
                        service="celery-workers",
                        status=HealthStatus.HEALTHY,
                        message="Celery workers are active and responding",
                        response_time_ms=response_time,
                        details={"inspect_output": result.stdout[:300]}
                    )
                else:
                    return HealthCheckResult(
                        service="celery-workers",
                        status=HealthStatus.DEGRADED,
                        message="Celery inspect succeeded but no active workers found",
                        response_time_ms=response_time
                    )
            else:
                return HealthCheckResult(
                    service="celery-workers",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Celery inspect failed: {result.stderr.strip()}",
                    response_time_ms=response_time
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                service="celery-workers",
                status=HealthStatus.UNKNOWN,
                message=f"Error checking Celery workers: {str(e)}",
                response_time_ms=response_time
            )
    
    async def check_system_resources(self: HealthChecker) -> HealthCheckResult:
        """Check system resource usage.
        
        Returns:
            Health check result for system resources.
        """
        start_time = time.time()
        
        try:
            # Check disk usage
            df_result = await self._run_command(["df", "-h", "/"])
            
            # Check memory usage
            free_result = await self._run_command(["free", "-h"])
            
            # Check load average
            uptime_result = await self._run_command(["uptime"])
            
            response_time = (time.time() - start_time) * 1000
            
            # Parse disk usage (simple check for > 90% usage)
            disk_usage_line = df_result.stdout.split('\n')[1] if df_result.returncode == 0 else ""
            disk_usage_percent = 0
            
            if disk_usage_line:
                parts = disk_usage_line.split()
                if len(parts) >= 5:
                    usage_str = parts[4].replace('%', '')
                    try:
                        disk_usage_percent = int(usage_str)
                    except ValueError:
                        pass
            
            # Determine status based on resource usage
            if disk_usage_percent > 90:
                status = HealthStatus.UNHEALTHY
                message = f"High disk usage: {disk_usage_percent}%"
            elif disk_usage_percent > 80:
                status = HealthStatus.DEGRADED
                message = f"Moderate disk usage: {disk_usage_percent}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"System resources normal (disk: {disk_usage_percent}%)"
            
            return HealthCheckResult(
                service="system-resources",
                status=status,
                message=message,
                response_time_ms=response_time,
                details={
                    "disk_usage": df_result.stdout.split('\n')[1] if df_result.returncode == 0 else "N/A",
                    "memory_usage": free_result.stdout.split('\n')[1] if free_result.returncode == 0 else "N/A",
                    "load_average": uptime_result.stdout.strip() if uptime_result.returncode == 0 else "N/A"
                }
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                service="system-resources",
                status=HealthStatus.UNKNOWN,
                message=f"Error checking system resources: {str(e)}",
                response_time_ms=response_time
            )
    
    async def run_all_checks(self: HealthChecker) -> List[HealthCheckResult]:
        """Run all health checks concurrently.
        
        Returns:
            List of all health check results.
        """
        logger.info("🔍 Running comprehensive health checks...")
        
        # Define all health checks
        checks = [
            # Systemd services
            self.check_systemd_service("redis"),
            self.check_systemd_service("django"),
            self.check_systemd_service("celery-worker"),
            self.check_systemd_service("celery-beat"),
            
            # HTTP endpoints
            self.check_http_endpoint("/api/v1/health/", 200),
            self.check_http_endpoint("/admin/", 302),  # Redirect to login
            
            # Connectivity checks
            self.check_redis_connectivity(),
            self.check_database_connectivity(),
            self.check_celery_workers(),
            
            # System resources
            self.check_system_resources()
        ]
        
        # Run all checks concurrently
        results = await asyncio.gather(*checks, return_exceptions=True)
        
        # Handle any exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(HealthCheckResult(
                    service=f"check-{i}",
                    status=HealthStatus.UNKNOWN,
                    message=f"Health check failed with exception: {str(result)}"
                ))
            else:
                final_results.append(result)
        
        return final_results
    
    def print_health_report(self: HealthChecker, results: List[HealthCheckResult]) -> None:
        """Print formatted health report.
        
        Args:
            results: List of health check results.
        """
        print("\n" + "="*80)
        print("🏥 JASTON REAL ESTATE PLATFORM - HEALTH CHECK REPORT")
        print("="*80)
        print(f"📅 Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print()
        
        # Count statuses
        status_counts = {status: 0 for status in HealthStatus}
        for result in results:
            status_counts[result.status] += 1
        
        # Overall health
        if status_counts[HealthStatus.UNHEALTHY] > 0:
            overall_status = "🔴 UNHEALTHY"
        elif status_counts[HealthStatus.DEGRADED] > 0:
            overall_status = "🟡 DEGRADED"
        elif status_counts[HealthStatus.UNKNOWN] > 0:
            overall_status = "❓ UNKNOWN"
        else:
            overall_status = "🟢 HEALTHY"
        
        print(f"🎯 Overall Status: {overall_status}")
        print(f"📊 Summary: {status_counts[HealthStatus.HEALTHY]} healthy, "
              f"{status_counts[HealthStatus.DEGRADED]} degraded, "
              f"{status_counts[HealthStatus.UNHEALTHY]} unhealthy, "
              f"{status_counts[HealthStatus.UNKNOWN]} unknown")
        print()
        
        # Detailed results
        for result in results:
            status_icon = {
                HealthStatus.HEALTHY: "🟢",
                HealthStatus.DEGRADED: "🟡",
                HealthStatus.UNHEALTHY: "🔴",
                HealthStatus.UNKNOWN: "❓"
            }.get(result.status, "❓")
            
            response_time = f" ({result.response_time_ms:.1f}ms)" if result.response_time_ms else ""
            print(f"{status_icon} {result.service:<25} {result.status.value.upper():<10} {result.message}{response_time}")
        
        print("="*80)
    
    def export_json_report(self: HealthChecker, results: List[HealthCheckResult], output_file: Optional[Path] = None) -> str:
        """Export health check results as JSON.
        
        Args:
            results: List of health check results.
            output_file: Optional output file path.
            
        Returns:
            JSON string of the health report.
        """
        # Convert results to dictionaries
        results_data = [asdict(result) for result in results]
        
        # Create report structure
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "platform": "Jaston Real Estate",
            "version": "1.0.0",
            "summary": {
                "total_checks": len(results),
                "healthy": sum(1 for r in results if r.status == HealthStatus.HEALTHY),
                "degraded": sum(1 for r in results if r.status == HealthStatus.DEGRADED),
                "unhealthy": sum(1 for r in results if r.status == HealthStatus.UNHEALTHY),
                "unknown": sum(1 for r in results if r.status == HealthStatus.UNKNOWN)
            },
            "checks": results_data
        }
        
        json_output = json.dumps(report, indent=2)
        
        if output_file:
            output_file.write_text(json_output)
            logger.info(f"Health report exported to {output_file}")
        
        return json_output


async def main() -> None:
    """Main entry point for health checker."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Jaston Real Estate Platform Health Checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                      # Run all health checks and display report
  %(prog)s --json               # Output results in JSON format
  %(prog)s --export health.json # Export results to JSON file
  %(prog)s --base-url http://localhost:8080  # Use custom base URL
        """
    )
    
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL for API health checks (default: http://localhost:8000)"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    
    parser.add_argument(
        "--export",
        type=Path,
        help="Export results to JSON file"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress non-essential output"
    )
    
    args = parser.parse_args()
    
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    # Initialize health checker
    checker = HealthChecker(base_url=args.base_url)
    
    try:
        # Run all health checks
        results = await checker.run_all_checks()
        
        if args.json or args.export:
            json_output = checker.export_json_report(results, args.export)
            if args.json:
                print(json_output)
        else:
            checker.print_health_report(results)
        
        # Exit with appropriate code
        unhealthy_count = sum(1 for r in results if r.status == HealthStatus.UNHEALTHY)
        sys.exit(1 if unhealthy_count > 0 else 0)
        
    except KeyboardInterrupt:
        logger.info("Health check cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during health check: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())