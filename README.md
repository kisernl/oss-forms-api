# Mayfly Forms API

A serverless email API service for handling form submissions from client websites. Currently supports AWS Lambda + SES, with plans for multi-provider support.

## 🎯 Overview

Mayfly Forms provides a simple, cost-effective way to handle contact forms and other form submissions without managing servers. Perfect for static sites, portfolios, and any application needing reliable form processing.

## ✨ Features

### Current Features
- 🚀 **Serverless**: Deploy on AWS Lambda for automatic scaling
- 📧 **Email Delivery**: Reliable sending via AWS SES
- 🔐 **API Key Authentication**: Secure access control for multiple clients
- 🛡️ **Rate Limiting**: Configurable limits to prevent abuse
- ✅ **Input Validation**: Comprehensive validation and sanitization
- 🌐 **CORS Support**: Ready for browser-based form submissions
- 💰 **Cost Effective**: Pay only for actual usage
- 🔧 **Easy Integration**: Works with any frontend framework

### 🗺️ Roadmap
- 📧 **Multi-Provider Email**: SendGrid, Mailgun, Postmark, Resend, SMTP support
- ☁️ **Multi-Cloud Deploy**: Vercel, Netlify Functions, Google Cloud Functions
- 🔧 **Enhanced Auth**: JWT tokens, webhook signatures
- 📊 **Analytics**: Form submission metrics and insights
- 🛡️ **Advanced Security**: Spam protection, enhanced validation
- 🧪 **Testing Suite**: Comprehensive unit and integration tests

## 🚀 Quick Start

### For Users (Deploy Your Own Instance)

#### Prerequisites
- Python 3.9+
- Node.js 14+ (for Serverless Framework)
- AWS CLI configured with appropriate permissions
- AWS account with SES access

#### Installation
```bash
# Fork this repository on GitHub first, then:
git clone https://github.com/YOUR-USERNAME/mayfly-forms-oss.git
cd mayfly-forms-oss

# Install dependencies
pip install -r requirements.txt
npm install

# Install Serverless Framework globally (if not already installed)
npm install -g serverless
```

#### AWS SES Setup
Before deploying, configure AWS SES:

```bash
# 1. Verify your sender email address or domain
aws ses verify-email-identity --email-address noreply@yourdomain.com

# 2. Check verification status
aws ses get-identity-verification-attributes --identities noreply@yourdomain.com

# 3. If in SES sandbox, verify recipient emails for testing
aws ses verify-email-identity --email-address test@yourdomain.com
```

#### Configuration
Set environment variables (create `.env` file or use your deployment method):

```bash
# Required
VALID_API_KEYS=your-secret-key-1,your-secret-key-2

# Recommended
SES_DEFAULT_SENDER=noreply@yourdomain.com  # Must be verified in SES
AWS_REGION=us-east-1

# For local development only
FLASK_ENV=development
```

#### Local Development
```bash
# Test locally (optional)
python app/main.py
# API available at http://localhost:5000
```

#### Deploy to AWS
```bash
# Deploy to development
serverless deploy

# Deploy to production  
serverless deploy --stage prod
```

### For Contributors (Development Setup)

If you want to contribute to the project:

```bash
# Fork the repo, then clone your fork
git clone https://github.com/YOUR-USERNAME/mayfly-forms-oss.git
cd mayfly-forms-oss

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8  # Additional dev tools

# Install Node.js dependencies
npm install

# Create a feature branch
git checkout -b feature/your-feature-name

# Make your changes and test
python -m pytest  # Run tests (if available)

# Follow contribution guidelines in CONTRIBUTING.md
```

## 🍴 Forking for Your Own Use

This project is designed to be easily forkable for your own needs:

### Why Fork?
- **Customize validation rules** for your specific forms
- **Add custom email templates** for your brand
- **Integrate with your specific services** (CRM, Slack, etc.)
- **Modify rate limiting** for your traffic patterns
- **Add custom authentication** (OAuth, custom headers, etc.)

### Customization Points
- **Email templates**: Modify `_generate_email_body()` in `app/handlers/email_handler.py:120`
- **Validation rules**: Update `app/utils/validation.py`
- **Rate limits**: Adjust `app/utils/rate_limiter.py`
- **Authentication**: Extend `app/auth/api_key_auth.py`
- **Response format**: Customize responses in `app/main.py`

### Best Practices for Forks
1. **Keep upstream connection**: Add this repo as an upstream remote
2. **Document your changes**: Update README with your modifications
3. **Environment-specific config**: Use environment variables for customization
4. **Consider contributing back**: If your changes could benefit others, submit a PR!

## API Usage

### Authentication

All requests require an API key in the `X-API-Key` header:

```bash
curl -X POST https://your-api-url/submit-form \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d @form-data.json
```

### Submit Form Endpoint

**POST** `/submit-form`

#### Request Body

```json
{
  "to_email": "recipient@example.com",
  "from_email": "sender@example.com",
  "subject": "New Contact Form Submission",
  "source_url": "https://yoursite.com/contact",
  "fields": {
    "name": "John Doe",
    "email": "john@example.com",
    "message": "Hello, I'd like to get in touch!",
    "phone": "+1-555-123-4567"
  }
}
```

#### Required Fields
- `to_email`: Recipient email address
- `fields`: Object containing form data (at least one field required)

#### Optional Fields
- `from_email`: Sender email (defaults to noreply@example.com)
- `subject`: Email subject (defaults to "New Form Submission")
- `source_url`: URL where the form was submitted from

#### Response

**Success (200)**
```json
{
  "message": "Form submitted successfully",
  "email_id": "resend-email-id"
}
```

**Error (400/401/429/500)**
```json
{
  "error": "Error description"
}
```

### Health Check

**GET** `/health`

```json
{
  "status": "healthy",
  "service": "mayfly-forms"
}
```

## Rate Limits

Default rate limits per IP address:
- 10 requests per minute
- 100 requests per hour  
- 1,000 requests per day

Rate limit exceeded returns HTTP 429.

## Client Integration Examples

### HTML Form with JavaScript

```html
<form id="contact-form">
  <input type="text" name="name" required>
  <input type="email" name="email" required>
  <textarea name="message" required></textarea>
  <button type="submit">Send</button>
</form>

<script>
document.getElementById('contact-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const formData = new FormData(e.target);
  const data = {
    to_email: 'contact@yourcompany.com',
    subject: 'New Contact Form Submission',
    source_url: window.location.href,
    fields: Object.fromEntries(formData)
  };
  
  try {
    const response = await fetch('https://your-api-url/submit-form', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': 'your-api-key'
      },
      body: JSON.stringify(data)
    });
    
    if (response.ok) {
      alert('Message sent successfully!');
      e.target.reset();
    } else {
      alert('Error sending message. Please try again.');
    }
  } catch (error) {
    alert('Network error. Please try again.');
  }
});
</script>
```

### React Component

```jsx
import { useState } from 'react';

const ContactForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch('https://your-api-url/submit-form', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': process.env.REACT_APP_FORMS_API_KEY
        },
        body: JSON.stringify({
          to_email: 'contact@yourcompany.com',
          subject: 'New Contact Form Submission',
          source_url: window.location.href,
          fields: formData
        })
      });
      
      if (response.ok) {
        alert('Message sent successfully!');
        setFormData({ name: '', email: '', message: '' });
      } else {
        alert('Error sending message.');
      }
    } catch (error) {
      alert('Network error.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form inputs */}
    </form>
  );
};
```

## Configuration

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `VALID_API_KEYS` | Yes | Comma-separated list of valid API keys for clients | `client-key-1,client-key-2` |
| `SES_DEFAULT_SENDER` | Recommended | Default sender email (must be verified in SES) | `noreply@yourdomain.com` |
| `AWS_REGION` | No | AWS region for SES (defaults to us-east-1) | `us-west-2` |
| `FLASK_ENV` | No | Flask environment (for local development only) | `development` |

**Note**: The table in the original README mentioned `RESEND_API_KEY` but the code actually uses AWS SES. This will change when multi-provider support is added.

### Rate Limiting Configuration

Edit `app/utils/rate_limiter.py` to customize rate limits:

```python
self.limits = {
    'per_minute': 10,    # Requests per minute
    'per_hour': 100,     # Requests per hour  
    'per_day': 1000      # Requests per day
}
```

## Security Features

### Built-in Security
- **API Key Authentication**: Secure access control with configurable keys
- **Input Validation**: Comprehensive validation and sanitization of all form data
- **XSS Protection**: Automatic filtering of potentially malicious content
- **Rate Limiting**: Built-in protection against abuse (10 req/min, 100 req/hour, 1000 req/day per IP)
- **CORS Configuration**: Configurable cross-origin resource sharing
- **Secure Defaults**: Debug mode disabled by default, no hardcoded secrets

### Important Security Considerations for Your Deployment

#### 🔑 API Key Security
- **Generate Strong Keys**: Use keys with 16+ characters, include random alphanumeric characters
- **Keep Keys Secret**: Never commit API keys to version control or share publicly
- **Use Environment Variables**: Always configure `VALID_API_KEYS` via environment variables
- **Consider Rotation**: Implement key rotation for production deployments

#### 🌐 CORS Configuration
- **Restrict Origins**: For production, update CORS settings to only allow your specific domains
- **Review Regularly**: Audit which domains have access to your API

#### 📊 Monitoring & Logging
- **Monitor Usage**: Watch CloudWatch logs for unusual patterns or abuse
- **Set Up Alerts**: Configure AWS CloudWatch alarms for high request volumes
- **Review Access**: Regularly audit API key usage patterns

#### 🛡️ Rate Limiting Considerations
- **Distributed Limits**: Current rate limiting is per-Lambda instance; consider DynamoDB for distributed limiting in high-traffic scenarios
- **IP Spoofing**: Be aware that `X-Forwarded-For` headers can be manipulated
- **Adjust Limits**: Modify rate limits in `app/utils/rate_limiter.py` based on your needs

#### 🔒 AWS Security Best Practices
- **IAM Permissions**: Use minimal required permissions for Lambda execution role
- **SES Sandbox**: Remove SES sandbox limitations only after verifying your sending domain
- **VPC Configuration**: Consider deploying Lambda in VPC for additional network isolation
- **Encryption**: Enable encryption at rest for any stored data

⚠️ **Security Notice**: This is a self-hosted solution. You are responsible for the security of your deployment, API key management, and compliance with applicable regulations.

## Cost Estimation

**AWS Lambda:**
- Free tier: 1M requests/month
- After free tier: $0.20 per 1M requests

**AWS SES:**
- Free tier: 62,000 emails/month (when sent from EC2)
- Outside free tier: $0.10 per 1,000 emails
- Additional charges for attachments: $0.12 per GB

**Example monthly costs:**
- Under 62K form submissions: **Free** (within SES free tier)
- 100K form submissions: **~$4** (Lambda + SES)
- 500K form submissions: **~$45** (Lambda + SES)

**Significantly more cost-effective than third-party email services!**

## 🏗️ Architecture & Development

### Current Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Apps   │───▶│  Mayfly Forms   │───▶│    AWS SES      │
│ (Static sites,  │    │   (Lambda)      │    │  (Email Send)   │
│  React, etc.)   │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Project Structure
```
mayfly-forms-oss/
├── app/                          # Core Flask application
│   ├── handlers/
│   │   └── email_handler.py      # 🎯 AWS SES integration (make generic!)
│   ├── auth/
│   │   └── api_key_auth.py       # API key authentication
│   ├── utils/
│   │   ├── validation.py         # Input validation
│   │   └── rate_limiter.py       # Rate limiting logic
│   └── main.py                   # Flask application entry point
├── docs/                         # Documentation
│   ├── DEPLOYMENT_GUIDE.md       # Deployment instructions
│   ├── DELIVERABILITY_GUIDE.md   # Email deliverability setup
│   └── SES_SETUP.md              # AWS SES specific setup
├── lambda_function.py            # AWS Lambda entry point
├── serverless.yml               # Serverless deployment config
├── requirements.txt             # Python dependencies
├── CONTRIBUTING.md              # Contribution guidelines
├── example-client.html          # Frontend integration example
└── README.md                    # This file
```

### Development Workflow

#### Running Tests
```bash
# Install test dependencies (when available)
pip install pytest

# Run tests
pytest

# Run with coverage
pytest --cov=app/
```

#### Code Quality
```bash
# Format code
black app/

# Lint code  
flake8 app/

# Type checking (if types added)
mypy app/
```

#### API Key Management
```python
# Generate new API keys
from app.auth.api_key_auth import generate_api_key
new_key = generate_api_key('client-name')
print(new_key)  # Returns: client-name-<random-string>
```

## 🤝 Contributing to Multi-Provider Support

**We need your help!** Currently, Mayfly Forms only supports AWS SES. We want to make it work with multiple email providers.

### 🎯 Priority Providers to Add
- **SendGrid** - Popular email service with good API
- **Mailgun** - Developer-friendly email service  
- **Postmark** - High deliverability focus
- **Resend** - Modern email API
- **SMTP** - Generic SMTP support for any provider

### 🛠️ How to Add a New Provider

#### 1. Provider Interface Design
We need to create a generic provider interface. The current `EmailHandler` class in `app/handlers/email_handler.py` is AWS SES specific.

**Proposed structure:**
```python
# app/providers/base.py
class EmailProvider:
    def send_email(self, form_data) -> dict:
        """Send email via provider. Returns success/error status."""
        raise NotImplementedError

# app/providers/ses_provider.py  
class SESProvider(EmailProvider):
    # Move current SES logic here

# app/providers/sendgrid_provider.py
class SendGridProvider(EmailProvider):
    # Implement SendGrid integration
```

#### 2. Configuration System
Add provider selection via environment variables:
```bash
EMAIL_PROVIDER=ses  # or sendgrid, mailgun, etc.
SENDGRID_API_KEY=...  # Provider-specific config
MAILGUN_API_KEY=...
```

#### 3. Provider Factory
Create a factory to instantiate the correct provider:
```python
# app/providers/factory.py
def get_email_provider():
    provider = os.environ.get('EMAIL_PROVIDER', 'ses')
    if provider == 'ses':
        return SESProvider()
    elif provider == 'sendgrid':
        return SendGridProvider()
    # etc.
```

### 📋 Contribution Checklist for New Providers

When adding a new provider, please ensure:

- [ ] **Provider class** implements `EmailProvider` interface
- [ ] **Environment variables** documented for configuration
- [ ] **Error handling** follows existing patterns
- [ ] **Tests** added for the new provider
- [ ] **Documentation** updated (README + provider-specific guide)
- [ ] **Example configuration** provided
- [ ] **Rate limiting** considerations addressed
- [ ] **Deliverability features** implemented (reply-to, sender name, etc.)

### 🚀 Getting Started with Provider Contributions

1. **Check existing issues** for provider requests
2. **Create an issue** to discuss the provider you want to add
3. **Fork the repository** and create a feature branch
4. **Study the current SES implementation** in `app/handlers/email_handler.py`
5. **Design the provider interface** (we can help with this!)
6. **Implement your provider** following the checklist above
7. **Submit a PR** with comprehensive testing

### 💡 Other Contribution Ideas

Beyond email providers, we welcome contributions for:

- **Deployment options**: Vercel, Netlify Functions, Google Cloud Functions
- **Authentication methods**: JWT tokens, webhook signatures
- **Storage backends**: For rate limiting, analytics
- **Monitoring**: Health checks, metrics, logging improvements
- **Security**: Additional validation, spam protection
- **Testing**: Unit tests, integration tests, load testing

## 📞 Support & Community

- **🐛 Bug Reports**: [Create an issue](https://github.com/kisernl/mayfly-forms-oss/issues)
- **💡 Feature Requests**: [Create an issue](https://github.com/kisernl/mayfly-forms-oss/issues) with `enhancement` label
- **❓ Questions**: [Discussions](https://github.com/kisernl/mayfly-forms-oss/discussions) or create issue with `question` label
- **🤝 Contributions**: See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**⭐ Star this repo if it's useful to you!** It helps others discover the project.