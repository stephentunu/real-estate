# Configuration Management

This directory contains centralized configuration utilities for the Jaston Real Estate platform, following Django 5.2.6+ best practices and strict type checking with Pyright.

## Overview

The `config/` directory provides modular configuration management for different aspects of the Django application, enabling clean separation of concerns and environment-specific settings.

## Configuration Modules

### Core Configuration

- **`database.py`** - Database connection and configuration management
- **`cache_config.py`** - Redis caching and session storage configuration
- **`logging_config.py`** - Structured logging with file rotation and levels
- **`security_config.py`** - CORS, CSRF, security headers, and authentication

### Framework Configuration

- **`drf_config.py`** - Django REST Framework API settings and documentation
- **`channels_config.py`** - WebSocket and real-time messaging configuration
- **`celery_config.py`** - Background task processing and periodic tasks

### Deployment Configuration

- **`deployment.py`** - Environment-specific settings, static files, email, and performance

## Usage Examples

### In Django Settings

```python
from config.database import get_database_config
from config.cache_config import get_cache_config, get_session_config
from config.security_config import get_cors_config, get_csrf_config
from config.drf_config import get_drf_config

# Database configuration
DATABASES = get_database_config()

# Cache configuration
CACHES = get_cache_config()

# Session configuration
globals().update(get_session_config())

# Security configuration
globals().update(get_cors_config())
globals().update(get_csrf_config())

# DRF configuration
REST_FRAMEWORK = get_drf_config()
```

### Environment Variables

Each configuration module respects environment variables for customization:

```bash
# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=jaston_re_prod
DB_USER=jaston_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432

# Cache & Sessions
REDIS_URL=redis://localhost:6379/1
CACHE_TIMEOUT=300

# Security
DEBUG=False
SECRET_KEY=your-secret-key
CORS_ALLOWED_ORIGINS=https://jastonrealestate.com,https://api.jastonrealestate.com

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=noreply@jastonrealestate.com
EMAIL_HOST_PASSWORD=app_password
```

## Type Safety

All configuration functions include complete type annotations and follow Pyright strict mode requirements:

```python
from typing import Any, Dict

def get_database_config() -> Dict[str, Any]:
    """
    Get database configuration based on environment.
    
    Returns:
        Database configuration dictionary for Django settings.
        
    Raises:
        ValueError: If required database environment variables are missing.
    """
```

## Testing Configuration

Each module provides test-specific configuration functions:

```python
from config.database import get_test_database_config
from config.cache_config import get_test_cache_config
from config.celery_config import get_test_celery_config

# In test settings
DATABASES = get_test_database_config()
CACHES = get_test_cache_config()
CELERY = get_test_celery_config()
```

## Best Practices

1. **Environment Variables**: Use `python-decouple` for environment variable management
2. **Type Safety**: All functions include complete type annotations
3. **Documentation**: Follow Google-style docstrings with type information
4. **Separation**: Keep related configurations grouped in dedicated modules
5. **Testing**: Provide test-specific configurations for all modules
6. **Security**: Never commit sensitive values; use environment variables

## Integration with Settings

The configuration modules are designed to integrate seamlessly with Django settings:

```python
# settings.py
from config.database import get_database_config
from config.logging_config import get_logging_config
from config.deployment import get_static_files_config, get_media_files_config

# Apply configurations
DATABASES = get_database_config()
LOGGING = get_logging_config()
globals().update(get_static_files_config())
globals().update(get_media_files_config())
```

## Extending Configuration

To add new configuration modules:

1. Create a new Python file in the `config/` directory
2. Follow the established patterns with type annotations
3. Provide both production and test configurations
4. Include comprehensive docstrings
5. Update this README with usage examples

## Support

For questions or issues with configuration management:
- **Email**: support@ifinsta.com
- **Company**: Eleso Solutions
- **Documentation**: See individual module docstrings for detailed usage