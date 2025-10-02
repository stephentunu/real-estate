# Contributing to Jaston Real Estate

Thank you for your interest in contributing to Jaston Real Estate! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Code Style and Standards](#code-style-and-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

- Python 3.13+
- Git
- WSL/Ubuntu (recommended)
- **Pyright** for Python type checking

### Development Philosophy

We follow these core principles:

- **Minimalism**: Prefer clean, vanilla solutions over external libraries
- **Quality**: All code must be performant, well-tested, and follow best practices
- **Type Safety**: **Mandatory** strict static type checking with Pyright
- **Single Source of Truth**: Centralized configuration to avoid duplication
- **Vanilla Frontend**: Pure JavaScript, HTML, and CSS - no frameworks allowed

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/eleso-solutions/jaston-real-estate.git
   cd jaston-real-estate
   ```

2. **Run the setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Activate the virtual environment**
   ```bash
   cd backend
   source venv/bin/activate
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start the development server**
   ```bash
   python manage.py runserver 8000
   ```

## Contributing Guidelines

### Types of Contributions

We welcome the following types of contributions:

- **Bug fixes**: Fix existing issues or problems
- **Feature enhancements**: Improve existing functionality
- **New features**: Add new capabilities (discuss first in issues)
- **Documentation**: Improve or add documentation
- **Tests**: Add or improve test coverage
- **Performance improvements**: Optimize existing code

### Before You Start

1. **Check existing issues** to see if your contribution is already being worked on
2. **Create an issue** for new features or significant changes to discuss the approach
3. **Fork the repository** and create a feature branch
4. **Follow our coding standards** (detailed below)

## Code Style and Standards

### Python Code Standards

#### Type Annotations
All functions and methods must include complete type annotations:

```python
from typing import Any, Self
from django.db import models

class PropertyRepository:
    """Repository for property-related database operations."""
    
    def __init__(self: Self, user: models.Model) -> None:
        """Initialize repository with user context.
        
        Args:
            user: The authenticated user for tenant isolation.
        """
        self.user = user
    
    def get_properties(self: Self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        """Retrieve properties based on filters.
        
        Args:
            filters: Dictionary of filter criteria.
            
        Returns:
            List of property dictionaries.
            
        Raises:
            ValidationError: If filters are invalid.
        """
        # Implementation here
        pass
```

#### Documentation Style
Use Google-style Python docstrings for all modules, classes, methods, and functions:

```python
def calculate_rent_amount(
    base_rent: float, 
    utilities: float = 0.0, 
    late_fee: float = 0.0
) -> float:
    """Calculate total rent amount including additional fees.
    
    Args:
        base_rent: The base monthly rent amount.
        utilities: Optional utility charges to add.
        late_fee: Optional late fee to add.
        
    Returns:
        The total rent amount.
        
    Raises:
        ValueError: If any amount is negative.
    """
    if base_rent < 0 or utilities < 0 or late_fee < 0:
        raise ValueError("Rent amounts cannot be negative")
    
    return base_rent + utilities + late_fee
```

#### Pyright Configuration
Ensure your code passes strict type checking. The project uses this configuration:

```json
{
    "typeCheckingMode": "strict",
    "reportMissingTypeStubs": false,
    "reportUnknownMemberType": false
}
```

### Frontend Standards

#### Vanilla JavaScript Only
- **Mandatory**: Use pure vanilla JavaScript (ES6+), HTML, and CSS only
- **Prohibited**: No frameworks or libraries (React, Vue, Angular, etc.)
- **Architecture**: Implement modular component-based architecture using vanilla JS
- **Type Safety**: Use JSDoc annotations for type documentation
- **Testing**: Use native browser testing APIs or lightweight testing utilities

#### CSS Standards
Follow BEM methodology with CSS custom properties:

```css
/* Use CSS custom properties for theming */
:root {
  --primary-color: #2563eb;
  --secondary-color: #64748b;
  --success-color: #10b981;
  --error-color: #ef4444;
  --font-family-base: 'Inter', system-ui, sans-serif;
  --border-radius-sm: 0.25rem;
  --border-radius-md: 0.375rem;
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
}

/* Follow BEM naming conventions */
.property-card {
  /* Component base styles */
  display: flex;
  flex-direction: column;
  border-radius: var(--border-radius-md);
}

.property-card__title {
  /* Element styles */
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
}

.property-card__price {
  /* Element styles */
  color: var(--primary-color);
  font-size: 1.25rem;
}

.property-card--featured {
  /* Modifier styles */
  border: 2px solid var(--primary-color);
}

.property-card--unavailable {
  /* Modifier styles */
  opacity: 0.6;
  pointer-events: none;
}
```

#### JavaScript Standards
```javascript
/**
 * Property management service for handling property operations.
 * @class
 */
class PropertyService {
  /**
   * Create a new property service instance.
   * @param {string} apiBaseUrl - The base URL for API requests
   */
  constructor(apiBaseUrl) {
    this.apiBaseUrl = apiBaseUrl;
    this.cache = new Map();
  }

  /**
   * Fetch properties with optional filtering.
   * @param {Object} filters - Filter criteria for properties
   * @param {string} [filters.location] - Location filter
   * @param {number} [filters.minPrice] - Minimum price filter
   * @param {number} [filters.maxPrice] - Maximum price filter
   * @returns {Promise<Array<Object>>} Array of property objects
   * @throws {Error} When API request fails
   */
  async fetchProperties(filters = {}) {
    const cacheKey = JSON.stringify(filters);
    
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    try {
      const queryParams = new URLSearchParams(filters);
      const response = await fetch(`${this.apiBaseUrl}/properties?${queryParams}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const properties = await response.json();
      this.cache.set(cacheKey, properties);
      
      return properties;
    } catch (error) {
      console.error('Failed to fetch properties:', error);
      throw error;
    }
  }
}
```

#### Icon Standards
- **Mandatory**: Use SVG icons exclusively
- **Prohibited**: No emoji usage anywhere in the codebase
- **Implementation**: Create reusable SVG icon components
- **Optimization**: Ensure SVGs are optimized for web delivery

```html
<!-- Example SVG icon component -->
<svg class="icon icon--home" viewBox="0 0 24 24" fill="none" stroke="currentColor">
  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
  <polyline points="9,22 9,12 15,12 15,22"/>
</svg>
```

### Database Standards

- Follow 3rd Normal Form (3NF) for all schema designs
- Use soft-delete patterns for data retention
- Implement proper indexing for performance
- Include migration rollback procedures

## Testing Requirements

### Test Coverage Standards
- **Minimum 90% test coverage** for critical workflows
- **100% Pyright type checking** compliance for all Python code
- **Complete JSDoc coverage** for all JavaScript functions and classes
- All new features must include comprehensive tests

### Type Checking Requirements

#### Python Type Checking (Mandatory)
All Python code must pass Pyright strict mode checking:

```bash
# Run Pyright type checking
cd backend
pyright

# Check specific files
pyright apps/properties/models.py

# Generate type checking report
pyright --outputjson > type_check_report.json
```

#### JavaScript Type Documentation
Use JSDoc annotations for type safety:

```javascript
/**
 * @typedef {Object} PropertyFilter
 * @property {string} [location] - Location filter
 * @property {number} [minPrice] - Minimum price
 * @property {number} [maxPrice] - Maximum price
 */

/**
 * Filter properties based on criteria.
 * @param {Array<Object>} properties - Array of property objects
 * @param {PropertyFilter} filters - Filter criteria
 * @returns {Array<Object>} Filtered properties
 */
function filterProperties(properties, filters) {
  // Implementation
}
```

### Test Types

#### Unit Tests (Python)
```python
# backend/apps/properties/tests/test_models.py
from typing import Any, Dict
from django.test import TestCase
from apps.properties.models import Property

class PropertyModelTest(TestCase):
    """Test cases for Property model with complete type annotations."""
    
    def test_property_creation(self: "PropertyModelTest") -> None:
        """Test property can be created with valid data.
        
        Validates that a Property instance can be created with the minimum
        required fields and that all fields are properly set.
        """
        property_data: Dict[str, Any] = {
            'title': 'Test Property',
            'address': '123 Test St',
            'rent_amount': 1500.00
        }
        property_obj: Property = Property.objects.create(**property_data)
        self.assertEqual(property_obj.title, 'Test Property')
        self.assertEqual(property_obj.rent_amount, 1500.00)
```

#### Integration Tests (Python)
```python
# backend/apps/properties/tests/test_api.py
from typing import Dict, Any
from rest_framework.test import APITestCase
from rest_framework.response import Response
from django.contrib.auth import get_user_model

User = get_user_model()

class PropertyAPITest(APITestCase):
    """Test cases for Property API endpoints with type safety."""
    
    def setUp(self: "PropertyAPITest") -> None:
        """Set up test data with proper type annotations."""
        self.user: User = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_property(self: "PropertyAPITest") -> None:
        """Test property creation via API with validation.
        
        Ensures that the API endpoint properly creates a property
        and returns the expected response format.
        """
        data: Dict[str, Any] = {
            'title': 'API Test Property',
            'address': '456 API St',
            'rent_amount': 2000.00
        }
        response: Response = self.client.post('/api/v1/properties/', data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.data)
```

#### Frontend Tests (Vanilla JavaScript)
```javascript
// frontend/src/tests/property-service.test.js

/**
 * Test suite for PropertyService class.
 * Uses native browser testing APIs for vanilla JavaScript testing.
 */
class PropertyServiceTest {
  /**
   * Set up test environment.
   */
  setUp() {
    this.mockApiUrl = 'http://localhost:8000/api/v1';
    this.propertyService = new PropertyService(this.mockApiUrl);
  }

  /**
   * Test property fetching functionality.
   * @returns {Promise<void>}
   */
  async testFetchProperties() {
    // Mock fetch API
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve([
          { id: 1, title: 'Test Property', price: 1500 }
        ])
      })
    );

    const properties = await this.propertyService.fetchProperties();
    
    console.assert(Array.isArray(properties), 'Properties should be an array');
    console.assert(properties.length === 1, 'Should return one property');
    console.assert(properties[0].title === 'Test Property', 'Property title should match');
  }

  /**
   * Run all tests.
   * @returns {Promise<void>}
   */
  async runTests() {
    this.setUp();
    await this.testFetchProperties();
    console.log('All PropertyService tests passed!');
  }
}

// Run tests
new PropertyServiceTest().runTests();
```

### Running Tests

```bash
# Backend tests with type checking
cd backend
pyright  # Type checking first
python manage.py test  # Then run tests

# Frontend tests
cd frontend
npm test  # Run vanilla JavaScript tests

# Integration tests
python infrastructure/scripts/integration_tester.py

# Complete test suite with type checking
./run_all_tests.sh  # Custom script that runs everything
```

## Pull Request Process

### Before Submitting

1. **Run all tests** and ensure they pass
2. **Run Pyright type checking** and fix all type errors
3. **Validate vanilla JavaScript** with JSDoc annotations
4. **Update documentation** if needed
5. **Add/update tests** for your changes
6. **Follow commit message conventions**
7. **Ensure SVG icons** are used instead of emojis

### Type Checking Validation

Before submitting any pull request, ensure:

```bash
# Python type checking (mandatory)
cd backend
pyright
# Must show: 0 errors, 0 warnings

# JavaScript validation (check JSDoc coverage)
cd frontend
npm run lint:js  # Custom script to validate JSDoc

# Integration validation
python infrastructure/scripts/validate_types.py
```

### Commit Message Format

```
type(scope): brief description

Detailed explanation of the changes made and why.

Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
```
feat(properties): add property search functionality

Implement search endpoint with filtering by location, price range,
and property type. Includes pagination and sorting options.

Fixes #45

fix(auth): resolve JWT token refresh issue

Token refresh was failing due to incorrect expiration validation.
Updated token validation logic to handle edge cases.

Fixes #67
```

### Pull Request Template

When creating a pull request, include:

- **Description**: What changes were made and why
- **Type of Change**: Bug fix, feature, documentation, etc.
- **Testing**: How the changes were tested
- **Checklist**: Confirm all requirements are met

### Review Process

1. **Automated checks** must pass (CI/CD pipeline)
2. **Code review** by at least one maintainer
3. **Testing verification** in staging environment
4. **Documentation review** if applicable
5. **Final approval** and merge

## Issue Reporting

### Bug Reports

When reporting bugs, include:

- **Environment**: OS, Python version, browser (if applicable)
- **Steps to reproduce**: Detailed steps to recreate the issue
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Screenshots/logs**: If applicable
- **Additional context**: Any other relevant information

### Feature Requests

When requesting features, include:

- **Problem description**: What problem does this solve?
- **Proposed solution**: How should it work?
- **Alternatives considered**: Other approaches you've thought of
- **Additional context**: Use cases, examples, etc.

## Development Workflow

### Branch Naming

- `feature/description`: New features
- `fix/description`: Bug fixes
- `docs/description`: Documentation updates
- `refactor/description`: Code refactoring
- `test/description`: Test improvements

### Development Process

1. **Create issue** (for significant changes)
2. **Create branch** from `main`
3. **Make changes** following our standards
4. **Write/update tests**
5. **Run quality checks**
6. **Submit pull request**
7. **Address review feedback**
8. **Merge after approval**

## Getting Help

- **Documentation**: Check existing docs first
- **Issues**: Search existing issues for similar problems
- **Discussions**: Use GitHub Discussions for questions
- **Email**: support@ifinsta.com for sensitive issues

## Recognition

Contributors will be recognized in:

- **CHANGELOG.md**: For significant contributions
- **README.md**: In the contributors section
- **Release notes**: For major features or fixes

Thank you for contributing to Jaston Real Estate! Your efforts help make property management better for everyone.