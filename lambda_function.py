import serverless_wsgi
from app.main import create_app

app = create_app()

def lambda_handler(event, context):
    """AWS Lambda handler function"""
    return serverless_wsgi.handle_request(app, event, context)