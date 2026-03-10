# Security Policy

## Supported Versions

We currently support the following versions of Orchestratorr with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

If you believe you've found a security vulnerability in Orchestratorr, please follow these steps:

1. **Create a private security advisory** on GitHub:
   - Go to the repository's "Security" tab
   - Click "Report a vulnerability"
   - Fill out the security advisory form

2. **Include the following information** in your report:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)
   - Any proof-of-concept or exploit code

3. **We will respond within 48 hours** to acknowledge receipt of your report

4. **We will work with you** to understand and validate the issue

5. **Once verified**, we will work on a fix and coordinate disclosure

## Security Best Practices for Users

### Configuration
- **Use strong API keys** for your *arr services
- **Run Orchestratorr behind a reverse proxy** with HTTPS in production
- **Restrict network access** to the Orchestratorr backend when possible
- **Regularly update** both Orchestratorr and your *arr services

### Deployment
- **Do not run as root** - use a dedicated user account
- **Use environment variables** for sensitive configuration
- **Keep your operating system** and dependencies updated
- **Monitor logs** for suspicious activity

## Security Considerations

Orchestratorr acts as a proxy to your *arr services. Keep in mind:

1. **API Keys**: Orchestratorr stores API keys in memory but does not persist them
2. **Network Exposure**: The backend exposes endpoints that proxy to your *arr services
3. **CORS**: Configure CORS appropriately for your deployment
4. **Authentication**: Orchestratorr does not currently implement user authentication

## Questions?

For security-related questions, please use the private security advisory feature on GitHub.