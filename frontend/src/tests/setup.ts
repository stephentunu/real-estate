import '@testing-library/jest-dom'
import { vi, beforeEach, afterEach } from 'vitest'

// Mock PromiseRejectionEvent for unhandled promise rejection tests
global.PromiseRejectionEvent = class PromiseRejectionEvent extends Event {
  promise: Promise<unknown>
  reason: unknown

  constructor(type: string, eventInitDict?: { promise: Promise<unknown>; reason: unknown }) {
    super(type)
    this.promise = eventInitDict?.promise || Promise.resolve()
    this.reason = eventInitDict?.reason
  }
} as unknown as typeof PromiseRejectionEvent

// Mock ErrorEvent for uncaught error tests
global.ErrorEvent = class ErrorEvent extends Event {
  error: Error | null
  message: string
  filename: string
  lineno: number
  colno: number

  constructor(type: string, eventInitDict?: { 
    error?: Error | null
    message?: string
    filename?: string
    lineno?: number
    colno?: number
  }) {
    super(type)
    this.error = eventInitDict?.error || null
    this.message = eventInitDict?.message || ''
    this.filename = eventInitDict?.filename || ''
    this.lineno = eventInitDict?.lineno || 0
    this.colno = eventInitDict?.colno || 0
  }
} as unknown as typeof ErrorEvent

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock scrollTo
Object.defineProperty(window, 'scrollTo', {
  writable: true,
  value: vi.fn(),
})

// Mock HTMLElement.scrollIntoView
Object.defineProperty(HTMLElement.prototype, 'scrollIntoView', {
  writable: true,
  value: vi.fn(),
})

// Mock navigator.clipboard
Object.defineProperty(navigator, 'clipboard', {
  writable: true,
  value: {
    writeText: vi.fn().mockResolvedValue(undefined),
    readText: vi.fn().mockResolvedValue(''),
  },
})

// Mock fetch globally
global.fetch = vi.fn()

// Setup console mocks to reduce noise in tests
const originalConsoleError = console.error
const originalConsoleWarn = console.warn

// Global error handler to prevent unhandled promise rejections from failing tests
const originalUnhandledRejection = process.listeners('unhandledRejection')
process.removeAllListeners('unhandledRejection')

beforeEach(() => {
  console.error = vi.fn()
  console.warn = vi.fn()
})

afterEach(() => {
  console.error = originalConsoleError
  console.warn = originalConsoleWarn
  vi.clearAllMocks()
})