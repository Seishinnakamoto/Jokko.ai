#!/usr/bin/env python3
"""
Multilingual Chatbot System
Integrates Glide App input, Groq API processing, and LibreTranslate translation

Features:
- Glide app webhook integration
- Groq API for AI responses
- LibreTranslate for automatic translation
- Support for 12+ languages
- Make.com alternative automation
"""

import asyncio
import json
import logging
import os
import aiohttp
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupportedLanguage(Enum):
    """Supported languages enum"""
    ITALIAN = "it"
    FRENCH = "fr"
    ENGLISH = "en"
    WOLOF = "wo"
    BAMBARA = "bm"
    HAUSA = "ha"
    SWAHILI = "sw"
    TIGRINYA = "ti"
    AMHARIC = "am"
    SONINKE = "snk"
    FULFULDE = "ff"
    LINGALA = "ln"

@dataclass
class ChatMessage:
    """Chat message data structure"""
    user_id: str
    message: str
    language: str
    timestamp: datetime
    session_id: Optional[str] = None

@dataclass
class ChatResponse:
    """Chat response data structure"""
    response: str
    original_language: str
    translated_response: str
    target_language: str
    processing_time: float

class LibreTranslateClient:
    """LibreTranslate API client for automatic translation"""
    
    def __init__(self, base_url: str = "https://libretranslate.com/translate"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text using LibreTranslate API"""
        try:
            # LibreTranslate language code mapping
            lang_mapping = {
                'it': 'it', 'fr': 'fr', 'en': 'en', 'wo': 'wo',
                'bm': 'bm', 'ha': 'ha', 'sw': 'sw', 'ti': 'ti',
                'am': 'am', 'snk': 'snk', 'ff': 'ff', 'ln': 'ln'
            }
            
            source_code = lang_mapping.get(source_lang, 'auto')
            target_code = lang_mapping.get(target_lang, 'en')
            
            payload = {
                'q': text,
                'source': source_code,
                'target': target_code,
                'format': 'text'
            }
            
            async with self.session.post(self.base_url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('translatedText', text)
                else:
                    logger.error(f"LibreTranslate API error: {response.status}")
                    return text
                    
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return text
    
    async def detect_language(self, text: str) -> str:
        """Detect language of input text"""
        try:
            # Simple pattern-based detection as fallback
            patterns = {
                'it': ['che', 'per', 'con', 'del', 'una', 'sono', 'dove', 'come'],
                'fr': ['que', 'pour', 'avec', 'des', 'une', 'suis', 'où', 'comment'],
                'en': ['that', 'for', 'with', 'the', 'and', 'are', 'where', 'how'],
                'wo': ['ku', 'ak', 'ci', 'la', 'nga', 'am', 'fan', 'naka'],
                'ha': ['da', 'mai', 'na', 'ta', 'ka', 'ba', 'ina', 'yaya'],
                'sw': ['na', 'wa', 'ya', 'za', 'la', 'ni', 'wapi', 'jinsi']
            }
            
            text_lower = text.lower()
            scores = {}
            
            for lang, words in patterns.items():
                score = sum(1 for word in words if word in text_lower)
                scores[lang] = score
            
            if scores:
                detected = max(scores, key=scores.get)
                if scores[detected] > 0:
                    return detected
            
            return 'it'  # Default to Italian
            
        except Exception as e:
            logger.error(f"Language detection error: {str(e)}")
            return 'it'

class GroqAPIClient:
    """Groq API client for AI processing"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def generate_response(self, message: str, language: str, context: List[str] = None) -> str:
        """Generate AI response using Groq API"""
        try:
            # System prompt for multilingual assistance
            system_prompt = f"""
            You are JOKKO AI, a multilingual assistant helping migrants and refugees in Italy.
            Respond in {language} language.
            Provide helpful, accurate information about:
            - Immigration procedures
            - Healthcare access
            - Employment rights
            - Housing assistance
            - Education opportunities
            
            Be empathetic, culturally sensitive, and provide practical advice.
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            # Add context from previous conversation if available
            if context:
                for ctx in context[-3:]:  # Last 3 messages for context
                    messages.insert(-1, {"role": "assistant", "content": ctx})
            
            payload = {
                "model": "mixtral-8x7b-32768",  # Groq's Mixtral model
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000,
                "stream": False
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(self.base_url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    logger.error(f"Groq API error: {response.status}")
                    return "Mi dispiace, non riesco a rispondere in questo momento. Riprova più tardi."
                    
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            return "Si è verificato un errore. Riprova più tardi."

class MultilingualChatbot:
    """Main multilingual chatbot class"""
    
    def __init__(self, groq_api_key: str, libretranslate_url: str = None):
        self.groq_api_key = groq_api_key
        self.libretranslate_url = libretranslate_url or "https://libretranslate.com/translate"
        self.conversation_history = {}
        self.supported_languages = {lang.value: lang.name.title() for lang in SupportedLanguage}
        
    async def process_message(self, chat_message: ChatMessage) -> ChatResponse:
        """Process incoming chat message and generate response"""
        start_time = time.time()
        
        try:
            async with LibreTranslateClient(self.libretranslate_url) as translator:
                async with GroqAPIClient(self.groq_api_key) as groq:
                    
                    # Detect language if not specified
                    if not chat_message.language or chat_message.language == 'auto':
                        chat_message.language = await translator.detect_language(chat_message.message)
                    
                    # Get conversation context
                    context = self.conversation_history.get(chat_message.user_id, [])
                    
                    # Translate message to Italian for processing if needed
                    message_for_processing = chat_message.message
                    if chat_message.language != 'it':
                        message_for_processing = await translator.translate(
                            chat_message.message, chat_message.language, 'it'
                        )
                    
                    # Generate AI response in Italian
                    ai_response = await groq.generate_response(
                        message_for_processing, 'it', context
                    )
                    
                    # Translate response back to user's language if needed
                    translated_response = ai_response
                    if chat_message.language != 'it':
                        translated_response = await translator.translate(
                            ai_response, 'it', chat_message.language
                        )
                    
                    # Update conversation history
                    if chat_message.user_id not in self.conversation_history:
                        self.conversation_history[chat_message.user_id] = []
                    
                    self.conversation_history[chat_message.user_id].append({
                        'user': chat_message.message,
                        'assistant': translated_response,
                        'timestamp': chat_message.timestamp
                    })
                    
                    # Keep only last 10 exchanges
                    if len(self.conversation_history[chat_message.user_id]) > 10:
                        self.conversation_history[chat_message.user_id] = \
                            self.conversation_history[chat_message.user_id][-10:]
                    
                    processing_time = time.time() - start_time
                    
                    return ChatResponse(
                        response=ai_response,
                        original_language='it',
                        translated_response=translated_response,
                        target_language=chat_message.language,
                        processing_time=processing_time
                    )
                    
        except Exception as e:
            logger.error(f"Message processing error: {str(e)}")
            processing_time = time.time() - start_time
            
            return ChatResponse(
                response="Si è verificato un errore durante l'elaborazione del messaggio.",
                original_language='it',
                translated_response="An error occurred while processing the message.",
                target_language=chat_message.language,
                processing_time=processing_time
            )
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.supported_languages
    
    def clear_conversation_history(self, user_id: str):
        """Clear conversation history for a user"""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]

# Test the chatbot
async def test_chatbot():
    """Test the multilingual chatbot"""
    # Note: Replace with your actual Groq API key
    groq_api_key = os.getenv('GROQ_API_KEY', 'your-groq-api-key-here')
    
    chatbot = MultilingualChatbot(groq_api_key)
    
    # Test messages in different languages
    test_messages = [
        ChatMessage(
            user_id="user1",
            message="Come posso ottenere il permesso di soggiorno?",
            language="it",
            timestamp=datetime.now()
        ),
        ChatMessage(
            user_id="user2", 
            message="How can I find a job in Italy?",
            language="en",
            timestamp=datetime.now()
        ),
        ChatMessage(
            user_id="user3",
            message="Comment puis-je accéder aux soins de santé?",
            language="fr",
            timestamp=datetime.now()
        )
    ]
    
    for message in test_messages:
        print(f"\n--- Processing message in {message.language} ---")
        print(f"User: {message.message}")
        
        response = await chatbot.process_message(message)
        
        print(f"Response: {response.translated_response}")
        print(f"Processing time: {response.processing_time:.2f}s")

if __name__ == "__main__":
    asyncio.run(test_chatbot())