#!/usr/bin/env python3
"""
Google Gemini API Client
Handles interactions with Google's Gemini models
"""

import os
import logging
from typing import List, Dict, Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GeminiClient:
    """Client for interacting with Google Gemini API"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-1.5-flash"
    ):
        """
        Initialize Gemini client
        
        Args:
            api_key: Google AI Studio API key (defaults to GEMINI_API_KEY env var)
            model_name: Model to use (gemini-1.5-pro, gemini-1.5-flash)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model_name = model_name
        
        if not self.api_key:
            logger.warning("No Gemini API key provided - Gemini will be unavailable")
            self.enabled = False
            return
        
        try:
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            
            # Initialize model
            self.model = genai.GenerativeModel(model_name)
            self.enabled = True
            
            logger.info(f"Gemini client initialized with model: {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.enabled = False
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048  # Gemini needs at least 50 tokens to generate text
    ) -> str:
        """
        Send chat request to Gemini
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Response text from Gemini
        """
        if not self.enabled:
            raise RuntimeError("Gemini client not enabled - check API key")
        
        try:
            # Convert messages to Gemini format
            # Gemini uses a simpler format - just concatenate user messages
            prompt = self._format_messages(messages)
            
            # Generate response
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extract text from response
            if not response.candidates:
                logger.warning("No candidates in Gemini response")
                return "I'm sorry, I couldn't generate a response."
            
            candidate = response.candidates[0]
            
            # Check if response was truncated due to token limit
            from google.ai.generativelanguage_v1beta.types import Candidate
            if candidate.finish_reason == Candidate.FinishReason.MAX_TOKENS:
                logger.warning("Gemini response truncated - increase max_tokens")
            
            if not candidate.content or not candidate.content.parts:
                logger.warning("No content in Gemini response")
                return "I'm sorry, I couldn't generate a response."
            
            # Extract text from all parts
            text_parts = []
            for part in candidate.content.parts:
                if hasattr(part, 'text') and part.text:
                    text_parts.append(part.text)
            
            if text_parts:
                return ''.join(text_parts)
            
            logger.warning("No text parts found in Gemini response")
            return "I'm sorry, I couldn't generate a response."
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}", exc_info=True)
            raise RuntimeError(f"Gemini API error: {str(e)}")
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """
        Format messages for Gemini
        
        Gemini 1.5 models accept a simple prompt string.
        We'll format conversation history as context.
        """
        formatted_parts = []
        
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            if role == 'system':
                formatted_parts.append(f"Instructions: {content}")
            elif role == 'user':
                formatted_parts.append(f"User: {content}")
            elif role == 'assistant':
                formatted_parts.append(f"Assistant: {content}")
        
        return "\n\n".join(formatted_parts)
    
    def health_check(self) -> bool:
        """
        Check if Gemini API is accessible
        
        Returns:
            True if API is responding, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            # Simple test generation
            response = self.model.generate_content(
                "Say 'OK' if you can hear me.",
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=10
                )
            )
            return bool(response.text)
        except Exception as e:
            logger.error(f"Gemini health check failed: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """
        List available Gemini models
        
        Returns:
            List of model names
        """
        if not self.enabled:
            return []
        
        try:
            models = genai.list_models()
            return [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        except Exception as e:
            logger.error(f"Failed to list Gemini models: {e}")
            return []

