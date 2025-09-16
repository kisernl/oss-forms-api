import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime

class EmailHandler:
    def __init__(self):
        # AWS SES configuration (AWS_REGION is automatically provided by Lambda)
        self.aws_region = os.environ.get('AWS_REGION', 'us-east-1')
        self.ses_client = boto3.client('ses', region_name=self.aws_region)
        
        # Default sender email - should be verified in SES
        self.default_sender = os.environ.get('SES_DEFAULT_SENDER', 'noreply@example.com')
        
        # Verify SES configuration
        try:
            self.ses_client.get_send_quota()
        except NoCredentialsError:
            raise ValueError("AWS credentials not configured. Please configure AWS credentials.")
        except Exception as e:
            print(f"Warning: Could not verify SES configuration: {str(e)}")
    
    def send_form_email(self, form_data):
        """Send form submission via AWS SES"""
        try:
            # Extract form fields
            to_email = form_data.get('to_email')
            from_email = form_data.get('from_email', self.default_sender)
            form_fields = form_data.get('fields', {})
            
            # Create a more professional, less spammy subject line
            customer_name = form_fields.get('name', 'Website Visitor')
            source_url = form_data.get('source_url', '')
            source_domain = source_url.split('/')[2] if source_url and len(source_url.split('/')) > 2 else 'your website'
            
            default_subject = f"New Form Submission from {customer_name} via {source_domain}"
            subject = form_data.get('subject', default_subject)
            
            # Generate email content
            html_body = self._generate_email_body(form_fields, form_data)
            text_body = self._generate_text_body(form_fields)
            
            # Prepare sender with proper name
            sender_name = "Contact Form"
            formatted_source = f"{sender_name} <{from_email}>"
            
            # Add reply-to if customer provided email
            reply_to_addresses = []
            customer_email = form_fields.get('email')
            if customer_email and '@' in customer_email:
                reply_to_addresses = [customer_email]
            
            # Send email using SES
            ses_params = {
                'Source': formatted_source,
                'Destination': {
                    'ToAddresses': [to_email]
                },
                'Message': {
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Html': {
                            'Data': html_body,
                            'Charset': 'UTF-8'
                        },
                        'Text': {
                            'Data': text_body,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            }
            
            # Add reply-to if available
            if reply_to_addresses:
                ses_params['ReplyToAddresses'] = reply_to_addresses
            
            response = self.ses_client.send_email(**ses_params)
            
            return {
                'success': True,
                'email_id': response['MessageId'],
                'message': 'Email sent successfully via AWS SES'
            }
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            # Handle specific SES errors
            if error_code == 'MessageRejected':
                return {
                    'success': False,
                    'error': f'Email rejected: {error_message}'
                }
            elif error_code == 'MailFromDomainNotVerified':
                return {
                    'success': False,
                    'error': f'Sender domain not verified: {error_message}'
                }
            elif error_code == 'ConfigurationSetDoesNotExist':
                return {
                    'success': False,
                    'error': f'Configuration set error: {error_message}'
                }
            else:
                return {
                    'success': False,
                    'error': f'AWS SES error ({error_code}): {error_message}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def _generate_email_body(self, form_fields, form_data):
        """Generate professional HTML email body"""
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p UTC")
        customer_name = form_fields.get('name', 'A potential customer')
        source_url = form_data.get('source_url', 'your website')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>New Customer Inquiry</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background-color: #f8f9fa; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #4a4a4a 0%, #2c2c2c 100%); color: white; padding: 30px 20px; text-align: center; }}
                .content {{ padding: 30px; }}
                .intro {{ font-size: 16px; margin-bottom: 25px; color: #555; }}
                .details {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .field {{ margin-bottom: 15px; }}
                .field-label {{ font-weight: 600; color: #333; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; }}
                .field-value {{ margin-top: 5px; font-size: 16px; color: #555; padding: 8px 0; border-bottom: 1px solid #e9ecef; }}
                .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; font-size: 14px; color: #6c757d; }}
                .timestamp {{ font-style: italic; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0; font-weight: 300;">New Form Submission</h1>
                </div>
                <div class="content">
                    <div class="intro">
                        <strong>{customer_name}</strong> has reached out to you through {source_url}. Here are the details of their form submission:
                    </div>
                    <div class="details">
        """
        
        # Add form fields
        for field_name, field_value in form_fields.items():
            if field_value:  # Only include non-empty fields
                html += f"""
                <div class="field">
                    <div class="field-label">{field_name.replace('_', ' ').title()}:</div>
                    <div class="field-value">{str(field_value)}</div>
                </div>
                """
        
        # Add metadata
        if form_data.get('source_url'):
            html += f"""
            <div class="field">
                <div class="field-label">Source URL:</div>
                <div class="field-value">{form_data['source_url']}</div>
            </div>
            """
        
        html += f"""
                    </div>
                </div>
                <div class="footer">
                    <div class="timestamp">Received on {timestamp}</div>
                    <div style="margin-top: 10px;">
                        <em>This inquiry was sent through your website contact form.</em>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_text_body(self, form_fields):
        """Generate plain text email body from form fields"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        text = "NEW FORM SUBMISSION\n"
        text += "=" * 30 + "\n\n"
        
        for field_name, field_value in form_fields.items():
            if field_value:
                text += f"{field_name.replace('_', ' ').title()}: {field_value}\n"
        
        text += f"\nSubmitted on: {timestamp}"
        
        return text