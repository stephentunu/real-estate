# Frontend Documentation - Jaston Real Estate

A modern React TypeScript frontend application for the Jaston Real Estate property management platform, built with Vite, shadcn/ui components, and Tailwind CSS.

## 🎯 Architecture Overview

The frontend follows a **modern React architecture** with TypeScript, emphasizing:

- **Type Safety**: Full TypeScript coverage with strict type checking
- **Performance**: Vite-powered development and optimized production builds
- **Component Library**: shadcn/ui components with Radix UI primitives
- **Styling**: Tailwind CSS with custom design system integration
- **State Management**: TanStack Query for server state and React Context for client state

## 🏗️ Project Structure

```
frontend/
├── src/                        # Source code
│   ├── components/            # React components
│   │   ├── ui/               # shadcn/ui base components
│   │   ├── messaging/        # Messaging-related components
│   │   ├── ApplyNowModal.tsx # Property application modal
│   │   ├── AuthButton.tsx    # Authentication button component
│   │   ├── DashboardLayout.tsx # Dashboard layout wrapper
│   │   ├── ErrorBoundary.ts  # Error boundary component
│   │   ├── Footer.tsx        # Site footer component
│   │   ├── GoogleSignIn.tsx  # Google OAuth integration
│   │   ├── ImagePreview.tsx  # Image preview component
│   │   ├── Layout.tsx        # Main layout component
│   │   ├── LoadingStates.ts  # Loading state components
│   │   ├── Navbar.tsx        # Navigation bar component
│   │   ├── NewsletterAdmin.jsx # Newsletter administration
│   │   ├── NewsletterSubscription.jsx # Newsletter subscription
│   │   ├── PropertyCard.tsx  # Property display card
│   │   ├── ProtectedRoute.tsx # Route protection wrapper
│   │   ├── RoleBasedFeatures.tsx # Role-based feature access
│   │   ├── ScheduleTourModal.tsx # Tour scheduling modal
│   │   └── SearchBar.tsx     # Property search component
│   ├── pages/                # Page components
│   │   ├── dashboard/        # Dashboard-specific pages
│   │   ├── AboutPage.tsx     # About page
│   │   ├── AuthPage.tsx      # Authentication page
│   │   ├── BlogPage.tsx      # Blog listing page
│   │   ├── CareersPage.tsx   # Careers page
│   │   ├── CitiesPage.tsx    # Cities listing page
│   │   ├── ContactPage.tsx   # Contact page
│   │   ├── CookiesPage.tsx   # Cookie policy page
│   │   ├── DashboardPage.tsx # Main dashboard page
│   │   ├── HelpCenterPage.tsx # Help center page
│   │   ├── Index.tsx         # Home page
│   │   ├── ListPropertyPage.tsx # Property listing page
│   │   ├── NewsletterPage.jsx # Newsletter page
│   │   ├── NotFound.tsx      # 404 error page
│   │   ├── PrivacyPolicyPage.tsx # Privacy policy page
│   │   ├── PropertiesPage.tsx # Properties listing page
│   │   ├── PropertyPage.tsx  # Individual property page
│   │   ├── SearchPage.tsx    # Property search page
│   │   ├── ServicesPage.tsx  # Services page
│   │   ├── SignInPage.tsx    # Sign in page
│   │   ├── SignUpPage.tsx    # Sign up page
│   │   ├── TeamPage.tsx      # Team page
│   │   └── TermsPage.tsx     # Terms of service page
│   ├── services/             # API service layer
│   │   ├── apiClient.ts      # Base API client configuration
│   │   ├── appointmentService.ts # Appointment API services
│   │   ├── authService.ts    # Authentication services
│   │   ├── blogService.ts    # Blog API services
│   │   ├── cityService.ts    # City API services
│   │   ├── dashboardService.ts # Dashboard API services
│   │   ├── errors.ts         # Error handling utilities
│   │   ├── featureService.ts # Feature flag services
│   │   ├── interceptors.ts   # HTTP request/response interceptors
│   │   ├── leaseService.ts   # Lease management services
│   │   ├── maintenanceService.ts # Maintenance API services
│   │   ├── messageService.ts # Messaging services
│   │   ├── newsletterService.js # Newsletter services
│   │   ├── notificationService.ts # Notification services
│   │   ├── propertyService.ts # Property API services
│   │   ├── teamService.ts    # Team management services
│   │   └── websocketService.ts # WebSocket connection management
│   ├── contexts/             # React Context providers
│   │   └── AuthContext.tsx   # Authentication context
│   ├── hooks/                # Custom React hooks
│   │   ├── use-mobile.tsx    # Mobile detection hook
│   │   ├── use-toast.ts      # Toast notification hook
│   │   └── useFeatures.ts    # Feature flag hook
│   ├── lib/                  # Utility libraries
│   │   └── utils.ts          # General utility functions
│   ├── utils/                # Additional utilities
│   │   └── errorHandler.ts   # Error handling utilities
│   ├── tests/                # Test files
│   │   └── integration.test.ts # Integration tests
│   ├── App.css               # Global application styles
│   ├── App.tsx               # Main App component
│   ├── index.css             # Global CSS imports
│   ├── main.tsx              # Application entry point
│   └── vite-env.d.ts         # Vite environment types
├── public/                   # Static public assets
│   ├── favicon.ico           # Favicon
│   ├── placeholder.svg       # Placeholder SVG
│   └── robots.txt            # Robots.txt file
├── components.json           # shadcn/ui configuration
├── eslint.config.js          # ESLint configuration
├── index.html                # Main HTML template
├── postcss.config.js         # PostCSS configuration
├── tailwind.config.ts        # Tailwind CSS configuration
├── test-integration.js       # Integration test runner
├── tsconfig.json             # TypeScript configuration
├── tsconfig.app.json         # Application TypeScript config
├── tsconfig.node.json        # Node.js TypeScript config
├── vite.config.ts            # Vite build configuration
├── package.json              # Dependencies and scripts
└── README.md                 # This documentation
```

## 🚀 Getting Started

### Prerequisites

- **Node.js 18+** and npm
- **Modern browser** with ES6+ support

### Installation

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

   The application will be available at `http://localhost:5173`

### Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run test` - Run test suite
- `npx tsc --noEmit` - TypeScript type checking (tooling validation)

## 🎨 Design System

### CSS Architecture

The frontend uses a **custom CSS design system** with:

- **CSS Variables**: Centralized theming and color management
- **BEM Methodology**: Block, Element, Modifier naming convention
- **Mobile-First**: Responsive design starting from mobile breakpoints
- **Component-Based**: Modular CSS matching JavaScript components

### CSS Variables (Theme System)

```css
:root {
  /* Colors */
  --color-primary: #2563eb;
  --color-primary-hover: #1d4ed8;
  --color-secondary: #64748b;
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  
  /* Typography */
  --font-family-sans: 'Inter', system-ui, sans-serif;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  
  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  
  /* Breakpoints */
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
}
```

### BEM Naming Convention

```css
/* Block */
.property-card { }

/* Element */
.property-card__title { }
.property-card__image { }
.property-card__price { }

/* Modifier */
.property-card--featured { }
.property-card__title--large { }
```

## 🧩 Component Architecture

### React Component Structure

Components follow React best practices with TypeScript:

```typescript
import React from 'react';

interface PropertyCardProps {
  property: Property;
  onSelect?: (property: Property) => void;
  className?: string;
}

/**
 * PropertyCard component for displaying property information
 * @param property - Property data object
 * @param onSelect - Optional callback when property is selected
 * @param className - Additional CSS classes
 */
export const PropertyCard: React.FC<PropertyCardProps> = ({ 
  property, 
  onSelect, 
  className 
}) => {
  const handleClick = () => {
    onSelect?.(property);
  };

  return (
    <div 
      className={`property-card ${className || ''}`}
      onClick={handleClick}
    >
      <img 
        src={property.imageUrl} 
        alt={property.title}
        className="property-card__image"
      />
      <h3 className="property-card__title">{property.title}</h3>
      <p className="property-card__price">${property.price}</p>
    </div>
  );
};
```

### Component Guidelines

1. **TypeScript First**: All components use TypeScript with proper interfaces
2. **Functional Components**: Use React functional components with hooks
3. **Props Interface**: Define clear TypeScript interfaces for all props
4. **JSDoc Comments**: Include JSDoc for component documentation
5. **CSS Classes**: Use Tailwind CSS with BEM-like custom classes when needed
6. **Accessibility**: Include ARIA attributes and semantic HTML

### Example Hook

```typescript
import { useState, useEffect } from 'react';
import { propertyService } from '../services/propertyService';

interface UsePropertiesResult {
  properties: Property[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

/**
 * Custom hook for managing property data
 * @param filters - Optional property filters
 * @returns Properties data, loading state, and error handling
 */
export const useProperties = (filters?: PropertyFilters): UsePropertiesResult => {
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProperties = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await propertyService.getProperties(filters);
      setProperties(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch properties');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProperties();
  }, [filters]);

  return { properties, loading, error, refetch: fetchProperties };
};
```

## 🔌 API Integration

### Service Layer Architecture

The frontend uses a **service layer pattern** with TypeScript for API communication:

```typescript
import { ApiResponse, Property, PropertyFilters } from '../types';

/**
 * Base API client with authentication and error handling
 */
class ApiClient {
  private baseURL: string;
  private token: string | null;

  constructor(baseURL = 'http://localhost:8000/api/v1') {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('authToken');
  }

  /**
   * Make authenticated API request
   * @param endpoint - API endpoint
   * @param options - Fetch options
   * @returns API response data
   */
  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` }),
        ...options.headers
      },
      ...options
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API Request failed:', error);
      throw error;
    }
  }
}

export { ApiClient };
```

### Service Examples

```typescript
/**
 * Property management service
 */
class PropertyService extends ApiClient {
  /**
   * Get all properties with optional filters
   * @param filters - Search and filter parameters
   * @returns Properties list with pagination
   */
  async getProperties(filters: PropertyFilters = {}): Promise<ApiResponse<Property[]>> {
    const params = new URLSearchParams(filters as Record<string, string>);
    return this.request<ApiResponse<Property[]>>(`/properties/?${params}`);
  }

  /**
   * Create new property
   * @param propertyData - Property information
   * @returns Created property data
   */
  async createProperty(propertyData: Partial<Property>): Promise<Property> {
    return this.request<Property>('/properties/', {
      method: 'POST',
      body: JSON.stringify(propertyData)
    });
  }

  /**
   * Get property by ID
   * @param id - Property ID
   * @returns Property details
   */
  async getProperty(id: string): Promise<Property> {
    return this.request<Property>(`/properties/${id}/`);
  }
}

export const propertyService = new PropertyService();
```

## 🎭 State Management

### React Context & TanStack Query

The frontend uses **React Context** for global state and **TanStack Query** for server state:

```typescript
import React, { createContext, useContext, useReducer } from 'react';

interface AppState {
  user: User | null;
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
}

interface AppAction {
  type: 'SET_USER' | 'SET_THEME' | 'TOGGLE_SIDEBAR';
  payload?: any;
}

const initialState: AppState = {
  user: null,
  theme: 'light',
  sidebarOpen: false
};

/**
 * App state reducer
 * @param state - Current state
 * @param action - Action to perform
 * @returns Updated state
 */
const appReducer = (state: AppState, action: AppAction): AppState => {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload };
    case 'SET_THEME':
      return { ...state, theme: action.payload };
    case 'TOGGLE_SIDEBAR':
      return { ...state, sidebarOpen: !state.sidebarOpen };
    default:
      return state;
  }
};

const AppContext = createContext<{
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
} | null>(null);

/**
 * App state provider component
 */
export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
};

/**
 * Hook to use app state
 * @returns App state and dispatch function
 */
export const useAppState = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppState must be used within AppProvider');
  }
  return context;
};
```

### TanStack Query Integration

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { propertyService } from '../services/propertyService';

/**
 * Hook for fetching properties with caching
 * @param filters - Property filters
 * @returns Query result with properties data
 */
export const usePropertiesQuery = (filters?: PropertyFilters) => {
  return useQuery({
    queryKey: ['properties', filters],
    queryFn: () => propertyService.getProperties(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  });
};

/**
 * Hook for creating properties with optimistic updates
 * @returns Mutation function and state
 */
export const useCreatePropertyMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: propertyService.createProperty,
    onSuccess: () => {
      // Invalidate and refetch properties
      queryClient.invalidateQueries({ queryKey: ['properties'] });
    },
  });
};
```

## 🧪 Testing Strategy

### Testing Philosophy

- **Unit Tests**: Test individual React components and hooks
- **Integration Tests**: Test component interactions and API integration
- **E2E Tests**: Test complete user workflows
- **Type Validation**: Use TypeScript for compile-time type checking

### Test Structure

```typescript
/**
 * Example React component test
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { PropertyCard } from '../src/components/PropertyCard';
import { Property } from '../src/types';

const mockProperty: Property = {
  id: '1',
  title: 'Test Property',
  price: 250000,
  imageUrl: '/test-image.jpg',
  location: 'Test City'
};

describe('PropertyCard Component', () => {
  test('should render property information correctly', () => {
    render(<PropertyCard property={mockProperty} />);
    
    expect(screen.getByText('Test Property')).toBeInTheDocument();
    expect(screen.getByText('$250000')).toBeInTheDocument();
    expect(screen.getByAltText('Test Property')).toBeInTheDocument();
  });

  test('should call onSelect when clicked', () => {
    const mockOnSelect = jest.fn();
    render(
      <PropertyCard 
        property={mockProperty} 
        onSelect={mockOnSelect} 
      />
    );
    
    fireEvent.click(screen.getByText('Test Property'));
    expect(mockOnSelect).toHaveBeenCalledWith(mockProperty);
  });

  test('should apply custom className', () => {
    const { container } = render(
      <PropertyCard 
        property={mockProperty} 
        className="custom-class" 
      />
    );
    
    expect(container.firstChild).toHaveClass('property-card', 'custom-class');
  });
});
```

### Hook Testing

```typescript
/**
 * Example custom hook test
 */
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { usePropertiesQuery } from '../src/hooks/usePropertiesQuery';
import { propertyService } from '../src/services/propertyService';

// Mock the service
jest.mock('../src/services/propertyService');
const mockedPropertyService = propertyService as jest.Mocked<typeof propertyService>;

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('usePropertiesQuery', () => {
  test('should fetch properties successfully', async () => {
    const mockProperties = [mockProperty];
    mockedPropertyService.getProperties.mockResolvedValue({
      data: mockProperties,
      total: 1
    });

    const { result } = renderHook(() => usePropertiesQuery(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.data).toEqual(mockProperties);
  });
});
```

## 🔧 Build Configuration

### Vite Configuration

The project uses **Vite** with **React** and **TypeScript** for fast development and optimized production builds:

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu'],
        },
      },
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
```

### TypeScript Configuration

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

## 🎯 Performance Optimization

### Best Practices

1. **Lazy Loading**: Load components and assets on demand
2. **Code Splitting**: Split code into smaller chunks
3. **Image Optimization**: Use WebP format and responsive images
4. **CSS Optimization**: Minimize and compress CSS
5. **Caching**: Implement proper browser caching strategies

### Bundle Analysis

```bash
# Analyze bundle size
npm run build
npx vite-bundle-analyzer dist
```

## 🔒 Security Considerations

### Frontend Security

1. **XSS Prevention**: React automatically escapes JSX content, but be careful with `dangerouslySetInnerHTML`
2. **CSRF Protection**: Include CSRF tokens in API requests
3. **Content Security Policy**: Implement strict CSP headers
4. **Secure Storage**: Use secure methods for sensitive data storage
5. **Type Safety**: TypeScript helps prevent runtime errors and security vulnerabilities

### Example: Secure Input Handling

```typescript
import { useState, useCallback } from 'react';
import DOMPurify from 'dompurify';

interface SecureInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

/**
 * Secure input component with built-in sanitization
 */
export const SecureInput: React.FC<SecureInputProps> = ({
  value,
  onChange,
  placeholder
}) => {
  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    // Sanitize input to prevent XSS
    const sanitizedValue = DOMPurify.sanitize(e.target.value);
    onChange(sanitizedValue);
  }, [onChange]);

  return (
    <input
      type="text"
      value={value}
      onChange={handleChange}
      placeholder={placeholder}
      className="secure-input"
    />
  );
};

/**
 * Safe HTML renderer for trusted content
 */
interface SafeHtmlProps {
  content: string;
  className?: string;
}

export const SafeHtml: React.FC<SafeHtmlProps> = ({ content, className }) => {
  const sanitizedContent = DOMPurify.sanitize(content);
  
  return (
    <div
      className={className}
      dangerouslySetInnerHTML={{ __html: sanitizedContent }}
    />
  );
};
```

## 📱 Responsive Design

### Tailwind CSS Responsive Utilities

The project uses **Tailwind CSS** for responsive design with a mobile-first approach:

```typescript
// Example responsive component
interface PropertyGridProps {
  properties: Property[];
}

export const PropertyGrid: React.FC<PropertyGridProps> = ({ properties }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {properties.map((property) => (
        <PropertyCard key={property.id} property={property} />
      ))}
    </div>
  );
};

// Custom responsive hook
export const useResponsive = () => {
  const [isMobile, setIsMobile] = useState(false);
  const [isTablet, setIsTablet] = useState(false);

  useEffect(() => {
    const checkDevice = () => {
      setIsMobile(window.innerWidth < 768);
      setIsTablet(window.innerWidth >= 768 && window.innerWidth < 1024);
    };

    checkDevice();
    window.addEventListener('resize', checkDevice);
    return () => window.removeEventListener('resize', checkDevice);
  }, []);

  return { isMobile, isTablet, isDesktop: !isMobile && !isTablet };
};
```

## 🎨 Icon System

### React Icon Components

All icons are **SVG format** using **Lucide React** for scalability and performance:

```typescript
import { Home, User, Search, Heart, MapPin } from 'lucide-react';

interface IconProps {
  size?: number;
  className?: string;
}

/**
 * Reusable icon component with consistent styling
 */
export const Icon: React.FC<IconProps & { name: string }> = ({ 
  name, 
  size = 24, 
  className = '' 
}) => {
  const iconMap = {
    home: Home,
    user: User,
    search: Search,
    heart: Heart,
    location: MapPin,
  };

  const IconComponent = iconMap[name as keyof typeof iconMap];
  
  if (!IconComponent) {
    console.warn(`Icon "${name}" not found`);
    return null;
  }

  return (
    <IconComponent 
      size={size} 
      className={`inline-block ${className}`}
    />
  );
};

/**
 * Custom SVG icon component for brand-specific icons
 */
interface CustomIconProps extends IconProps {
  children: React.ReactNode;
  viewBox?: string;
}

export const CustomIcon: React.FC<CustomIconProps> = ({
  children,
  size = 24,
  className = '',
  viewBox = '0 0 24 24'
}) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox={viewBox}
      fill="currentColor"
      className={`inline-block ${className}`}
    >
      {children}
    </svg>
  );
};
```

## 🚀 Deployment

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Build Output

```
dist/
├── index.html          # Main HTML file
├── assets/            # Optimized assets
│   ├── main.[hash].js # Bundled JavaScript
│   ├── main.[hash].css # Bundled CSS
│   └── icons/         # Optimized SVG icons
└── manifest.json      # Web app manifest
```

## 📚 Additional Resources

### Documentation Links

- [MDN Web Docs](https://developer.mozilla.org/) - Web standards reference
- [Vite Documentation](https://vitejs.dev/) - Build tool documentation
- [BEM Methodology](http://getbem.com/) - CSS naming convention
- [Web Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/) - WCAG 2.1 reference

### Development Tools

- **VS Code Extensions**: ES6 String HTML, CSS Peek, Auto Rename Tag
- **Browser DevTools**: Chrome/Firefox developer tools
- **Testing**: Jest for unit tests, Playwright for E2E tests
- **Linting**: ESLint for JavaScript, Stylelint for CSS

## 🤝 Contributing

When contributing to the frontend:

1. **Follow Architecture**: Use vanilla JavaScript patterns established in this documentation
2. **CSS Standards**: Follow BEM methodology and use CSS variables
3. **Documentation**: Include JSDoc comments for all functions
4. **Testing**: Write tests for new components and features
5. **Performance**: Consider bundle size and runtime performance
6. **Accessibility**: Ensure components are accessible and semantic

## 📞 Support

For frontend-specific questions:

- **Email**: support@ifinsta.com
- **Company**: Eleso Solutions
- **Documentation**: This README and inline code comments

---

**Built with vanilla JavaScript and modern web standards by the Eleso Solutions team**