import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from app.handlers.email_handler import EmailHandler
from app.auth.api_key_auth import require_api_key
from app.utils.validation import validate_form_data
from app.utils.rate_limiter import RateLimiter

def create_app():
    app = Flask(__name__)
    
    # Enable CORS for all domains
    CORS(app, origins="*", methods=["POST", "OPTIONS"])
    
    # Initialize services
    email_handler = EmailHandler()
    rate_limiter = RateLimiter()
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "service": "mayfly-forms"})
    
    @app.route('/submit-form', methods=['POST'])
    @require_api_key
    def submit_form():
        try:
            # Rate limiting check
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            api_key = request.headers.get('X-API-Key')
            
            if not rate_limiter.is_allowed(client_ip, api_key):
                return jsonify({"error": "Rate limit exceeded"}), 429
            
            # Validate request data
            form_data = request.get_json()
            if not form_data:
                return jsonify({"error": "No JSON data provided"}), 400
            
            validation_result = validate_form_data(form_data)
            if not validation_result['valid']:
                return jsonify({"error": validation_result['message']}), 400
            
            # Send email
            result = email_handler.send_form_email(form_data)
            
            if result['success']:
                return jsonify({
                    "message": "Form submitted successfully",
                    "email_id": result['email_id']
                }), 200
            else:
                return jsonify({"error": result['error']}), 500
                
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint not found"}), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"error": "Method not allowed"}), 405
    
    return app

if __name__ == '__main__':
    app = create_app()
    # Use environment variable for debug mode, default to False for security
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() in ('true', '1', 'yes', 'on')
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug_mode, port=port)