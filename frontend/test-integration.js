#!/usr/bin/env node

/**
 * Integration Test Runner
 * 
 * Simple Node.js script to run frontend-backend integration tests
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Configuration
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';

// Test results
const results = [];

// Utility functions
function log(message, type = 'info') {
  const timestamp = new Date().toISOString();
  const prefix = type === 'error' ? '❌' : type === 'success' ? '✅' : '📝';
  console.log(`${prefix} [${timestamp}] ${message}`);
}

async function checkBackendHealth() {
  log('Checking backend health...');
  
  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/health/`);
    const data = await response.json();
    
    if (response.ok) {
      log(`Backend is healthy: ${data.status}`, 'success');
      return true;
    } else {
      log(`Backend health check failed: ${response.status}`, 'error');
      return false;
    }
  } catch (error) {
    log(`Backend health check error: ${error.message}`, 'error');
    return false;
  }
}

async function checkFrontendBuild() {
  log('Checking frontend build...');
  
  const buildPath = path.join(__dirname, 'dist');
  if (fs.existsSync(buildPath)) {
    log('Frontend build exists', 'success');
    return true;
  } else {
    log('Frontend build not found, building...');
    
    try {
      execSync('npm run build', { stdio: 'inherit' });
      log('Frontend build completed', 'success');
      return true;
    } catch (error) {
      log(`Frontend build failed: ${error.message}`, 'error');
      return false;
    }
  }
}

async function checkAPIEndpoints() {
  log('Checking API endpoints...');
  
  const endpoints = [
    { method: 'GET', path: '/api/v1/auth/user/', expected: 401 },
    { method: 'POST', path: '/api/v1/auth/login/', expected: 400 },
    { method: 'GET', path: '/api/v1/blog/posts/', expected: 200 },
    { method: 'GET', path: '/api/v1/cities/', expected: 200 },
  ];

  let passed = 0;
  
  for (const endpoint of endpoints) {
    try {
      const response = await fetch(`${BACKEND_URL}${endpoint.path}`, {
        method: endpoint.method,
      });
      
      if (response.status === endpoint.expected) {
        log(`${endpoint.method} ${endpoint.path} ✓`, 'success');
        passed++;
      } else {
        log(`${endpoint.method} ${endpoint.path} ✗ (got ${response.status}, expected ${endpoint.expected})`, 'error');
      }
    } catch (error) {
      log(`${endpoint.method} ${endpoint.path} ✗ (${error.message})`, 'error');
    }
  }
  
  log(`${passed}/${endpoints.length} API endpoints responding correctly`);
  return passed === endpoints.length;
}

async function checkTypeDefinitions() {
  log('Checking TypeScript type definitions...');
  
  try {
    execSync('npx tsc --noEmit', { stdio: 'pipe' });
    log('TypeScript compilation successful', 'success');
    return true;
  } catch (error) {
    log('TypeScript compilation failed', 'error');
    return false;
  }
}

async function checkServiceImports() {
  log('Checking service imports...');
  
  const services = [
    '../src/services/apiClient.js',
    '../src/services/authService.js',
    '../src/services/blogService.js',
    '../src/services/cityService.js',
  ];

  let passed = 0;
  
  for (const service of services) {
    try {
      const servicePath = path.join(__dirname, service);
      if (fs.existsSync(servicePath)) {
        log(`${service} ✓`, 'success');
        passed++;
      } else {
        log(`${service} ✗ (file not found)`, 'error');
      }
    } catch (error) {
      log(`${service} ✗ (${error.message})`, 'error');
    }
  }
  
  return passed === services.length;
}

async function runIntegrationTests() {
  log('Starting integration tests...');
  
  const tests = [
    checkBackendHealth,
    checkFrontendBuild,
    checkAPIEndpoints,
    checkTypeDefinitions,
    checkServiceImports,
  ];

  const results = [];
  
  for (const test of tests) {
    try {
      const result = await test();
      results.push(result);
    } catch (error) {
      log(`Test failed: ${error.message}`, 'error');
      results.push(false);
    }
  }

  const passed = results.filter(r => r).length;
  const total = results.length;
  
  log(`\n📊 Test Summary: ${passed}/${total} tests passed`);
  
  if (passed === total) {
    log('🎉 All integration tests passed!', 'success');
    process.exit(0);
  } else {
    log('⚠️ Some tests failed. Check the logs above for details.', 'error');
    process.exit(1);
  }
}

// CLI interface
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
Frontend-Backend Integration Test Runner

Usage: node test-integration.js [options]

Options:
  --backend-url <url>    Backend API URL (default: http://localhost:8000)
  --frontend-url <url>   Frontend URL (default: http://localhost:3000)
  --help, -h            Show this help message

Environment Variables:
  BACKEND_URL           Backend API URL
  FRONTEND_URL          Frontend URL
    `);
    process.exit(0);
  }

  // Parse arguments
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--backend-url' && i + 1 < args.length) {
      process.env.BACKEND_URL = args[i + 1];
      i++;
    } else if (args[i] === '--frontend-url' && i + 1 < args.length) {
      process.env.FRONTEND_URL = args[i + 1];
      i++;
    }
  }

  // Run tests
  runIntegrationTests().catch(error => {
    log(`Test runner error: ${error.message}`, 'error');
    process.exit(1);
  });
}

module.exports = {
  runIntegrationTests,
  checkBackendHealth,
  checkAPIEndpoints,
  checkTypeDefinitions,
};