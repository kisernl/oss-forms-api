#!/bin/bash

# Mayfly Forms API Deployment Script

set -e

echo "🚀 Deploying Mayfly Forms API..."

# Check if required environment variables are set
if [ -z "$VALID_API_KEYS" ]; then
    echo "❌ Error: VALID_API_KEYS environment variable is required"
    echo "   Please set it with: export VALID_API_KEYS=key1,key2,key3"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ Error: AWS credentials not configured"
    echo "   Please configure AWS CLI with: aws configure"
    exit 1
fi

echo "✅ AWS credentials configured"

# Optional: Check if SES sender email is provided
if [ -n "$SES_DEFAULT_SENDER" ]; then
    echo "📧 Using SES sender email: $SES_DEFAULT_SENDER"
else
    echo "⚠️  Warning: SES_DEFAULT_SENDER not set, using default 'noreply@example.com'"
    echo "   You may want to set it with: export SES_DEFAULT_SENDER=your-verified-email@example.com"
fi

# Get deployment stage (default to 'dev')
STAGE=${1:-dev}

echo "📦 Installing Serverless Framework if not installed..."
if ! command -v serverless &> /dev/null; then
    npm install -g serverless
fi

echo "📦 Installing serverless plugins..."
if [ ! -d node_modules ]; then
    npm init -y
fi
npm install serverless-python-requirements

echo "📤 Deploying to AWS Lambda (stage: $STAGE)..."
serverless deploy --stage $STAGE

echo "✅ Deployment complete!"
echo "📋 API Info:"
serverless info --stage $STAGE

echo ""
echo "🔗 Your API is ready! Test it with:"
echo "curl -X GET https://\$(serverless info --stage $STAGE | grep ServiceEndpoint | cut -d' ' -f2)/health"