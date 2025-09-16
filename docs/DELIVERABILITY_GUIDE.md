# Email Deliverability Guide

This guide will help you prevent form emails from going to spam folders.

## 🚨 **Critical Issue: Why Emails Go to Spam**

1. **No domain authentication** - Using hello@example.com without proper DNS setup
2. **Missing SPF, DKIM, DMARC records**
3. **No sender reputation** 
4. **Generic content patterns**

## 🛡️ **Step 1: DNS Records Setup (Required)**

Add these DNS records to your `example.com` domain:

### Domain Verification
```
Type: TXT
Name: _amazonses.example.com
Value: 1lZgb6a40H8/5n16/BnTkpinXXrqeTed2NPnLcgtD+Q=
TTL: 300
```

### SPF Record (Prevents Spoofing)
```
Type: TXT  
Name: example.com
Value: v=spf1 include:amazonses.com ~all
TTL: 300
```

### DMARC Record (Email Authentication)
```
Type: TXT
Name: _dmarc.example.com  
Value: v=DMARC1; p=quarantine; rua=mailto:admin@example.com
TTL: 300
```

## 🔧 **Step 2: After DNS Records Propagate (24-48 hours)**

Run these commands to enable DKIM:

```bash
# Check domain verification status
aws ses get-identity-verification-attributes --identities example.com

# Enable DKIM (after domain is verified)
aws ses set-identity-dkim-enabled --identity example.com --dkim-enabled

# Get DKIM tokens for DNS
aws ses get-identity-dkim-attributes --identities example.com
```

You'll get 3 DKIM tokens to add as CNAME records:
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

## 🚀 **Step 3: Request SES Production Access**

Currently you're in SES Sandbox mode. Request production access:

1. **Via AWS Console:**
   - Go to [SES Console](https://console.aws.amazon.com/ses/)
   - Click "Request production access"
   - Fill out use case: "Contact form submissions for client websites"

2. **Benefits of Production Access:**
   - Send to ANY email address (not just verified ones)
   - Higher sending limits
   - Better reputation management
   - No sandbox restrictions

## 📧 **Step 4: Improve Email Content**

Update the email handler to be less "spammy":

### Current Issues:
- Generic subject lines
- Form-like content structure
- No personalization

### Improvements Needed:
```python
# Instead of: "New Form Submission"
subject = f"New inquiry from {form_fields.get('name', 'Website Visitor')} - {form_data.get('source_domain', 'Your Website')}"

# Add legitimate business context
# Include proper sender identification
# Use professional email templates
```

## 🎯 **Step 5: Immediate Workarounds**

While waiting for DNS propagation:

### Option A: Use Different Sender Address
```bash
# Verify a sender that doesn't look like forms
aws ses verify-email-identity --email-address inquiries@example.com
```

### Option B: Add Reply-To Headers
Update the email handler to include:
```python
# In the SES send_email call, add:
'ReplyToAddresses': [form_fields.get('email', 'noreply@example.com')]
```

### Option C: Warm Up Your Domain
Send a few legitimate test emails manually to build reputation.

## 📊 **Step 6: Monitor Deliverability**

Set up CloudWatch monitoring:
```bash
# Check bounce/complaint rates
aws ses get-send-statistics

# Monitor reputation
aws cloudwatch get-metric-statistics \
  --namespace AWS/SES \
  --metric-name Bounce \
  --start-time 2024-01-01 \
  --end-time 2024-01-31 \
  --period 86400 \
  --statistics Average
```

## 🎯 **Quick Wins (Do These Now)**

1. **Better Subject Lines:**
   ```
   ❌ "New Form Submission"
   ✅ "New inquiry from [Name] about your services"
   ```

2. **Professional From Name:**
   ```
   ❌ hello@example.com
   ✅ "Mayfly Creative Contact Form" <hello@example.com>
   ```

3. **Add Business Context:**
   ```
   ❌ Generic form fields
   ✅ "A potential client has contacted you through your website"
   ```

## 🚨 **Critical Actions Required**

**Today:**
1. Add the DNS TXT record for domain verification
2. Update email content to be less form-like
3. Request SES production access

**This Week:**
4. Add SPF, DMARC records  
5. Enable DKIM after domain verification
6. Test with various email providers

**Results Expected:**
- 90%+ inbox delivery rate
- Professional appearance
- No more spam folder issues

## 🔍 **Testing Deliverability**

Use these tools to test:
- [Mail-Tester.com](https://mail-tester.com) - Get spam score
- [MXToolbox](https://mxtoolbox.com/deliverability) - Check DNS records
- Send tests to Gmail, Outlook, Yahoo

## 📞 **Need Help?**

If emails still go to spam after these changes:
1. Check AWS SES reputation dashboard
2. Review bounce/complaint rates  
3. Consider using a dedicated IP (for high volume)
4. Contact AWS Support for deliverability review

**Target:** 95%+ inbox delivery rate within 1-2 weeks of proper setup.