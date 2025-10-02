#!/usr/bin/env python3
"""
Jaston Real Estate Platform - Dynamic SystemD Service Generator

This module provides a type-safe, template-based system for generating
systemd service files from configuration data. It uses Jinja2 templates
and JSON configuration files to create consistent, maintainable service
definitions.

Author: Douglas Mutethia <support@ifinsta.com>
Company: Eleso Solutions
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Self

from jinja2 import Environment, FileSystemLoader, select_autoescape


class ServiceType(Enum):
    """Enumeration of supported service types."""
    DJANGO = "django"
    CELERY_WORKER = "celery-worker"
    CELERY_BEAT = "celery-beat"
    REDIS = "redis"


class EnvironmentType(Enum):
    """Enumeration of deployment environments."""
    DEVELOPMENT = "development"
    PRODUCTION = "production"


@dataclass
class ServiceConfig:
    """Configuration data for a single service."""
    name: str
    description: str
    service_type: ServiceType
    working_directory: str
    exec_start: str
    dependencies: List[str] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)
    resources: Dict[str, Union[str, int]] = field(default_factory=dict)
    
    def __post_init__(self: Self) -> None:
        """Validate service configuration after initialization."""
        if not self.name:
            raise ValueError("Service name cannot be empty")
        if not self.description:
            raise ValueError("Service description cannot be empty")
        if not self.exec_start:
            raise ValueError("Service exec_start cannot be empty")


@dataclass
class ProjectConfig:
    """Project-wide configuration settings."""
    name: str
    display_name: str
    root_dir: str
    user: str
    group: str
    
    def __post_init__(self: Self) -> None:
        """Validate project configuration after initialization."""
        if not all([self.name, self.display_name, self.root_dir, self.user, self.group]):
            raise ValueError("All project configuration fields are required")


class ServiceGeneratorError(Exception):
    """Custom exception for service generator errors."""
    pass


class ConfigurationError(ServiceGeneratorError):
    """Exception raised for configuration-related errors."""
    pass


class TemplateError(ServiceGeneratorError):
    """Exception raised for template-related errors."""
    pass


class ServiceGenerator:
    """
    Type-safe service generator for creating systemd service files from templates.
    
    This class handles loading configuration files, rendering Jinja2 templates,
    and generating systemd service files with proper error handling and validation.
    """
    
    def __init__(
        self: Self,
        config_dir: Union[str, Path],
        template_dir: Union[str, Path],
        output_dir: Union[str, Path],
        environment: EnvironmentType = EnvironmentType.DEVELOPMENT
    ) -> None:
        """
        Initialize the service generator.
        
        Args:
            config_dir: Directory containing configuration JSON files
            template_dir: Directory containing Jinja2 templates
            output_dir: Directory where generated service files will be written
            environment: Target deployment environment
            
        Raises:
            ConfigurationError: If directories don't exist or are invalid
        """
        self.config_dir = Path(config_dir)
        self.template_dir = Path(template_dir)
        self.output_dir = Path(output_dir)
        self.environment = environment
        
        # Validate directories
        self._validate_directories()
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Load configurations
        self._base_config: Dict[str, Any] = {}
        self._env_config: Dict[str, Any] = {}
        self._services_config: Dict[str, Any] = {}
        self._load_configurations()
    
    def _validate_directories(self: Self) -> None:
        """
        Validate that required directories exist.
        
        Raises:
            ConfigurationError: If any required directory doesn't exist
        """
        if not self.config_dir.exists():
            raise ConfigurationError(f"Configuration directory not found: {self.config_dir}")
        if not self.template_dir.exists():
            raise ConfigurationError(f"Template directory not found: {self.template_dir}")
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_configurations(self: Self) -> None:
        """
        Load all configuration files.
        
        Raises:
            ConfigurationError: If configuration files are missing or invalid
        """
        try:
            # Load base configuration
            base_config_path = self.config_dir / "base.json"
            if not base_config_path.exists():
                raise ConfigurationError(f"Base configuration not found: {base_config_path}")
            
            with open(base_config_path, 'r', encoding='utf-8') as f:
                self._base_config = json.load(f)
            
            # Load environment-specific configuration
            env_config_path = self.config_dir / f"{self.environment.value}.json"
            if env_config_path.exists():
                with open(env_config_path, 'r', encoding='utf-8') as f:
                    self._env_config = json.load(f)
            
            # Load services configuration
            services_config_path = self.config_dir / "services.json"
            if not services_config_path.exists():
                raise ConfigurationError(f"Services configuration not found: {services_config_path}")
            
            with open(services_config_path, 'r', encoding='utf-8') as f:
                self._services_config = json.load(f)
                
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in configuration file: {e}")
        except IOError as e:
            raise ConfigurationError(f"Error reading configuration file: {e}")
    
    def _merge_configs(self: Self, service_name: str) -> Dict[str, Any]:
        """
        Merge base, environment, and service-specific configurations.
        
        Args:
            service_name: Name of the service to generate config for
            
        Returns:
            Merged configuration dictionary
            
        Raises:
            ConfigurationError: If service configuration is not found
        """
        if service_name not in self._services_config:
            raise ConfigurationError(f"Service configuration not found: {service_name}")
        
        # Start with base configuration
        merged_config = self._base_config.copy()
        
        # Deep merge environment-specific overrides
        self._deep_merge(merged_config, self._env_config)
        
        # Add service-specific configuration
        merged_config['service'] = self._services_config[service_name].copy()
        
        return merged_config
    
    def _deep_merge(self: Self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """
        Recursively merge two dictionaries.
        
        Args:
            base: Base dictionary to merge into
            override: Dictionary with override values
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _get_template_name(self: Self, service_type: ServiceType) -> str:
        """
        Get the template filename for a service type.
        
        Args:
            service_type: Type of service
            
        Returns:
            Template filename
        """
        return f"{service_type.value}.service.j2"
    
    def generate_service(self: Self, service_name: str) -> Path:
        """
        Generate a systemd service file for the specified service.
        
        Args:
            service_name: Name of the service to generate
            
        Returns:
            Path to the generated service file
            
        Raises:
            ConfigurationError: If service configuration is invalid
            TemplateError: If template rendering fails
        """
        try:
            # Merge configurations
            config = self._merge_configs(service_name)
            
            # Determine service type
            service_config = config['service']
            service_type_str = service_name.replace('jaston-', '')
            
            try:
                service_type = ServiceType(service_type_str)
            except ValueError:
                # Default to base template for unknown service types
                template_name = "base.service.j2"
            else:
                template_name = self._get_template_name(service_type)
            
            # Load and render template
            try:
                template = self.jinja_env.get_template(template_name)
            except Exception as e:
                # Fallback to base template if specific template not found
                self.logger.warning(f"Template {template_name} not found, using base template: {e}")
                template = self.jinja_env.get_template("base.service.j2")
            
            rendered_content = template.render(**config)
            
            # Write generated service file
            output_file = self.output_dir / f"{service_config['name']}.service"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(rendered_content)
            
            self.logger.info(f"Generated service file: {output_file}")
            return output_file
            
        except Exception as e:
            if isinstance(e, (ConfigurationError, TemplateError)):
                raise
            raise TemplateError(f"Error generating service {service_name}: {e}")
    
    def generate_all_services(self: Self) -> List[Path]:
        """
        Generate systemd service files for all configured services.
        
        Returns:
            List of paths to generated service files
            
        Raises:
            ServiceGeneratorError: If any service generation fails
        """
        generated_files: List[Path] = []
        errors: List[str] = []
        
        for service_name in self._services_config.keys():
            try:
                service_file = self.generate_service(service_name)
                generated_files.append(service_file)
            except Exception as e:
                error_msg = f"Failed to generate {service_name}: {e}"
                errors.append(error_msg)
                self.logger.error(error_msg)
        
        if errors:
            raise ServiceGeneratorError(f"Service generation failed: {'; '.join(errors)}")
        
        return generated_files
    
    def list_available_services(self: Self) -> List[str]:
        """
        Get a list of all available services that can be generated.
        
        Returns:
            List of service names
        """
        return list(self._services_config.keys())
    
    def validate_configuration(self: Self) -> bool:
        """
        Validate all loaded configurations.
        
        Returns:
            True if all configurations are valid
            
        Raises:
            ConfigurationError: If any configuration is invalid
        """
        # Validate project configuration
        project_config = self._base_config.get('project', {})
        required_project_fields = ['name', 'display_name', 'root_dir', 'user', 'group']
        
        for field in required_project_fields:
            if not project_config.get(field):
                raise ConfigurationError(f"Missing required project field: {field}")
        
        # Validate service configurations
        for service_name, service_config in self._services_config.items():
            required_service_fields = ['name', 'description', 'exec_start']
            
            for field in required_service_fields:
                if not service_config.get(field):
                    raise ConfigurationError(f"Missing required field '{field}' in service '{service_name}'")
        
        return True


def main() -> None:
    """
    Command-line interface for the service generator.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate systemd service files from templates")
    parser.add_argument("--config-dir", default="configs", help="Configuration directory")
    parser.add_argument("--template-dir", default="templates", help="Template directory")
    parser.add_argument("--output-dir", default="generated", help="Output directory")
    parser.add_argument("--environment", choices=["development", "production"], 
                       default="development", help="Target environment")
    parser.add_argument("--service", help="Generate specific service (default: all)")
    parser.add_argument("--validate", action="store_true", help="Validate configurations only")
    parser.add_argument("--list", action="store_true", help="List available services")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    
    try:
        # Initialize generator
        generator = ServiceGenerator(
            config_dir=args.config_dir,
            template_dir=args.template_dir,
            output_dir=args.output_dir,
            environment=EnvironmentType(args.environment)
        )
        
        if args.list:
            services = generator.list_available_services()
            print("Available services:")
            for service in services:
                print(f"  - {service}")
            return
        
        if args.validate:
            generator.validate_configuration()
            print("Configuration validation passed")
            return
        
        # Generate services
        if args.service:
            service_file = generator.generate_service(args.service)
            print(f"Generated: {service_file}")
        else:
            service_files = generator.generate_all_services()
            print(f"Generated {len(service_files)} service files:")
            for service_file in service_files:
                print(f"  - {service_file}")
                
    except ServiceGeneratorError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()