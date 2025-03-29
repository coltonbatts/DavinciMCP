#!/usr/bin/env python3
"""
gemini_handler.py - Google Gemini AI API Handler

This module provides the GeminiAPIHandler class for integrating with
Google's Gemini Generative AI API for intelligent video editing assistance.
"""

import logging
from typing import Optional, Dict, Any, List
import google.generativeai as genai

# Logger for this module
logger = logging.getLogger(__name__)

class GeminiAPIHandler:
    """
    Class for Gemini API operations
    Handles AI-assisted operations using Google's Generative AI
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.initialized = False
        self.model = None
        self.generation_config = None
        if api_key:
            self.initialize(api_key)
        else:
            logger.info("Gemini API Handler created but not initialized (needs API key)")
    
    def initialize(self, api_key: str) -> bool:
        """
        Initialize the Gemini API connection
        
        Args:
            api_key (str): The API key for authentication
            
        Returns:
            bool: True if initialization is successful
        """
        try:
            self.api_key = api_key
            genai.configure(api_key=self.api_key)
            
            # Set default model to Gemini Pro
            self.model = genai.GenerativeModel('gemini-pro')
            
            # Default generation config
            # Temperature values can be updated from config when handler is used
            self.generation_config = {
                "temperature": 0.7,  # Default value
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 1024,  # Default value
            }
            
            self.initialized = True
            logger.info("Gemini API successfully initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {str(e)}")
            self.initialized = False
            return False
    
    def generate_response(self, prompt: str) -> str:
        """
        Generate a response using the Gemini API
        
        Args:
            prompt (str): The input prompt
            
        Returns:
            str: The generated response
        """
        if not self.initialized:
            logger.warning("Gemini API not initialized")
            return "Error: API not initialized"
            
        try:
            logger.info(f"Processing prompt: {prompt[:50]}...")
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_msg = f"Error generating response from Gemini API: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
    
    def generate_with_config(self, 
                           prompt: str, 
                           temperature: Optional[float] = None, 
                           max_output_tokens: Optional[int] = None) -> str:
        """
        Generate a response with custom configuration
        
        Args:
            prompt (str): The input prompt
            temperature (float, optional): Controls randomness (0.0-1.0)
            max_output_tokens (int, optional): Maximum length of response
            
        Returns:
            str: The generated response
        """
        if not self.initialized:
            logger.warning("Gemini API not initialized")
            return "Error: API not initialized"
        
        try:
            # Create a custom generation config
            generation_config = self.generation_config.copy()
            if temperature is not None:
                generation_config["temperature"] = max(0.0, min(1.0, temperature))
            if max_output_tokens is not None:
                generation_config["max_output_tokens"] = max_output_tokens
                
            logger.info(f"Processing prompt with custom config: {prompt[:50]}...")
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            return response.text
            
        except Exception as e:
            error_msg = f"Error generating response with custom config: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
            
    def chat_session(self, messages: List[Dict[str, str]]) -> str:
        """
        Handle a multi-turn conversation with Gemini
        
        Args:
            messages (List[Dict[str, str]]): List of conversation messages
                Each message should have 'role' (user/model) and 'content' keys
                
        Returns:
            str: The response from Gemini
        """
        if not self.initialized:
            logger.warning("Gemini API not initialized")
            return "Error: API not initialized"
            
        try:
            logger.info(f"Processing chat session with {len(messages)} messages")
            
            # Convert to the format needed by Gemini API
            chat = self.model.start_chat(history=[])
            
            # Add messages
            response = None
            for msg in messages:
                if msg["role"] == "user":
                    response = chat.send_message(msg["content"])
                    
            if response:
                return response.text
            else:
                return "No response generated from chat session"
                
        except Exception as e:
            error_msg = f"Error in chat session: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}" 