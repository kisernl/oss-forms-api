# AWS SES Setup Guide

This guide will help you set up AWS Simple Email Service (SES) for the Mayfly Forms API.

## Overview

AWS SES requires verification of sender email addresses or domains before you can send emails. This prevents spam and ensures deliverability.

## Step 1: Verify Email Address or Domain

### Option A: Verify Individual Email Address

```bash
# Verify a specific email address
aws ses verify-email-identity --email-address noreply@example.com

# Check verification status
aws ses get-identity-verification-attributes --identities noreply@example.com
```

### Option B: Verify Entire Domain (Recommended for Production)

```bash
# Verify a domain
aws ses verify-domain-identity --domain example.com

# Get the DNS verification record
aws ses get-identity-verification-attributes --identities example.com
```

You'll need to add a TXT record to your domain's DNS settings with the verification token provided.

## Step 2: Move Out of SES Sandbox (Production)

By default, SES starts in "sandbox mode" with these limitations:
- Can only send to verified email addresses
- Limited to 200 emails per 24 hours
- Maximum send rate of 1 email per second

### Request Production Access

1. **Via AWS Console:**
   - Go to SES Console → Account dashboard
   - Click "Request production access"
   - Fill out the use case form

2. **Via AWS CLI:**
   ```bash
   aws sesv2 put-account-sending-enabled --sending-enabled
   ```

### Production Access Benefits
- Send to any email address
- Higher sending limits (starts at 200/day, can request increases)
- Better reputation management

## Step 3: Configure DNS Records (Domain Verification)

When verifying a domain, you'll get DNS records to add:

### TXT Record for Domain Verification
```
Name: _amazonses.example.com
Value: [verification-token-from-aws]
Type: TXT
```

### Optional: DKIM Records (Recommended)
DKIM improves email deliverability:

```bash
# Enable DKIM for your domain
aws ses put-identity-dkim-attributes --identity example.com --dkim-enabled

# Get DKIM tokens
aws ses get-identity-dkim-attributes --identities example.com
```

Add three CNAME records:
```
Name: [token1]._domainkey.example.com
Value: [token1].dkim.amazonses.com
Type: CNAME

Name: [token2]._domainkey.example.com
Value: [token2].dkim.amazonses.com
Type: CNAME

Name: [token3]._domainkey.example.com
Value: [token3].dkim.amazonses.com
Type: CNAME
```

## Step 4: Set Sending Limits (Optional)

Check your current limits:
```bash
aws ses get-send-quota
aws ses get-send-statistics
```

Request limit increases if needed:
```bash
# This opens a support case for limit increase
aws support create-case \
  --subject "SES Sending Limit Increase Request" \
  --service-code "ses" \
  --severity-code "normal" \
  --category-code "limits" \
  --communication-body "Please increase my SES sending limits for domain: example.com"
```

## Step 5: Configure Environment Variables

Set these in your deployment environment:

```bash
export SES_DEFAULT_SENDER=noreply@example.com
export AWS_REGION=us-east-1  # Choose your preferred region
export VALID_API_KEYS=your-api-key-1,your-api-key-2
```

## Step 6: Test Your Setup

Create a test script to verify SES is working:

```python
import boto3
from botocore.exceptions import ClientError

def test_ses():
    ses = boto3.client('ses', region_name='us-east-1')
    
    try:
        response = ses.send_email(
            Source='noreply@example.com',
            Destination={'ToAddresses': ['test@example.com']},
            Message={
                'Subject': {'Data': 'SES Test Email'},
                'Body': {'Text': {'Data': 'This is a test email from SES!'}}
            }
        )
        print(f"Email sent successfully! Message ID: {response['MessageId']}")
        return True
    except ClientError as e:
        print(f"Error: {e.response['Error']['Message']}")
        return False

if __name__ == "__main__":
    test_ses()
```

## Troubleshooting

### Common Issues

1. **Email not verified**: Make sure sender email is verified in SES
2. **Still in sandbox**: Request production access if sending to unverified addresses
3. **Region mismatch**: Ensure your Lambda and SES are in the same region
4. **IAM permissions**: Verify your Lambda has SES permissions

### Check SES Status

```bash
# Check if email/domain is verified
aws ses get-identity-verification-attributes --identities example.com

# Check sending statistics
aws ses get-send-statistics

# List verified identities
aws ses list-verified-email-addresses
aws ses list-identities
```

### Monitor Email Delivery

Set up CloudWatch alarms for:
- Bounce rate
- Complaint rate
- Send rate
- Reputation metrics

```bash
# Get reputation info
aws ses get-reputation --identity example.com
```

## Security Best Practices

1. **Use IAM roles** instead of access keys for Lambda
2. **Restrict SES permissions** to only necessary actions
3. **Monitor bounce/complaint rates** to maintain reputation
4. **Implement proper error handling** in your application
5. **Use HTTPS** for all API endpoints
6. **Validate input** to prevent email injection attacks

## Cost Optimization

- Use the free tier wisely (62,000 emails/month from EC2)
- Monitor usage with CloudWatch
- Set up billing alerts
- Consider using SES in us-east-1 for lowest costs

## Next Steps

After completing setup:
1. Deploy your Mayfly Forms API
2. Test with verified email addresses
3. Request production access if needed
4. Monitor email delivery metrics
5. Scale as needed