/**
 * Common error classes for API interactions
 */

export class APIValidationError extends Error {
  public validationErrors: Record<string, string[]>;
  public statusCode: number;

  constructor(message: string, validationErrors: Record<string, string[]>, statusCode: number = 400) {
    super(message);
    this.name = 'APIValidationError';
    this.validationErrors = validationErrors;
    this.statusCode = statusCode;
  }
}

export class APIError extends Error {
  status: number;
  code?: string;
  data?: unknown;

  constructor(message: string, status: number, code?: string, data?: unknown) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.code = code;
    this.data = data;
  }
}

export class NetworkError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'NetworkError';
  }
}

export class AuthenticationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AuthenticationError';
  }
}

export class ValidationError extends Error {
  public field?: string;
  public errors?: Record<string, string[]>;
  public validationErrors?: Record<string, string[]>;

  constructor(message: string, validationErrors?: Record<string, string[]> | string, errors?: Record<string, string[]>) {
    super(message);
    this.name = 'ValidationError';
    
    // Handle both old and new constructor patterns
    if (typeof validationErrors === 'string') {
      this.field = validationErrors;
      this.errors = errors;
    } else {
      this.validationErrors = validationErrors;
      this.errors = validationErrors;
    }
  }
}