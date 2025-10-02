# Security Policy

## Supported Versions

We actively support the following versions of Jaston Real Estate platform with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

The Jaston Real Estate team takes security vulnerabilities seriously. We appreciate your efforts to responsibly disclose your findings, and will make every effort to acknowledge your contributions.

### How to Report a Security Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **support@ifinsta.com**

Please include the following information in your report:

- Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

### What to Expect

After you submit a report, we will:

1. **Acknowledge receipt** of your vulnerability report within 48 hours
2. **Provide an estimated timeline** for addressing the vulnerability within 5 business days
3. **Notify you** when the vulnerability is fixed
4. **Credit you** in our security advisories (if desired)

### Security Response Timeline

- **Critical vulnerabilities**: Patched within 24-48 hours
- **High severity vulnerabilities**: Patched within 1 week
- **Medium/Low severity vulnerabilities**: Patched within 30 days

## Security Best Practices

### For Contributors

When contributing to this project, please:

- Never commit sensitive information (API keys, passwords, tokens) to the repository
- Use environment variables for configuration secrets
- Follow secure coding practices
- Run security linters and tests before submitting PRs
- Keep dependencies up to date

### For Deployments

When deploying Jaston Real Estate:

- Use HTTPS in production environments
- Keep your Django SECRET_KEY secure and unique
- Use strong database passwords
- Enable Django's security middleware
- Regularly update dependencies
- Monitor logs for suspicious activity
- Use proper firewall configurations
- Enable database encryption at rest

## Security Features

This platform includes several built-in security features:

- **Authentication**: JWT-based authentication with refresh token rotation
- **Authorization**: Role-based access control with tenant isolation
- **Data Protection**: Soft-delete patterns to prevent accidental data loss
- **Input Validation**: Comprehensive input sanitization and validation
- **CSRF Protection**: Django's built-in CSRF protection
- **SQL Injection Prevention**: Django ORM prevents SQL injection attacks
- **XSS Protection**: Template auto-escaping and CSP headers

## Security Considerations for Property Management

Given the sensitive nature of property management data, we implement:

- **Multi-tenant isolation**: Strict data visibility controls
- **Document security**: Secure file upload and storage
- **Payment data protection**: PCI DSS compliance considerations
- **Personal data protection**: GDPR/privacy law compliance features
- **Audit logging**: Comprehensive activity logging for compliance

## Vulnerability Disclosure Policy

We follow responsible disclosure practices:

1. We will work with security researchers to verify and address reported vulnerabilities
2. We will provide credit to researchers who report vulnerabilities responsibly
3. We will not pursue legal action against researchers who follow our guidelines
4. We will publish security advisories for significant vulnerabilities after they are fixed

## Contact

For security-related questions or concerns, please contact:

- **Email**: support@ifinsta.com
- **Company**: Eleso Solutions
- **Response Time**: Within 48 hours for security issues

## Security Updates

Security updates and advisories will be published:

- In the project's GitHub Security Advisories
- In the CHANGELOG.md file
- Via email to registered users (for critical vulnerabilities)

Thank you for helping keep Jaston Real Estate and our users safe!