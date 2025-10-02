#!/usr/bin/env python3
"""
Frontend Environment Checker for Jaston Real Estate Platform

This module provides comprehensive frontend environment validation including:
- Node.js version and package manager checks
- Package dependency verification
- Build tool configuration validation
- Development server setup checks
- Asset and build optimization validation

Author: Douglas Mutethia (Eleso Solutions)
Version: 1.0.0
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class FrontendCheck:
    """Result of a frontend environment check."""
    name: str
    passed: bool
    message: str
    severity: str = "error"  # error, warning, info
    fix_suggestion: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class FrontendEnvironmentChecker:
    """Comprehensive frontend environment checker."""
    
    def __init__(self, project_root: Path) -> None:
        """Initialize the frontend checker.
        
        Args:
            project_root: Path to the project root directory.
        """
        self.project_root = project_root
        self.frontend_dir = project_root / "frontend"
        self.package_json = self.frontend_dir / "package.json"
        self.node_modules = self.frontend_dir / "node_modules"
        self.vite_config = self.frontend_dir / "vite.config.ts"
        self.tsconfig = self.frontend_dir / "tsconfig.json"
        
        # Required Node.js version
        self.min_node_version = (18, 0)
        self.recommended_node_version = (20, 0)
        
        # Critical dependencies for the project
        self.critical_dependencies = {
            'react': '^18.0.0',
            'react-dom': '^18.0.0',
            'vite': '^5.0.0',
            'typescript': '^5.0.0',
            '@types/react': '^18.0.0',
            '@types/react-dom': '^18.0.0'
        }
        
        # Recommended development dependencies
        self.recommended_dev_deps = {
            'eslint': 'Code quality',
            'prettier': 'Code formatting',
            '@vitejs/plugin-react': 'React support for Vite',
            'tailwindcss': 'CSS framework',
            'autoprefixer': 'CSS vendor prefixes'
        }

    async def run_all_checks(self) -> List[FrontendCheck]:
        """Run all frontend environment checks.
        
        Returns:
            List of check results.
        """
        logger.info("🌐 Running comprehensive frontend environment checks...")
        
        checks: List[FrontendCheck] = []
        
        # Core Node.js checks
        checks.extend(await self._check_node_environment())
        
        # Package manager checks
        checks.extend(await self._check_package_managers())
        
        # Project structure checks
        checks.extend(await self._check_project_structure())
        
        # Dependencies checks
        checks.extend(await self._check_dependencies())
        
        # Configuration checks
        checks.extend(await self._check_configuration())
        
        # Build system checks
        checks.extend(await self._check_build_system())
        
        # Development server checks
        checks.extend(await self._check_dev_server())
        
        # Performance and optimization checks
        checks.extend(await self._check_performance_settings())
        
        return checks

    async def _run_command(self, command: List[str], cwd: Optional[Path] = None, timeout: int = 30) -> Tuple[bool, str, str]:
        """Run a shell command and return success status and output.
        
        Args:
            command: Command to run as list of strings.
            cwd: Working directory for the command.
            timeout: Command timeout in seconds.
            
        Returns:
            Tuple of (success, stdout, stderr).
        """
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd or self.frontend_dir
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
            
            return (
                process.returncode == 0,
                stdout.decode('utf-8').strip(),
                stderr.decode('utf-8').strip()
            )
        except asyncio.TimeoutError:
            return False, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return False, "", str(e)

    async def _check_node_environment(self) -> List[FrontendCheck]:
        """Check Node.js version and environment."""
        checks = []
        
        # Check if Node.js is installed
        node_available = shutil.which('node') is not None
        
        if not node_available:
            checks.append(FrontendCheck(
                name="Node.js Installation",
                passed=False,
                message="Node.js not found in PATH",
                severity="error",
                fix_suggestion="Install Node.js from https://nodejs.org/ or use nvm"
            ))
            return checks
        
        # Check Node.js version
        success, stdout, stderr = await self._run_command(['node', '--version'])
        
        if not success:
            checks.append(FrontendCheck(
                name="Node.js Version Check",
                passed=False,
                message=f"Failed to get Node.js version: {stderr}",
                severity="error",
                fix_suggestion="Reinstall Node.js"
            ))
            return checks
        
        try:
            # Parse version (format: v18.17.0)
            version_str = stdout.strip().lstrip('v')
            version_parts = version_str.split('.')
            current_version = (int(version_parts[0]), int(version_parts[1]))
            
            if current_version < self.min_node_version:
                checks.append(FrontendCheck(
                    name="Node.js Version",
                    passed=False,
                    message=f"Node.js {version_str} is below minimum required version {self.min_node_version[0]}.{self.min_node_version[1]}",
                    severity="error",
                    fix_suggestion=f"Upgrade to Node.js {self.recommended_node_version[0]}.{self.recommended_node_version[1]} or higher"
                ))
            elif current_version < self.recommended_node_version:
                checks.append(FrontendCheck(
                    name="Node.js Version",
                    passed=True,
                    message=f"Node.js {version_str} (recommended: {self.recommended_node_version[0]}.{self.recommended_node_version[1]}+)",
                    severity="warning",
                    fix_suggestion=f"Consider upgrading to Node.js {self.recommended_node_version[0]}.{self.recommended_node_version[1]} for better performance"
                ))
            else:
                checks.append(FrontendCheck(
                    name="Node.js Version",
                    passed=True,
                    message=f"Node.js {version_str} ✅",
                    severity="info"
                ))
                
            # Check Node.js executable location
            node_path = shutil.which('node')
            checks.append(FrontendCheck(
                name="Node.js Executable",
                passed=True,
                message=f"Using Node.js at: {node_path}",
                severity="info",
                details={"executable_path": node_path, "version": version_str}
            ))
            
        except (ValueError, IndexError) as e:
            checks.append(FrontendCheck(
                name="Node.js Version Parsing",
                passed=False,
                message=f"Failed to parse Node.js version: {stdout}",
                severity="error",
                fix_suggestion="Reinstall Node.js"
            ))
        
        return checks

    async def _check_package_managers(self) -> List[FrontendCheck]:
        """Check available package managers."""
        checks = []
        
        # Check npm
        npm_available = shutil.which('npm') is not None
        if npm_available:
            success, stdout, stderr = await self._run_command(['npm', '--version'])
            if success:
                checks.append(FrontendCheck(
                    name="npm Package Manager",
                    passed=True,
                    message=f"npm {stdout} available",
                    severity="info",
                    details={"version": stdout}
                ))
            else:
                checks.append(FrontendCheck(
                    name="npm Package Manager",
                    passed=False,
                    message=f"npm found but not working: {stderr}",
                    severity="warning",
                    fix_suggestion="Reinstall npm"
                ))
        else:
            checks.append(FrontendCheck(
                name="npm Package Manager",
                passed=False,
                message="npm not found",
                severity="error",
                fix_suggestion="Install npm (usually comes with Node.js)"
            ))
        
        # Check bun (optional but recommended)
        bun_available = shutil.which('bun') is not None
        if bun_available:
            success, stdout, stderr = await self._run_command(['bun', '--version'])
            if success:
                checks.append(FrontendCheck(
                    name="Bun Package Manager",
                    passed=True,
                    message=f"Bun {stdout} available (recommended for faster builds)",
                    severity="info",
                    details={"version": stdout}
                ))
            else:
                checks.append(FrontendCheck(
                    name="Bun Package Manager",
                    passed=True,
                    message="Bun found but not working properly",
                    severity="warning",
                    fix_suggestion="Reinstall Bun from https://bun.sh/"
                ))
        else:
            checks.append(FrontendCheck(
                name="Bun Package Manager",
                passed=True,
                message="Bun not installed (optional but recommended)",
                severity="info",
                fix_suggestion="Install Bun for faster package management: curl -fsSL https://bun.sh/install | bash"
            ))
        
        # Check yarn (optional)
        yarn_available = shutil.which('yarn') is not None
        if yarn_available:
            success, stdout, stderr = await self._run_command(['yarn', '--version'])
            if success:
                checks.append(FrontendCheck(
                    name="Yarn Package Manager",
                    passed=True,
                    message=f"Yarn {stdout} available",
                    severity="info",
                    details={"version": stdout}
                ))
        
        return checks

    async def _check_project_structure(self) -> List[FrontendCheck]:
        """Check frontend project structure."""
        checks = []
        
        # Check if frontend directory exists
        if not self.frontend_dir.exists():
            checks.append(FrontendCheck(
                name="Frontend Directory",
                passed=False,
                message="Frontend directory not found",
                severity="error",
                fix_suggestion="Create frontend directory and initialize project"
            ))
            return checks
        
        checks.append(FrontendCheck(
            name="Frontend Directory",
            passed=True,
            message="Frontend directory exists",
            severity="info"
        ))
        
        # Check package.json
        if not self.package_json.exists():
            checks.append(FrontendCheck(
                name="package.json",
                passed=False,
                message="package.json not found",
                severity="error",
                fix_suggestion="Initialize project: npm init or create React app"
            ))
            return checks
        
        checks.append(FrontendCheck(
            name="package.json",
            passed=True,
            message="package.json found",
            severity="info"
        ))
        
        # Check essential directories
        essential_dirs = {
            'src': 'Source code directory',
            'public': 'Public assets directory'
        }
        
        for dir_name, description in essential_dirs.items():
            dir_path = self.frontend_dir / dir_name
            if dir_path.exists():
                checks.append(FrontendCheck(
                    name=f"Directory: {dir_name}",
                    passed=True,
                    message=f"{description} exists",
                    severity="info"
                ))
            else:
                checks.append(FrontendCheck(
                    name=f"Directory: {dir_name}",
                    passed=False,
                    message=f"{description} not found",
                    severity="warning",
                    fix_suggestion=f"Create {dir_name} directory"
                ))
        
        # Check essential files
        essential_files = {
            'index.html': 'Main HTML file',
            'src/main.tsx': 'Main TypeScript entry point',
            'src/App.tsx': 'Main App component'
        }
        
        for file_path, description in essential_files.items():
            full_path = self.frontend_dir / file_path
            if full_path.exists():
                checks.append(FrontendCheck(
                    name=f"File: {file_path}",
                    passed=True,
                    message=f"{description} exists",
                    severity="info"
                ))
            else:
                checks.append(FrontendCheck(
                    name=f"File: {file_path}",
                    passed=False,
                    message=f"{description} not found",
                    severity="warning",
                    fix_suggestion=f"Create {file_path}"
                ))
        
        return checks

    async def _check_dependencies(self) -> List[FrontendCheck]:
        """Check package dependencies."""
        checks = []
        
        # Parse package.json
        try:
            with open(self.package_json, 'r') as f:
                package_data = json.load(f)
        except Exception as e:
            checks.append(FrontendCheck(
                name="package.json Parsing",
                passed=False,
                message=f"Error parsing package.json: {str(e)}",
                severity="error",
                fix_suggestion="Fix syntax errors in package.json"
            ))
            return checks
        
        checks.append(FrontendCheck(
            name="package.json Parsing",
            passed=True,
            message="package.json parsed successfully",
            severity="info"
        ))
        
        # Check dependencies
        dependencies = package_data.get('dependencies', {})
        dev_dependencies = package_data.get('devDependencies', {})
        all_deps = {**dependencies, **dev_dependencies}
        
        checks.append(FrontendCheck(
            name="Dependencies Count",
            passed=True,
            message=f"Found {len(dependencies)} dependencies and {len(dev_dependencies)} dev dependencies",
            severity="info",
            details={
                "dependencies": len(dependencies),
                "devDependencies": len(dev_dependencies),
                "total": len(all_deps)
            }
        ))
        
        # Check critical dependencies
        missing_critical = []
        for dep_name, min_version in self.critical_dependencies.items():
            if dep_name not in all_deps:
                missing_critical.append(dep_name)
                checks.append(FrontendCheck(
                    name=f"Critical Dependency: {dep_name}",
                    passed=False,
                    message=f"{dep_name} not installed",
                    severity="error",
                    fix_suggestion=f"Install {dep_name}: npm install {dep_name}"
                ))
            else:
                checks.append(FrontendCheck(
                    name=f"Critical Dependency: {dep_name}",
                    passed=True,
                    message=f"{dep_name} {all_deps[dep_name]} installed",
                    severity="info"
                ))
        
        # Check recommended dev dependencies
        for dep_name, purpose in self.recommended_dev_deps.items():
            if dep_name not in all_deps:
                checks.append(FrontendCheck(
                    name=f"Recommended: {dep_name}",
                    passed=True,
                    message=f"{dep_name} not installed ({purpose})",
                    severity="info",
                    fix_suggestion=f"Consider installing {dep_name}: npm install --save-dev {dep_name}"
                ))
            else:
                checks.append(FrontendCheck(
                    name=f"Recommended: {dep_name}",
                    passed=True,
                    message=f"{dep_name} installed ({purpose})",
                    severity="info"
                ))
        
        # Check node_modules
        if not self.node_modules.exists():
            checks.append(FrontendCheck(
                name="node_modules",
                passed=False,
                message="node_modules directory not found",
                severity="error",
                fix_suggestion="Install dependencies: npm install"
            ))
        else:
            # Count installed packages
            try:
                installed_packages = len([d for d in self.node_modules.iterdir() if d.is_dir() and not d.name.startswith('.')])
                checks.append(FrontendCheck(
                    name="node_modules",
                    passed=True,
                    message=f"node_modules exists with {installed_packages} packages",
                    severity="info",
                    details={"installed_packages": installed_packages}
                ))
            except Exception:
                checks.append(FrontendCheck(
                    name="node_modules",
                    passed=True,
                    message="node_modules exists",
                    severity="info"
                ))
        
        return checks

    async def _check_configuration(self) -> List[FrontendCheck]:
        """Check configuration files."""
        checks = []
        
        # Check Vite configuration
        if self.vite_config.exists():
            checks.append(FrontendCheck(
                name="Vite Configuration",
                passed=True,
                message="vite.config.ts found",
                severity="info"
            ))
            
            # Try to parse Vite config
            try:
                with open(self.vite_config, 'r') as f:
                    config_content = f.read()
                    
                if '@vitejs/plugin-react' in config_content:
                    checks.append(FrontendCheck(
                        name="Vite React Plugin",
                        passed=True,
                        message="React plugin configured in Vite",
                        severity="info"
                    ))
                else:
                    checks.append(FrontendCheck(
                        name="Vite React Plugin",
                        passed=False,
                        message="React plugin not found in Vite config",
                        severity="warning",
                        fix_suggestion="Add @vitejs/plugin-react to vite.config.ts"
                    ))
                    
            except Exception as e:
                checks.append(FrontendCheck(
                    name="Vite Configuration Parsing",
                    passed=False,
                    message=f"Error reading Vite config: {str(e)}",
                    severity="warning"
                ))
        else:
            checks.append(FrontendCheck(
                name="Vite Configuration",
                passed=False,
                message="vite.config.ts not found",
                severity="error",
                fix_suggestion="Create vite.config.ts with React plugin configuration"
            ))
        
        # Check TypeScript configuration
        if self.tsconfig.exists():
            checks.append(FrontendCheck(
                name="TypeScript Configuration",
                passed=True,
                message="tsconfig.json found",
                severity="info"
            ))
            
            try:
                with open(self.tsconfig, 'r') as f:
                    ts_config = json.load(f)
                    
                compiler_options = ts_config.get('compilerOptions', {})
                
                # Check important TypeScript settings
                if compiler_options.get('strict'):
                    checks.append(FrontendCheck(
                        name="TypeScript Strict Mode",
                        passed=True,
                        message="Strict mode enabled",
                        severity="info"
                    ))
                else:
                    checks.append(FrontendCheck(
                        name="TypeScript Strict Mode",
                        passed=True,
                        message="Strict mode not enabled",
                        severity="warning",
                        fix_suggestion="Enable strict mode in tsconfig.json for better type safety"
                    ))
                
                if compiler_options.get('jsx') == 'react-jsx':
                    checks.append(FrontendCheck(
                        name="TypeScript JSX Configuration",
                        passed=True,
                        message="JSX configured for React",
                        severity="info"
                    ))
                    
            except Exception as e:
                checks.append(FrontendCheck(
                    name="TypeScript Configuration Parsing",
                    passed=False,
                    message=f"Error parsing tsconfig.json: {str(e)}",
                    severity="warning",
                    fix_suggestion="Fix syntax errors in tsconfig.json"
                ))
        else:
            checks.append(FrontendCheck(
                name="TypeScript Configuration",
                passed=False,
                message="tsconfig.json not found",
                severity="error",
                fix_suggestion="Create tsconfig.json for TypeScript configuration"
            ))
        
        # Check other configuration files
        config_files = {
            'tailwind.config.js': 'Tailwind CSS configuration',
            'postcss.config.js': 'PostCSS configuration',
            '.eslintrc.json': 'ESLint configuration',
            '.prettierrc': 'Prettier configuration'
        }
        
        for config_file, description in config_files.items():
            config_path = self.frontend_dir / config_file
            if config_path.exists():
                checks.append(FrontendCheck(
                    name=f"Config: {config_file}",
                    passed=True,
                    message=f"{description} found",
                    severity="info"
                ))
            else:
                checks.append(FrontendCheck(
                    name=f"Config: {config_file}",
                    passed=True,
                    message=f"{description} not found (optional)",
                    severity="info",
                    fix_suggestion=f"Consider adding {config_file} for {description.lower()}"
                ))
        
        return checks

    async def _check_build_system(self) -> List[FrontendCheck]:
        """Check build system configuration."""
        checks = []
        
        # Check package.json scripts
        try:
            with open(self.package_json, 'r') as f:
                package_data = json.load(f)
                
            scripts = package_data.get('scripts', {})
            
            # Check essential scripts
            essential_scripts = {
                'dev': 'Development server',
                'build': 'Production build',
                'preview': 'Preview production build',
                'lint': 'Code linting'
            }
            
            for script_name, description in essential_scripts.items():
                if script_name in scripts:
                    checks.append(FrontendCheck(
                        name=f"Script: {script_name}",
                        passed=True,
                        message=f"{description} script configured",
                        severity="info",
                        details={"command": scripts[script_name]}
                    ))
                else:
                    severity = "error" if script_name in ['dev', 'build'] else "warning"
                    checks.append(FrontendCheck(
                        name=f"Script: {script_name}",
                        passed=script_name not in ['dev', 'build'],
                        message=f"{description} script not configured",
                        severity=severity,
                        fix_suggestion=f"Add {script_name} script to package.json"
                    ))
            
            # Test build command
            if 'build' in scripts:
                checks.append(FrontendCheck(
                    name="Build Command Test",
                    passed=True,
                    message="Build command available for testing",
                    severity="info",
                    fix_suggestion="Run 'npm run build' to test production build"
                ))
                
        except Exception as e:
            checks.append(FrontendCheck(
                name="Build Scripts Check",
                passed=False,
                message=f"Error checking build scripts: {str(e)}",
                severity="error"
            ))
        
        return checks

    async def _check_dev_server(self) -> List[FrontendCheck]:
        """Check development server configuration."""
        checks = []
        
        # Check if dev server can be started (without actually starting it)
        try:
            with open(self.package_json, 'r') as f:
                package_data = json.load(f)
                
            scripts = package_data.get('scripts', {})
            
            if 'dev' in scripts:
                dev_command = scripts['dev']
                
                # Check if it's using Vite
                if 'vite' in dev_command:
                    checks.append(FrontendCheck(
                        name="Development Server",
                        passed=True,
                        message="Vite development server configured",
                        severity="info",
                        details={"command": dev_command}
                    ))
                else:
                    checks.append(FrontendCheck(
                        name="Development Server",
                        passed=True,
                        message=f"Development server configured: {dev_command}",
                        severity="info",
                        details={"command": dev_command}
                    ))
                
                # Check for common dev server configurations
                if '--host' in dev_command or '--host 0.0.0.0' in dev_command:
                    checks.append(FrontendCheck(
                        name="Dev Server Host Configuration",
                        passed=True,
                        message="Development server configured for external access",
                        severity="info"
                    ))
                else:
                    checks.append(FrontendCheck(
                        name="Dev Server Host Configuration",
                        passed=True,
                        message="Development server using default host (localhost)",
                        severity="info",
                        fix_suggestion="Consider adding --host 0.0.0.0 for external access"
                    ))
                    
            else:
                checks.append(FrontendCheck(
                    name="Development Server",
                    passed=False,
                    message="No development server script configured",
                    severity="error",
                    fix_suggestion="Add 'dev' script to package.json"
                ))
                
        except Exception as e:
            checks.append(FrontendCheck(
                name="Development Server Check",
                passed=False,
                message=f"Error checking dev server configuration: {str(e)}",
                severity="warning"
            ))
        
        return checks

    async def _check_performance_settings(self) -> List[FrontendCheck]:
        """Check performance and optimization settings."""
        checks = []
        
        # Check for performance-related configurations
        perf_files = {
            '.env': 'Environment variables',
            '.env.local': 'Local environment overrides',
            '.gitignore': 'Git ignore rules'
        }
        
        for file_name, description in perf_files.items():
            file_path = self.frontend_dir / file_name
            if file_path.exists():
                checks.append(FrontendCheck(
                    name=f"Performance File: {file_name}",
                    passed=True,
                    message=f"{description} configured",
                    severity="info"
                ))
                
                # Check .gitignore content
                if file_name == '.gitignore':
                    try:
                        with open(file_path, 'r') as f:
                            gitignore_content = f.read()
                            
                        if 'node_modules' in gitignore_content:
                            checks.append(FrontendCheck(
                                name="Git Ignore node_modules",
                                passed=True,
                                message="node_modules properly ignored",
                                severity="info"
                            ))
                        else:
                            checks.append(FrontendCheck(
                                name="Git Ignore node_modules",
                                passed=False,
                                message="node_modules not in .gitignore",
                                severity="warning",
                                fix_suggestion="Add node_modules to .gitignore"
                            ))
                            
                        if 'dist' in gitignore_content or 'build' in gitignore_content:
                            checks.append(FrontendCheck(
                                name="Git Ignore Build Output",
                                passed=True,
                                message="Build output properly ignored",
                                severity="info"
                            ))
                        else:
                            checks.append(FrontendCheck(
                                name="Git Ignore Build Output",
                                passed=False,
                                message="Build output not in .gitignore",
                                severity="warning",
                                fix_suggestion="Add dist/ or build/ to .gitignore"
                            ))
                            
                    except Exception:
                        pass
            else:
                severity = "warning" if file_name == '.gitignore' else "info"
                checks.append(FrontendCheck(
                    name=f"Performance File: {file_name}",
                    passed=file_name != '.gitignore',
                    message=f"{description} not found",
                    severity=severity,
                    fix_suggestion=f"Create {file_name} for {description.lower()}"
                ))
        
        # Check for bundle analysis tools
        try:
            with open(self.package_json, 'r') as f:
                package_data = json.load(f)
                
            all_deps = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}
            
            bundle_analyzers = ['webpack-bundle-analyzer', 'rollup-plugin-analyzer', 'vite-bundle-analyzer']
            has_analyzer = any(analyzer in all_deps for analyzer in bundle_analyzers)
            
            if has_analyzer:
                checks.append(FrontendCheck(
                    name="Bundle Analysis",
                    passed=True,
                    message="Bundle analyzer available",
                    severity="info"
                ))
            else:
                checks.append(FrontendCheck(
                    name="Bundle Analysis",
                    passed=True,
                    message="No bundle analyzer configured (optional)",
                    severity="info",
                    fix_suggestion="Consider adding a bundle analyzer for optimization"
                ))
                
        except Exception:
            pass
        
        return checks

    def generate_report(self, checks: List[FrontendCheck]) -> Dict[str, Any]:
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
    checker = FrontendEnvironmentChecker(project_root)
    
    checks = await checker.run_all_checks()
    report = checker.generate_report(checks)
    
    # Print summary
    print("\n" + "="*60)
    print("🌐 FRONTEND ENVIRONMENT CHECK REPORT")
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
    report_file = project_root / "frontend_check_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_file}")


if __name__ == "__main__":
    asyncio.run(main())