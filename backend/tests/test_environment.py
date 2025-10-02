"""
Tests for the environment configuration system.

This module tests the centralized environment loader, validation,
and configuration management functionality.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from config.environment import (
    EnvironmentLoader,
    EnvironmentType,
    ValidationError,
    DatabaseConfig,
    ServerConfig,
    SecurityConfig,
    get_env_loader,
    validate_environment,
)


class TestEnvironmentLoader(unittest.TestCase):
    """Test cases for the EnvironmentLoader class."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.env_file = Path(self.temp_dir) / '.env'
        
        # Create a test .env file
        self.env_file.write_text("""
# Test environment configuration
APP_ENV=development
SECRET_KEY=test-secret-key-that-is-long-enough-for-validation
DEBUG=true
DB_ENGINE=sqlite
DB_NAME=test.db
SERVER_HOST=localhost
SERVER_PORT=8000
ALLOWED_HOSTS=localhost,127.0.0.1
        """.strip())
        
        self.loader = EnvironmentLoader(self.env_file)
    
    def tearDown(self) -> None:
        """Clean up test fixtures."""
        if self.env_file.exists():
            self.env_file.unlink()
        Path(self.temp_dir).rmdir()
    
    def test_get_string_with_default(self) -> None:
        """Test get_string with default value when variable is not set."""
        with patch.dict(os.environ, {}, clear=True):
            loader = EnvironmentLoader()
            result = loader.get_string('MISSING_VAR', default='development')
            self.assertEqual(result, 'development')
    
    def test_get_string_required_missing(self) -> None:
        """Test that missing required string raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            self.loader.get_string('MISSING_REQUIRED_VAR')
        
        self.assertIn('MISSING_REQUIRED_VAR', str(context.exception))
        self.assertIn('missing or empty', str(context.exception))
    
    def test_get_int_valid(self) -> None:
        """Test get_int with valid integer string."""
        with patch.dict(os.environ, {'SERVER_PORT': '8000'}):
            loader = EnvironmentLoader()
            result = loader.get_int('SERVER_PORT')
            self.assertEqual(result, 8000)
    
    def test_get_int_invalid(self) -> None:
        """Test that invalid integer raises ValidationError."""
        # Add invalid integer to env file
        self.env_file.write_text(self.env_file.read_text() + '\nINVALID_INT=not_a_number')
        
        with self.assertRaises(ValidationError) as context:
            self.loader.get_int('INVALID_INT')
        
        self.assertIn('valid integer', str(context.exception))
    
    def test_get_bool_valid(self) -> None:
        """Test getting valid boolean values."""
        result = self.loader.get_bool('DEBUG', required=False)
        self.assertTrue(result)
        self.assertIsInstance(result, bool)
    
    def test_get_list_valid(self) -> None:
        """Test get_list with valid comma-separated values."""
        with patch.dict(os.environ, {'ALLOWED_HOSTS': 'localhost,127.0.0.1'}):
            loader = EnvironmentLoader()
            result = loader.get_list('ALLOWED_HOSTS')
            self.assertEqual(result, ['localhost', '127.0.0.1'])
    
    def test_get_environment_type_valid(self) -> None:
        """Test getting valid environment type."""
        result = self.loader.get_environment_type()
        self.assertEqual(result, EnvironmentType.DEVELOPMENT)
    
    def test_get_environment_type_invalid(self) -> None:
        """Test invalid environment type raises ValidationError."""
        with patch.dict(os.environ, {'APP_ENV': 'invalid'}, clear=True):
            loader = EnvironmentLoader()
            with self.assertRaises(ValidationError) as context:
                loader.get_environment_type()
            self.assertIn("Invalid environment type", str(context.exception))


class TestDatabaseConfig(unittest.TestCase):
    """Test cases for DatabaseConfig validation."""
    
    def test_sqlite_config_valid(self) -> None:
        """Test valid SQLite configuration."""
        config = DatabaseConfig(
            engine='sqlite',
            name='test.db',
            user='',
            password='',
            host='',
            port=0
        )
        
        # Should not raise any exception
        config.validate()
    
    def test_postgresql_config_valid(self) -> None:
        """Test valid PostgreSQL configuration."""
        config = DatabaseConfig(
            engine='postgresql',
            name='testdb',
            user='testuser',
            password='testpass',
            host='localhost',
            port=5432
        )
        
        # Should not raise any exception
        config.validate()
    
    def test_postgresql_config_missing_credentials(self) -> None:
        """Test PostgreSQL configuration with missing credentials."""
        config = DatabaseConfig(
            engine='postgresql',
            name='testdb',
            user='',  # Missing user
            password='testpass',
            host='localhost',
            port=5432
        )
        
        with self.assertRaises(ValidationError) as context:
            config.validate()
        
        self.assertIn('PostgreSQL requires', str(context.exception))
    
    def test_invalid_engine(self) -> None:
        """Test configuration with invalid database engine."""
        config = DatabaseConfig(
            engine='mysql',  # Unsupported engine
            name='testdb',
            user='testuser',
            password='testpass',
            host='localhost',
            port=3306
        )
        
        with self.assertRaises(ValidationError) as context:
            config.validate()
        
        self.assertIn('Unsupported database engine', str(context.exception))


class TestServerConfig(unittest.TestCase):
    """Test cases for ServerConfig validation."""
    
    def test_valid_server_config(self) -> None:
        """Test valid server configuration."""
        config = ServerConfig(
            host='localhost',
            port=8000,
            allowed_hosts=['localhost', '127.0.0.1']
        )
        
        # Should not raise any exception
        config.validate()
    
    def test_invalid_port(self) -> None:
        """Test server configuration with invalid port."""
        config = ServerConfig(
            host='localhost',
            port=70000,  # Invalid port
            allowed_hosts=['localhost']
        )
        
        with self.assertRaises(ValidationError) as context:
            config.validate()
        
        self.assertIn('Invalid port number', str(context.exception))
    
    def test_empty_allowed_hosts(self) -> None:
        """Test server configuration with empty allowed hosts."""
        config = ServerConfig(
            host='localhost',
            port=8000,
            allowed_hosts=[]  # Empty allowed hosts
        )
        
        with self.assertRaises(ValidationError) as context:
            config.validate()
        
        self.assertIn('ALLOWED_HOSTS cannot be empty', str(context.exception))


class TestSecurityConfig(unittest.TestCase):
    """Test cases for SecurityConfig validation."""
    
    def test_valid_security_config(self) -> None:
        """Test valid security configuration."""
        config = SecurityConfig(
            secret_key='a-very-long-secret-key-that-meets-minimum-requirements',
            debug=False
        )
        
        # Should not raise any exception
        config.validate()
    
    def test_short_secret_key(self) -> None:
        """Test security configuration with short secret key."""
        config = SecurityConfig(
            secret_key='short',  # Too short
            debug=False
        )
        
        with self.assertRaises(ValidationError) as context:
            config.validate()
        
        self.assertIn('at least 32 characters', str(context.exception))
    
    @patch.dict(os.environ, {'APP_ENV': 'production'})
    def test_debug_in_production(self) -> None:
        """Test security configuration with debug enabled in production."""
        config = SecurityConfig(
            secret_key='a-very-long-secret-key-that-meets-minimum-requirements',
            debug=True  # Debug enabled in production
        )
        
        with self.assertRaises(ValidationError) as context:
            config.validate()
        
        self.assertIn('DEBUG cannot be True in production', str(context.exception))


class TestGlobalFunctions(unittest.TestCase):
    """Test cases for global environment functions."""
    
    def test_get_env_loader_singleton(self) -> None:
        """Test that get_env_loader returns the same instance."""
        loader1 = get_env_loader()
        loader2 = get_env_loader()
        
        self.assertIs(loader1, loader2)
    
    @patch('config.environment.get_env_loader')
    def test_validate_environment_success(self, mock_get_loader: MagicMock) -> None:
        """Test successful environment validation."""
        mock_loader = MagicMock()
        mock_get_loader.return_value = mock_loader
        
        # Should not raise any exception
        validate_environment()
        
        mock_loader.validate_all.assert_called_once()
    
    @patch('config.environment.get_env_loader')
    def test_validate_environment_failure(self, mock_get_loader: MagicMock) -> None:
        """Test environment validation failure."""
        mock_loader = MagicMock()
        mock_loader.validate_all.side_effect = ValidationError("Test validation error")
        mock_get_loader.return_value = mock_loader
        
        with self.assertRaises(ValidationError) as context:
            validate_environment()
        
        self.assertIn('Test validation error', str(context.exception))


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test cases for complete environment scenarios."""
    
    def test_complete_development_environment(self) -> None:
        """Test complete development environment setup."""
        temp_dir = tempfile.mkdtemp()
        env_file = Path(temp_dir) / '.env'
        
        try:
            # Create complete development .env file
            env_file.write_text("""
APP_ENV=development
SECRET_KEY=development-secret-key-that-is-long-enough-for-validation-requirements
DEBUG=true
DB_ENGINE=sqlite
DB_NAME=dev.db
SERVER_HOST=localhost
SERVER_PORT=8000
ALLOWED_HOSTS=localhost,127.0.0.1,*.example.com
            """.strip())
            
            loader = EnvironmentLoader(env_file)
            
            # Test all configuration sections
            env_type = loader.get_environment_type()
            db_config = loader.get_database_config()
            server_config = loader.get_server_config()
            security_config = loader.get_security_config()
            
            # Validate all configurations
            self.assertEqual(env_type, EnvironmentType.DEVELOPMENT)
            self.assertEqual(db_config.engine, 'sqlite')
            self.assertEqual(server_config.port, 8000)
            self.assertTrue(security_config.debug)
            
            # Test complete validation
            loader.validate_all()
            self.assertTrue(loader.is_validated)
            
        finally:
            if env_file.exists():
                env_file.unlink()
            Path(temp_dir).rmdir()
    
    def test_complete_production_environment(self) -> None:
        """Test complete production environment setup."""
        temp_dir = tempfile.mkdtemp()
        env_file = Path(temp_dir) / '.env'
        
        try:
            # Create complete production .env file
            env_file.write_text("""
APP_ENV=production
SECRET_KEY=production-secret-key-that-is-very-long-and-secure-for-production-use
DEBUG=false
DB_ENGINE=postgresql
DB_NAME=jaston_prod
DB_USER=jaston_user
DB_PASSWORD=secure_password_123
DB_HOST=db.example.com
DB_PORT=5432
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
ALLOWED_HOSTS=jaston.com,www.jaston.com,api.jaston.com
            """.strip())
            
            loader = EnvironmentLoader(env_file)
            
            # Test all configuration sections
            env_type = loader.get_environment_type()
            db_config = loader.get_database_config()
            server_config = loader.get_server_config()
            security_config = loader.get_security_config()
            
            # Validate all configurations
            self.assertEqual(env_type, EnvironmentType.PRODUCTION)
            self.assertEqual(db_config.engine, 'postgresql')
            self.assertEqual(db_config.user, 'jaston_user')
            self.assertFalse(security_config.debug)
            
            # Test complete validation
            loader.validate_all()
            self.assertTrue(loader.is_validated)
            
        finally:
            if env_file.exists():
                env_file.unlink()
            Path(temp_dir).rmdir()


if __name__ == '__main__':
    unittest.main()