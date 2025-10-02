# Infrastructure Directory

This directory contains all setup-related scripts, configuration files, and logs for the Jaston Real Estate platform.

## Directory Structure

```
infrastructure/
├── scripts/           # Setup and management scripts
│   ├── backend_checker.py      # Backend environment validation
│   ├── exception_handler.py    # Global exception handling
│   ├── frontend_checker.py     # Frontend environment validation
│   ├── integration_tester.py   # Comprehensive integration testing
│   └── service_manager.py      # Service lifecycle management
├── logs/             # Application and setup logs
│   ├── setup.log     # Setup process logs
│   └── errors.log    # Error logs
└── setup.py          # Main setup script

```

## Usage

### Running the Setup Script

From the project root directory:

```bash
# Full setup (recommended for first-time setup)
python3 infrastructure/setup.py

# Run integration tests only
python3 infrastructure/setup.py --test-only

# Show help
python3 infrastructure/setup.py --help
```

### Available Commands

- `python3 infrastructure/setup.py` - Run full platform setup
- `python3 infrastructure/setup.py --test-only` - Run integration tests only
- `python3 infrastructure/setup.py --stop` - Stop all services
- `python3 infrastructure/setup.py --restart` - Restart services
- `python3 infrastructure/setup.py --help` - Show help information

## Scripts Overview

### setup.py
Main orchestration script that handles:
- Environment validation
- Backend and frontend setup
- Service management
- Health checks
- Integration testing

### Scripts Directory

- **backend_checker.py**: Validates Python environment, Django setup, and database configuration
- **frontend_checker.py**: Validates Node.js environment and frontend dependencies
- **service_manager.py**: Manages Django, Redis, Celery, and frontend development servers
- **integration_tester.py**: Comprehensive end-to-end testing framework
- **exception_handler.py**: Global exception handling and recovery strategies

## Logs Directory

All application logs are centralized in the `logs/` directory:
- `setup.log`: Complete setup process logs
- `errors.log`: Error-specific logs for debugging

## Design Principles

This infrastructure follows the project's core principles:
- **Minimalism**: Clean, focused scripts with minimal dependencies
- **Type Safety**: Full type annotations using Pyright strict mode
- **Single Source of Truth**: Centralized configuration management
- **Quality**: Comprehensive testing and error handling