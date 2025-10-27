"""
LiteLLM Client
Handles communication with LiteLLM proxy server
"""

import logging
from typing import Dict, List, Any, Optional
import openai
from openai import OpenAI

logger = logging.getLogger(__name__)


class LiteLLMClient:
    """Client for interacting with LiteLLM proxy"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:4000/v1",
        api_key: str = "***REMOVED***",
        model: str = "granite-3.2-8b-instruct"
    ):
        """
        Initialize LiteLLM client
        
        Args:
            base_url: LiteLLM proxy URL
            api_key: API key for authentication
            model: Default model to use
        """
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        
        # Initialize OpenAI client pointing to LiteLLM
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        
        logger.info(f"Initialized LiteLLM client: {base_url}, model: {model}")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 150,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get chat completion from AI model
        
        Args:
            messages: Conversation history
            model: Model to use (defaults to self.model)
            max_tokens: Maximum tokens in response
            temperature: Response randomness (0.0-1.0)
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary with 'content' and 'usage' keys
        """
        try:
            # Add system prompt for voice assistant context
            enhanced_messages = self._add_system_prompt(messages)
            
            # Call LiteLLM
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=enhanced_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Extract response
            content = response.choices[0].message.content
            usage = {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
            
            logger.info(
                "Chat completion successful",
                extra={'tokens': usage['total_tokens']}
            )
            
            return {
                'content': content,
                'usage': usage
            }
            
        except openai.APIError as e:
            logger.error(f"LiteLLM API error: {e}")
            raise Exception(f"AI service unavailable: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in chat completion: {e}")
            raise
    
    def _add_system_prompt(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Add system prompt for voice assistant context
        
        Args:
            messages: Original conversation messages
            
        Returns:
            Enhanced messages with system prompt
        """
        # Check if system prompt already exists
        if messages and messages[0].get('role') == 'system':
            return messages
        
        # Add voice-optimized system prompt
        system_prompt = {
            "role": "system",
            "content": (
                "You are a helpful AI assistant integrated with Google Assistant. "
                "Provide concise, clear responses optimized for voice output. "
                "Keep responses under 3 sentences when possible. "
                "Avoid markdown formatting, code blocks, and long URLs. "
                "Be conversational and friendly."
            )
        }
        
        return [system_prompt] + messages
    
    def health_check(self) -> bool:
        """
        Check if LiteLLM service is healthy
        
        Returns:
            True if service is responsive, False otherwise
        """
        try:
            # Try a simple completion
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return bool(response.choices)
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False

