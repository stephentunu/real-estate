# Jaston Real Estate - Property Management Platform

A comprehensive real estate and property management platform built with Django REST Framework and vanilla JavaScript, designed to streamline property management workflows for real estate professionals, landlords, tenants, and property managers in Kenya and beyond.

## 🏠 Project Overview

Jaston Real Estate is a full-stack property management solution that provides:

- **Multi-tenant Architecture**: Secure data isolation with visibility-based access control
- **Property Management**: Complete property lifecycle management with geospatial features
- **Lease Management**: Automated lease creation, payment scheduling, and renewal workflows
- **Maintenance Requests**: Streamlined maintenance request handling with vendor management
- **Real-time Communication**: WebSocket-powered messaging and notifications
- **Document Management**: Secure document storage and verification workflows
- **Payment Processing**: Integrated wallet system with transaction management
- **Soft Delete System**: Comprehensive data retention with configurable policies

## 🚀 Technology Stack

### Backend
- **Framework**: Django 5.2.6 with Django REST Framework
- **Database**: SQLite (development) / PostgreSQL (production)
- **Real-time**: Django Channels for WebSocket communication
- **Authentication**: JWT-based authentication with refresh token rotation
- **API Documentation**: drf-yasg (Swagger/OpenAPI)
- **Task Queue**: Celery with Redis
- **Python**: 3.13+
- **Type Checking**: Pyright (strict mode enabled)

### Frontend
- **Architecture**: Vanilla JavaScript (ES6+), HTML5, and CSS3
- **Styling**: Custom CSS design system with CSS variables and BEM methodology
- **Icons**: SVG icons exclusively (no emojis)
- **Build Tool**: Vite for development and bundling
- **Package Manager**: npm
- **Type Safety**: JSDoc annotations for documentation

## 📁 Project Structure

```
jaston-real-estate/
├── frontend/                   # Vanilla JavaScript frontend application
│   ├── src/                   # Source code
│   │   ├── components/        # Reusable UI components (vanilla JS)
│   │   ├── pages/            # Page components
│   │   ├── services/         # API service layer
│   │   ├── utils/            # Utility functions
│   │   ├── styles/           # CSS design system
│   │   └── assets/           # SVG icons and static assets
│   ├── public/               # Static assets
│   ├── tsconfig.json         # TypeScript configuration for tooling
│   ├── tsconfig.app.json     # Application-specific TypeScript config
│   ├── tsconfig.node.json    # Node.js TypeScript config
│   ├── vite.config.ts        # Vite build configuration
│   └── package.json          # Frontend dependencies
├── backend/                   # Django REST API
│   ├── apps/                 # Django applications
│   │   ├── users/            # User management and authentication
│   │   ├── properties/       # Property management
│   │   ├── leases/           # Lease management
│   │   ├── maintenance/      # Maintenance requests
│   │   ├── messaging/        # Real-time messaging
│   │   ├── documents/        # Document management
│   │   ├── payments/         # Payment processing
│   │   ├── notifications/    # Notification system
│   │   ├── contacts/         # Contact management
│   │   ├── team/             # Team member management
│   │   ├── appointments/     # Appointment scheduling
│   │   ├── core/             # Core utilities and base classes
│   │   ├── requirements.txt  # Backend dependencies
│   │   └── manage.py         # Django management script
│   ├── config/               # Centralized configuration
│   │   ├── database.py       # Database configuration
│   │   ├── cache_config.py   # Redis and caching
│   │   ├── security_config.py # Security settings
│   │   └── drf_config.py     # DRF configuration
│   ├── pyrightconfig.json    # Pyright type checking configuration
│   └── venv/                 # Python virtual environment
├── infrastructure/           # Setup and deployment scripts
│   ├── scripts/              # Management scripts
│   │   ├── backend_checker.py    # Backend environment validation
│   │   ├── frontend_checker.py   # Frontend environment validation
│   │   ├── integration_tester.py # Integration testing
│   │   └── service_manager.py    # Service lifecycle management
│   ├── logs/                 # Application logs
│   └── setup.py              # Main setup script
└── .github/                  # GitHub Actions workflows
    └── workflows/
        ├── ci.yml            # Continuous Integration
        ├── test.yml          # Automated Testing
        └── quality.yml       # Code Quality Checks

```

## 🛠️ Development Setup

### Prerequisites

- **Python 3.13+**
- **Node.js 18+** and npm
- **PostgreSQL** (for production)
- **Redis** (for caching and task queue)
- **Pyright** (for Python type checking)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Start development server**:
   ```bash
   python manage.py runserver
   ```

   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173`

### Type Checking

**Backend (Pyright)**:
```bash
cd backend
pyright
```

**Frontend (TypeScript for tooling)**:
```bash
cd frontend
npx tsc --noEmit
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### Integration Tests
```bash
cd frontend
node test-integration.js
```

### Type Checking Tests
```bash
# Backend type checking
cd backend
pyright

# Frontend TypeScript validation
cd frontend
npx tsc --noEmit
```

## 📚 API Documentation

Once the backend is running, API documentation is available at:
- **Swagger UI**: `http://localhost:8000/swagger/`
- **ReDoc**: `http://localhost:8000/redoc/`

## 🏗️ Architecture Highlights

### Multi-tenant Design
- **Visibility Mixins**: Automatic data isolation based on user roles
- **Tenant-aware APIs**: All endpoints respect tenant boundaries
- **Flexible Permissions**: Role-based access control with custom permissions

### Real-time Features
- **WebSocket Integration**: Live messaging and notifications
- **Event-driven Architecture**: Automatic updates across connected clients
- **Scalable Design**: Redis-backed channel layers for horizontal scaling

### Data Management
- **Soft Delete Pattern**: Configurable retention policies for deleted data
- **Audit Trail**: Complete change tracking for compliance
- **Geospatial Support**: Location-based property search and mapping

## 🤝 Contributing

We welcome contributions from the community! Please follow these guidelines:

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following our coding standards
4. **Write tests** for new functionality
5. **Run the test suite** to ensure nothing breaks
6. **Submit a pull request** with a clear description

### Code Standards

- **Python**: Follow PEP 8 with Pyright strict mode type checking
- **JavaScript**: Use ES6+ with JSDoc annotations for documentation
- **CSS**: Follow BEM methodology with CSS variables for theming
- **Testing**: Maintain >90% test coverage for critical workflows
- **Documentation**: Update relevant documentation for new features
- **Icons**: Use SVG format exclusively (no emojis or raster images)

### Commit Convention

Use conventional commits for clear history:
```
feat: add property search filtering
fix: resolve lease payment calculation bug
docs: update API documentation
test: add integration tests for messaging
```

## 📋 Available Scripts

### Backend
- `python manage.py runserver` - Start development server
- `python manage.py test` - Run test suite
- `python manage.py migrate` - Apply database migrations
- `python manage.py collectstatic` - Collect static files

### Frontend
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run test` - Run frontend tests
- `npx tsc --noEmit` - TypeScript type checking

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### Production Deployment

For production deployment, ensure:
- Set `DEBUG=False`
- Use PostgreSQL database
- Configure proper CORS settings
- Set up SSL certificates
- Configure Redis for production use

## 📞 Support

For questions, issues, or contributions:

- **Email**: support@ifinsta.com
- **Company**: Eleso Solutions
- **Issues**: Use GitHub Issues for bug reports and feature requests

## 📄 License

This project is proprietary software developed by Eleso Solutions. All rights reserved.

---

**Built with ❤️ by the Eleso Solutions team**
