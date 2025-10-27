"""
Google Assistant Webhook Handler
Processes Google Dialogflow/Actions requests and generates responses
"""

import logging
from typing import Dict, Any
from app.conversation import ConversationManager

logger = logging.getLogger(__name__)

# Initialize conversation manager
conversation_manager = ConversationManager()


def handle_webhook(request_data: Dict[str, Any], litellm_client) -> Dict[str, Any]:
    """
    Process webhook request from Google Assistant/Dialogflow
    
    Args:
        request_data: The JSON payload from Google
        litellm_client: LiteLLM client instance
        
    Returns:
        Response dictionary formatted for Google Assistant
    """
    try:
        # Extract key information from request
        query_result = request_data.get('queryResult', {})
        intent_name = query_result.get('intent', {}).get('displayName', '')
        query_text = query_result.get('queryText', '')
        session_id = request_data.get('session', 'default')
        
        logger.info(f"Processing intent: {intent_name}, query: {query_text}")
        
        # Handle different intents
        if intent_name == 'Default Welcome Intent':
            response_text = handle_welcome()
        elif intent_name == 'Default Fallback Intent':
            response_text = handle_fallback()
        elif intent_name == 'Ask AI':
            response_text = handle_ai_query(
                query_text, 
                session_id, 
                litellm_client
            )
        else:
            # For any other intent, use AI to respond
            response_text = handle_ai_query(
                query_text, 
                session_id, 
                litellm_client
            )
        
        # Format response for Google Assistant
        return format_response(response_text)
        
    except Exception as e:
        logger.error(f"Error handling webhook: {e}", exc_info=True)
        return format_response(
            "I'm having trouble processing that right now. Could you try asking in a different way?"
        )


def handle_welcome() -> str:
    """Generate welcome message"""
    return (
        "Hi! I'm your personal AI assistant powered by Granite. "
        "I can help you with questions, information, and conversations. "
        "What would you like to know?"
    )


def handle_fallback() -> str:
    """Generate fallback message when intent not recognized"""
    return (
        "I didn't quite catch that. Could you rephrase your question? "
        "I'm here to help with information and answer your questions."
    )


def handle_ai_query(query_text: str, session_id: str, litellm_client) -> str:
    """
    Send query to AI model and get response
    
    Args:
        query_text: The user's question
        session_id: Session identifier for conversation context
        litellm_client: LiteLLM client instance
        
    Returns:
        AI-generated response text
    """
    try:
        # Get conversation history
        conversation_history = conversation_manager.get_history(session_id)
        
        # Add user message to history
        conversation_history.append({
            "role": "user",
            "content": query_text
        })
        
        # Get AI response
        ai_response = litellm_client.chat_completion(
            messages=conversation_history,
            max_tokens=150,  # Keep responses concise for voice
            temperature=0.7
        )
        
        # Extract response text
        response_text = ai_response.get('content', '')
        
        # Optimize for voice (remove markdown, long URLs, etc.)
        response_text = optimize_for_voice(response_text)
        
        # Update conversation history
        conversation_history.append({
            "role": "assistant",
            "content": response_text
        })
        conversation_manager.update_history(session_id, conversation_history)
        
        return response_text
        
    except Exception as e:
        logger.error(f"Error getting AI response: {e}", exc_info=True)
        return (
            "I'm having trouble connecting to my AI brain right now. "
            "Please try again in a moment."
        )


def optimize_for_voice(text: str) -> str:
    """
    Optimize text for voice output
    
    - Remove markdown formatting
    - Shorten long URLs
    - Break up long sentences
    - Remove code blocks
    
    Args:
        text: Raw AI response text
        
    Returns:
        Voice-optimized text
    """
    # Remove markdown code blocks
    text = text.replace('```', '')
    
    # Remove markdown bold/italic
    text = text.replace('**', '').replace('__', '').replace('*', '').replace('_', '')
    
    # Replace long URLs with "see the link in your app"
    import re
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    if re.search(url_pattern, text):
        text = re.sub(url_pattern, 'check the link I sent to your phone', text)
    
    # Limit length (Google Assistant works best with shorter responses)
    max_length = 500
    if len(text) > max_length:
        text = text[:max_length].rsplit(' ', 1)[0] + '...'
    
    return text.strip()


def format_response(text: str) -> Dict[str, Any]:
    """
    Format response for Google Assistant/Dialogflow
    
    Args:
        text: Response text to send
        
    Returns:
        Formatted response dictionary
    """
    return {
        'fulfillmentText': text,
        'fulfillmentMessages': [
            {
                'text': {
                    'text': [text]
                }
            }
        ]
    }

