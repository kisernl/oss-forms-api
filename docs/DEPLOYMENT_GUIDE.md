# Mayfly Forms API - Developer Deployment Guide

This guide will walk you through deploying your own instance of the Mayfly Forms API using AWS Lambda and SES.

## 📋 **Prerequisites**

### Required Tools
- **Node.js** 16+ and npm
- **Python** 3.9+
- **AWS CLI** configured with appropriate permissions
- **Git** for cloning the repository

### Required AWS Permissions
Your AWS user/role needs these permissions:
- `AWSLambdaFullAccess`
- `AmazonAPIGatewayAdministrator`
- `CloudFormationFullAccess`
- `AmazonSESFullAccess`
- `IAMFullAccess` (for creating Lambda execution roles)
- `AmazonS3FullAccess` (for Serverless Framework deployments)

## 🚀 **Step 1: Clone and Setup**

```bash
# Clone the repository
git clone https://github.com/your-repo/mayfly-forms.git
cd mayfly-forms

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies for Serverless Framework
npm install -g serverless@3
npm install serverless-python-requirements
```

## 🔧 **Step 2: AWS CLI Configuration**

```bash
# Configure AWS CLI with your credentials
aws configure

# Verify configuration
aws sts get-caller-identity
```

**Required inputs:**
- AWS Access Key ID
- AWS Secret Access Key
- Default region (recommend `us-east-1` or `us-east-2`)
- Output format: `json`

## 📧 **Step 3: AWS SES Setup**

### Verify Sender Email/Domain

**Option A: Verify Individual Email**
```bash
# Replace with your sender email
aws ses verify-email-identity --email-address noreply@example.com

# Check verification status
aws ses get-identity-verification-attributes --identities noreply@example.com
```

**Option B: Verify Entire Domain (Recommended)**
```bash
# Verify domain
aws ses verify-domain-identity --domain example.com

# Get DNS verification token
aws ses get-identity-verification-attributes --identities example.com
```

### Add DNS Records for Domain Verification

Add this TXT record to your domain's DNS:
```
Type: TXT
Name: _amazonses.example.com
Value: [verification-token-from-aws]
TTL: 300
```

### Request Production Access

1. Go to [AWS SES Console](https://console.aws.amazon.com/ses/)
2. Click "Request production access"
3. Fill out the form:
   - **Mail Type:** Transactional
   - **Website URL:** Your business website
   - **Use Case:** Contact form submissions for client websites
   - **Expected Volume:** Your estimated monthly email volume

**Note:** Production access usually takes 24-48 hours to approve.

## 🔐 **Step 4: Generate API Keys**

```bash
# Generate secure API keys (run this in Python)
python3 -c "
from app.auth.api_key_auth import generate_api_key
print('Client Key 1:', generate_api_key('client1'))
print('Client Key 2:', generate_api_key('client2'))
print('Dev Key:', generate_api_key('dev'))
"
```

Save these keys securely - you'll need them for client integrations.

## 🌍 **Step 5: Environment Configuration**

```bash
# Set required environment variables
export VALID_API_KEYS=your-generated-key-1,your-generated-key-2,your-dev-key
export SES_DEFAULT_SENDER=noreply@example.com

# Optional: Set specific region if different from AWS CLI default
export AWS_REGION=us-east-1
```

**For persistent configuration, add to your `.bashrc` or `.zshrc`:**
```bash
echo 'export VALID_API_KEYS=your-generated-keys' >> ~/.bashrc
echo 'export SES_DEFAULT_SENDER=noreply@example.com' >> ~/.bashrc
```

## 🚀 **Step 6: Deploy to AWS**

### Validate Configuration
```bash
# Test serverless configuration
serverless config validate
```

### Deploy
```bash
# Deploy to development stage
serverless deploy

# Deploy to specific region
serverless deploy --region us-east-1

# Deploy to production stage
serverless deploy --stage prod
```

### Verify Deployment
```bash
# Get deployment information
serverless info

# Test health endpoint
curl -X GET https://your-api-url/health
```

## 🧪 **Step 7: Test the API**

### Basic Functionality Test
```bash
curl -X POST https://your-api-url/submit-form \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "to_email": "test@example.com",
    "from_email": "noreply@example.com",
    "subject": "Test Form Submission",
    "source_url": "https://testsite.com/contact",
    "fields": {
      "name": "Test User",
      "email": "user@example.com",
      "message": "This is a test message"
    }
  }'
```

**Expected Response:**
```json
{
  "email_id": "ses-message-id",
  "message": "Form submitted successfully"
}
```

### Authentication Test
```bash
# Test without API key (should fail)
curl -X POST https://your-api-url/submit-form \
  -H "Content-Type: application/json" \
  -d '{"to_email": "test@domain.com", "fields": {"test": "data"}}'

# Expected: 401 Unauthorized
```

### Rate Limiting Test
```bash
# Send multiple requests quickly to test rate limiting
for i in {1..15}; do
  curl -X POST https://your-api-url/submit-form \
    -H "X-API-Key: your-api-key" \
    -H "Content-Type: application/json" \
    -d '{"to_email": "test@domain.com", "fields": {"test": "'$i'"}}'
  sleep 1
done

# Should see 429 Rate Limit Exceeded after 10 requests
```

## 📊 **Step 8: DNS Configuration for Better Deliverability**

### SPF Record
```
Type: TXT
Name: example.com
Value: v=spf1 include:amazonses.com ~all
TTL: 300
```

### DMARC Record
```
Type: TXT
Name: _dmarc.example.com
Value: v=DMARC1; p=quarantine; rua=mailto:admin@example.com
TTL: 300
```

### DKIM Setup (After Domain Verification)
```bash
# Enable DKIM
aws ses set-identity-dkim-enabled --identity example.com --dkim-enabled

# Get DKIM tokens
aws ses get-identity-dkim-attributes --identities example.com
```

Add the 3 CNAME records returned:
```
Type: CNAME
Name: [token1]._domainkey.example.com
Value: [token1].dkim.amazonses.com

Type: CNAME
Name: [token2]._domainkey.example.com
Value: [token2].dkim.amazonses.com

Type: CNAME
Name: [token3]._domainkey.example.com
Value: [token3].dkim.amazonses.com
```

## 🎛️ **Step 9: Configuration Customization**

### Update Rate Limits
Edit `app/utils/rate_limiter.py`:
```python
self.limits = {
    'per_minute': 20,    # Increase from 10
    'per_hour': 500,     # Increase from 100
    'per_day': 5000      # Increase from 1000
}
```

### Customize Email Templates
Edit `app/handlers/email_handler.py`:
- Modify `_generate_email_body()` for HTML template
- Modify `_generate_text_body()` for plain text template
- Update sender name in the SES call

### Add Custom Validation
Edit `app/utils/validation.py`:
- Add custom field validations
- Modify spam detection patterns
- Add domain-specific validation rules

## 🔄 **Step 10: Redeploy Changes**

```bash
# After making code changes
serverless deploy

# For faster function-only updates
serverless deploy function -f api
```

## 📈 **Step 11: Monitoring and Management**

### View Logs
```bash
# View recent logs
serverless logs -f api

# Follow logs in real-time
serverless logs -f api --tail
```

### Monitor SES Usage
```bash
# Check sending quota and usage
aws ses get-send-quota
aws ses get-send-statistics

# Check reputation
aws ses get-reputation --identity example.com
```

### CloudWatch Metrics
- Go to AWS Console → CloudWatch → Metrics
- Check `AWS/Lambda` and `AWS/SES` namespaces
- Set up alarms for error rates and usage

## 🗑️ **Step 12: Cleanup (Optional)**

```bash
# Remove the entire stack
serverless remove

# Remove specific stage
serverless remove --stage prod
```

## 🔐 **Security Best Practices**

### API Key Management
```bash
# Rotate API keys regularly
python3 -c "
from app.auth.api_key_auth import generate_api_key
print('New key:', generate_api_key('client1-v2'))
"

# Update environment variable
export VALID_API_KEYS=old-key,new-key  # Keep both during transition
# Later remove old key: export VALID_API_KEYS=new-key
```

### Environment Variables
- Use AWS Systems Manager Parameter Store for production
- Never commit API keys to version control
- Use different keys for different environments

### Monitoring
```bash
# Set up CloudWatch alarms
aws cloudwatch put-metric-alarm \
  --alarm-name "High-Email-Error-Rate" \
  --alarm-description "Alert when email error rate is high" \
  --metric-name Bounce \
  --namespace AWS/SES \
  --statistic Average \
  --period 300 \
  --threshold 5.0 \
  --comparison-operator GreaterThanThreshold
```

## 🌍 **Step 13: Multi-Environment Setup**

### Development Environment
```bash
serverless deploy --stage dev
```

### Staging Environment
```bash
export VALID_API_KEYS=staging-key-1,staging-key-2
export SES_DEFAULT_SENDER=staging@example.com
serverless deploy --stage staging
```

### Production Environment
```bash
export VALID_API_KEYS=prod-key-1,prod-key-2
export SES_DEFAULT_SENDER=noreply@example.com
serverless deploy --stage prod
```

## 🚨 **Troubleshooting**

### Common Issues

**1. SES Email Rejected**
```bash
# Check if email/domain is verified
aws ses get-identity-verification-attributes --identities example.com

# Check if in sandbox mode
aws ses get-send-quota
# If Max24HourSend is 200, you're in sandbox mode
```

**2. Lambda Timeout Errors**
```yaml
# Increase timeout in serverless.yml
provider:
  timeout: 30  # Increase from default 6 seconds
```

**3. API Gateway CORS Issues**
```yaml
# Ensure CORS is properly configured in serverless.yml
http:
  cors:
    origin: '*'
    headers:
      - Content-Type
      - X-API-Key
```

**4. Environment Variable Issues**
```bash
# Verify variables are set
echo $VALID_API_KEYS
echo $SES_DEFAULT_SENDER

# Check deployed environment variables
aws lambda get-function-configuration --function-name mayfly-forms-api-dev-api
```

### Debug Logs
```bash
# Enable debug logging
export SLS_DEBUG=*
serverless deploy

# Check CloudWatch logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/mayfly-forms"
```

## 📞 **Support**

### AWS Documentation
- [SES Developer Guide](https://docs.aws.amazon.com/ses/)
- [Lambda Developer Guide](https://docs.aws.amazon.com/lambda/)
- [API Gateway Developer Guide](https://docs.aws.amazon.com/apigateway/)

### Useful Commands
```bash
# Check AWS service status
aws sts get-caller-identity
aws ses get-send-quota
aws lambda list-functions --query 'Functions[?contains(FunctionName, `mayfly`)]'

# Test SES directly
aws ses send-email \
  --source noreply@example.com \
  --destination ToAddresses=test@example.com \
  --message 'Subject={Data="Test"},Body={Text={Data="Test message"}}'
```

## 🎯 **Next Steps**

1. **Integrate with client websites** using the API endpoints
2. **Set up monitoring and alerting** for production use
3. **Implement backup strategies** for important configurations
4. **Scale as needed** by adjusting rate limits and SES quotas
5. **Consider CDN integration** for global performance optimization

## 📋 **Deployment Checklist**

- [ ] AWS CLI configured with proper permissions
- [ ] SES sender email/domain verified
- [ ] SES production access requested (and approved)
- [ ] DNS records added (SPF, DMARC, DKIM)
- [ ] API keys generated and stored securely
- [ ] Environment variables configured
- [ ] Serverless Framework deployed successfully
- [ ] API endpoints tested and working
- [ ] Rate limiting tested
- [ ] Authentication tested
- [ ] Email delivery tested
- [ ] Monitoring and logging configured
- [ ] Security best practices implemented

Your Mayfly Forms API is now ready for production use! 🚀