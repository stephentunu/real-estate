"""Centralized environment configuration loader for the Jaston Real Estate platform.

This module provides a modular, type-safe approach to loading and validating
environment variables with proper error handling and defaults.
"""

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from decouple import config, Csv


class EnvironmentType(Enum):
    """Supported environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class ValidationError(Exception):
    """Raised when environment validation fails."""
    pass


@dataclass(frozen=True)
class DatabaseConfig:
    """Database configuration settings."""
    engine: str
    name: str
    user: str
    password: str
    host: str
    port: int
    
    def validate(self) -> None:
        """Validate database configuration."""
        valid_engines = [
            'sqlite',
            'postgresql',
            'django.db.backends.sqlite3',
            'django.db.backends.postgresql'
        ]
        if self.engine not in valid_engines:
            raise ValidationError(f"Unsupported database engine: {self.engine}")
        
        if self.engine == 'postgresql':
            if not all([self.user, self.password, self.host]):
                raise ValidationError("PostgreSQL requires user, password, and host")
            if not (1 <= self.port <= 65535):
                raise ValidationError(f"Invalid port number: {self.port}")


@dataclass(frozen=True)
class ServerConfig:
    """Server configuration settings."""
    host: str
    port: int
    allowed_hosts: List[str]
    
    def validate(self) -> None:
        """Validate server configuration."""
        if not (1 <= self.port <= 65535):
            raise ValidationError(f"Invalid port number: {self.port}")
        
        if not self.allowed_hosts:
            raise ValidationError("ALLOWED_HOSTS cannot be empty")


@dataclass(frozen=True)
class SecurityConfig:
    """Security configuration settings."""
    secret_key: str
    debug: bool
    
    def validate(self) -> None:
        """Validate security configuration."""
        if len(self.secret_key) < 32:
            raise ValidationError("SECRET_KEY must be at least 32 characters long")
        
        if self.debug and os.getenv('APP_ENV') == 'production':
            raise ValidationError("DEBUG cannot be True in production environment")


class EnvironmentLoader:
    """
    Centralized environment variable loader with validation and type safety.
    
    This class provides a single point of access for all environment variables
    used throughout the application, with proper validation and error handling.
    """
    
    def __init__(self, env_file_path: Optional[Path] = None) -> None:
        """
        Initialize the environment loader.
        
        Args:
            env_file_path: Optional path to the .env file. Defaults to project root.
        """
        if env_file_path is None:
            # Default to project root .env file
            current_dir = Path(__file__).parent.parent.parent
            env_file_path = current_dir / '.env'
        
        self.env_file_path = env_file_path
        self._validated = False
        
        # Load the .env file if it exists
        if self.env_file_path.exists():
            from decouple import Config, RepositoryEnv
            self.config = Config(RepositoryEnv(str(self.env_file_path)))
        else:
            self.config = config
    
    def get_string(self, key: str, default: Optional[str] = None, required: bool = True) -> str:
        """
        Get a string environment variable.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            required: Whether the variable is required
            
        Returns:
            String value from environment
            
        Raises:
            ValidationError: If required variable is missing
        """
        try:
            value = self.config(key, default=default)
            if required and (value is None or value == ''):
                raise ValidationError(f"Required environment variable '{key}' is missing or empty")
            return str(value) if value is not None else ''
        except Exception as e:
            if required:
                raise ValidationError(f"Error loading environment variable '{key}': {e}")
            return default or ''
    
    def get_int(self, key: str, default: Optional[int] = None, required: bool = True) -> int:
        """
        Get an integer environment variable.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            required: Whether the variable is required
            
        Returns:
            Integer value from environment
            
        Raises:
            ValidationError: If required variable is missing or invalid
        """
        try:
            value = self.config(key, default=default, cast=int)
            
            if required and value is None:
                raise ValidationError(f"Environment variable '{key}' is required but not defined")
            
            return value
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Environment variable '{key}' must be a valid integer: {e}")
    
    def get_bool(self, key: str, default: Optional[bool] = None, required: bool = True) -> bool:
        """
        Get a boolean environment variable.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            required: Whether the variable is required
            
        Returns:
            Boolean value from environment
            
        Raises:
            ValidationError: If required variable is missing or invalid
        """
        try:
            value = self.config(key, default=default, cast=bool)
            if required and value is None:
                raise ValidationError(f"Environment variable '{key}' is required but not defined")
            return value
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Environment variable '{key}' must be a valid boolean: {e}")
    
    def get_list(self, key: str, default: Optional[List[str]] = None, required: bool = True) -> List[str]:
        """
        Get a comma-separated list environment variable.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            required: Whether the variable is required
            
        Returns:
            List of strings from environment
            
        Raises:
            ValidationError: If required variable is missing
        """
        value_str = self.config(key, default=None)
        
        if value_str is None:
            if required:
                raise ValidationError(f"Environment variable '{key}' is required but not defined")
            return default or []
        
        # Split by comma and strip whitespace
        return [item.strip() for item in value_str.split(',') if item.strip()]
    
    def get_environment_type(self) -> EnvironmentType:
        """
        Get the current environment type.
        
        Returns:
            EnvironmentType enum value
            
        Raises:
            ValidationError: If environment type is invalid
        """
        env_value = self.get_string('APP_ENV', default='development', required=False)
        
        try:
            return EnvironmentType(env_value)
        except ValueError:
            raise ValidationError(f"Invalid environment type: {env_value}. Must be one of: {', '.join([e.value for e in EnvironmentType])}")
    
    def get_database_config(self) -> DatabaseConfig:
        """
        Get database configuration.
        
        Returns:
            DatabaseConfig instance with validated settings
            
        Raises:
            ValidationError: If database configuration is invalid
        """
        config_obj = DatabaseConfig(
            engine=self.get_string('DB_ENGINE', default='sqlite', required=False),
            name=self.get_string('DB_NAME', default='db.sqlite3', required=False),
            user=self.get_string('DB_USER', default='', required=False),
            password=self.get_string('DB_PASSWORD', default='', required=False),
            host=self.get_string('DB_HOST', default='localhost', required=False),
            port=self.get_int('DB_PORT', default=5432, required=False),
        )
        config_obj.validate()
        return config_obj
    
    def get_server_config(self) -> ServerConfig:
        """
        Get server configuration.
        
        Returns:
            ServerConfig instance with validated settings
            
        Raises:
            ValidationError: If server configuration is invalid
        """
        config_obj = ServerConfig(
            host=self.get_string('SERVER_HOST', default='localhost', required=False),
            port=self.get_int('SERVER_PORT', default=8000, required=False),
            allowed_hosts=self.get_list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'], required=False),
        )
        config_obj.validate()
        return config_obj
    
    def get_security_config(self) -> SecurityConfig:
        """
        Get security configuration.
        
        Returns:
            SecurityConfig instance with validated settings
            
        Raises:
            ValidationError: If security configuration is invalid
        """
        config_obj = SecurityConfig(
            secret_key=self.get_string('SECRET_KEY'),
            debug=self.get_bool('DEBUG', default=False, required=False),
        )
        config_obj.validate()
        return config_obj
    
    def validate_all(self) -> None:
        """
        Validate all environment configurations.
        
        This method loads and validates all configuration sections,
        ensuring the environment is properly set up.
        
        Raises:
            ValidationError: If any configuration is invalid
        """
        try:
            # Validate core configurations
            self.get_environment_type()
            self.get_database_config()
            self.get_server_config()
            self.get_security_config()
            
            self._validated = True
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Unexpected error during environment validation: {e}")
    
    @property
    def is_validated(self) -> bool:
        """Check if environment has been validated."""
        return self._validated


# Global environment loader instance
_env_loader: Optional[EnvironmentLoader] = None


def get_env_loader() -> EnvironmentLoader:
    """
    Get the global environment loader instance.
    
    Returns:
        EnvironmentLoader instance
    """
    global _env_loader
    if _env_loader is None:
        _env_loader = EnvironmentLoader()
    return _env_loader


def validate_environment() -> None:
    """
    Validate the entire environment configuration.
    
    This function should be called during application startup
    to ensure all environment variables are properly configured.
    
    Raises:
        ValidationError: If environment validation fails
    """
    loader = get_env_loader()
    loader.validate_all()