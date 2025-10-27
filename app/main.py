#!/usr/bin/env python3
"""
Google Assistant AI Webhook Service
Connects Google Assistant to LiteLLM-powered AI models
"""

import os
import time
import logging
from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, generate_latest
from pythonjsonlogger import jsonlogger

from app.webhook import handle_webhook
from app.litellm_client import LiteLLMClient
from app.gemini_client import GeminiClient

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

# Initialize LiteLLM client (local models)
litellm_client = LiteLLMClient(
    base_url=os.getenv('LITELLM_BASE_URL', 'http://localhost:4000/v1'),
    api_key=os.getenv('LITELLM_API_KEY', 'sk-pai-hatter-red-hat-ai-models-2025'),
    model=os.getenv('LITELLM_MODEL', 'mistral-7b-instruct')
)

# Initialize Gemini client (Google Cloud)
gemini_client = GeminiClient(
    api_key=os.getenv('GEMINI_API_KEY'),
    model_name=os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring (fast, no AI calls)"""
    try:
        # Service is healthy if Flask is running
        # Don't make actual AI calls here - too slow for health checks
        return jsonify({
            'status': 'healthy',
            'service': 'ai-chat-gateway',
            'backends': {
                'litellm': 'configured',
                'gemini': 'enabled' if gemini_client.enabled else 'disabled'
            }
        }), 200
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


@app.route('/chat', methods=['POST'])
def chat():
    """
    Unified chat endpoint
    
    Accepts OpenAI-style chat completions and routes to appropriate backend.
    
    Request body:
    {
        "model": "gemini-1.5-flash" | "mistral-7b-instruct" | etc.,
        "messages": [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."}
        ],
        "temperature": 0.7,
        "max_tokens": 2048
    }
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        # Extract parameters
        model = data.get('model', 'gemini-1.5-flash')
        messages = data.get('messages', [])
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens', 2048)
        
        if not messages:
            return jsonify({'error': 'messages array is required'}), 400
        
        # Route to appropriate backend
        if model.startswith('gemini') or model.startswith('models/gemini'):
            # Use Gemini API
            if not gemini_client.enabled:
                return jsonify({
                    'error': 'Gemini backend not available',
                    'hint': 'Set GEMINI_API_KEY environment variable'
                }), 503
            
            response_text = gemini_client.chat(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            backend = 'gemini'
        else:
            # Use LiteLLM (local models)
            response_text = litellm_client.chat(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            backend = 'litellm'
        
        # Return OpenAI-compatible response
        return jsonify({
            'id': 'chat-' + os.urandom(8).hex(),
            'object': 'chat.completion',
            'created': int(time.time()),
            'model': model,
            'backend': backend,
            'choices': [{
                'index': 0,
                'message': {
                    'role': 'assistant',
                    'content': response_text
                },
                'finish_reason': 'stop'
            }]
        }), 200
        
    except RuntimeError as e:
        logger.error(f"Chat processing error: {e}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


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

