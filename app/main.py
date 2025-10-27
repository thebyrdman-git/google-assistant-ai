#!/usr/bin/env python3
"""
Google Assistant AI Webhook Service
Connects Google Assistant to LiteLLM-powered AI models
"""

import os
import logging
from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, generate_latest
from pythonjsonlogger import jsonlogger

from webhook import handle_webhook
from litellm_client import LiteLLMClient

# Configure structured logging
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s'
)
logHandler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'assistant_requests_total',
    'Total number of webhook requests',
    ['intent', 'status']
)
REQUEST_DURATION = Histogram(
    'assistant_request_duration_seconds',
    'Request processing duration'
)
AI_RESPONSE_TIME = Histogram(
    'assistant_ai_response_time_seconds',
    'AI model response time'
)

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize LiteLLM client
litellm_client = LiteLLMClient(
    base_url=os.getenv('LITELLM_BASE_URL', 'http://localhost:4000/v1'),
    api_key=os.getenv('LITELLM_API_KEY', '***REMOVED***'),
    model=os.getenv('LITELLM_MODEL', 'granite-3.2-8b-instruct')
)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check LiteLLM connectivity
        litellm_healthy = litellm_client.health_check()
        
        if litellm_healthy:
            return jsonify({
                'status': 'healthy',
                'service': 'google-assistant-ai',
                'litellm': 'connected'
            }), 200
        else:
            return jsonify({
                'status': 'degraded',
                'service': 'google-assistant-ai',
                'litellm': 'unavailable'
            }), 503
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503


@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()


@app.route('/webhook', methods=['POST'])
@REQUEST_DURATION.time()
def webhook():
    """
    Main webhook endpoint for Google Assistant/Dialogflow
    
    Handles incoming requests from Google Assistant and returns
    voice-optimized responses from LiteLLM models.
    """
    try:
        # Parse request
        if not request.is_json:
            logger.warning("Non-JSON request received")
            REQUEST_COUNT.labels(intent='unknown', status='error').inc()
            return jsonify({
                'fulfillmentText': 'Sorry, I received an invalid request format.'
            }), 400
        
        request_data = request.get_json()
        
        # Log request (sanitized)
        logger.info(
            "Webhook request received",
            extra={
                'intent': request_data.get('queryResult', {}).get('intent', {}).get('displayName'),
                'session': request_data.get('session', 'unknown')[:20] + '...'
            }
        )
        
        # Handle webhook
        response = handle_webhook(request_data, litellm_client)
        
        # Track metrics
        intent_name = request_data.get('queryResult', {}).get('intent', {}).get('displayName', 'unknown')
        REQUEST_COUNT.labels(intent=intent_name, status='success').inc()
        
        logger.info(
            "Webhook response sent",
            extra={'intent': intent_name}
        )
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(
            "Webhook processing error",
            extra={'error': str(e)},
            exc_info=True
        )
        REQUEST_COUNT.labels(intent='error', status='error').inc()
        
        # Return friendly error message
        return jsonify({
            'fulfillmentText': 'Sorry, I encountered an error processing your request. Please try again.'
        }), 200  # Return 200 to avoid Google Assistant error messages


@app.route('/', methods=['GET'])
def root():
    """Root endpoint - service information"""
    return jsonify({
        'service': 'google-assistant-ai',
        'version': '1.0.0',
        'endpoints': {
            'webhook': '/webhook',
            'health': '/health',
            'metrics': '/metrics'
        }
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


if __name__ == '__main__':
    # Development server
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting Google Assistant AI Webhook Service on port {port}")
    logger.info(f"LiteLLM endpoint: {litellm_client.base_url}")
    logger.info(f"Default model: {litellm_client.model}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )

