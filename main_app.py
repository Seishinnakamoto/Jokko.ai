#!/usr/bin/env python3
"""
Main Application - Multilingual Chatbot System
Integrates Glide App input, Groq API processing, LibreTranslate translation, and automation

Usage:
    python main_app.py

Environment Variables Required:
    GROQ_API_KEY - Your Groq API key

Optional Environment Variables:
    LIBRETRANSLATE_URL - LibreTranslate service URL
    SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD - Email configuration
    PORT - Server port (default: 8000)
"""

import asyncio
import logging
import sys
from datetime import datetime
from typing import Dict, Any

from config import load_config, validate_config
from multilingual_chatbot import MultilingualChatbot, ChatMessage
from glide_webhook_server import GlideWebhookServer
from automation_engine import create_automation_engine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MultilingualChatbotApp:
    """Main application class that orchestrates all components"""
    
    def __init__(self):
        self.config = None
        self.chatbot = None
        self.webhook_server = None
        self.automation_engine = None
        self.running = False
    
    async def initialize(self):
        """Initialize all application components"""
        try:
            # Load and validate configuration
            logger.info("Loading configuration...")
            self.config = load_config()
            
            issues = validate_config(self.config)
            if issues:
                logger.error("Configuration validation failed:")
                for issue in issues:
                    logger.error(f"  - {issue}")
                return False
            
            logger.info("Configuration loaded successfully")
            
            # Initialize chatbot
            logger.info("Initializing multilingual chatbot...")
            self.chatbot = MultilingualChatbot(
                groq_api_key=self.config.groq.api_key,
                libretranslate_url=self.config.libretranslate.base_url
            )
            
            # Initialize automation engine
            if self.config.enable_automation:
                logger.info("Initializing automation engine...")
                self.automation_engine = create_automation_engine()
                self.automation_engine.start_scheduler()
            
            # Initialize webhook server with enhanced integration
            logger.info("Initializing webhook server...")
            self.webhook_server = EnhancedGlideWebhookServer(
                chatbot=self.chatbot,
                automation_engine=self.automation_engine,
                config=self.config
            )
            
            logger.info("Application initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}")
            return False
    
    async def start(self):
        """Start the application"""
        if not await self.initialize():
            logger.error("Failed to initialize application")
            return False
        
        try:
            logger.info("Starting multilingual chatbot application...")
            logger.info(f"Server will run on {self.config.server.host}:{self.config.server.port}")
            logger.info(f"Supported languages: {list(self.config.supported_languages.keys())}")
            
            self.running = True
            await self.webhook_server.start_server()
            
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
            await self.shutdown()
        except Exception as e:
            logger.error(f"Application error: {str(e)}")
            await self.shutdown()
    
    async def shutdown(self):
        """Gracefully shutdown the application"""
        logger.info("Shutting down application...")
        self.running = False
        
        if self.automation_engine:
            self.automation_engine.stop_scheduler()
        
        logger.info("Application shutdown complete")

class EnhancedGlideWebhookServer(GlideWebhookServer):
    """Enhanced webhook server with automation integration"""
    
    def __init__(self, chatbot: MultilingualChatbot, automation_engine, config):
        self.chatbot = chatbot
        self.automation_engine = automation_engine
        self.config = config
        
        # Initialize parent class components
        self.port = config.server.port
        self.app = self._create_app()
        self.setup_routes()
        self.setup_cors()
    
    def _create_app(self):
        """Create aiohttp application with middleware"""
        from aiohttp import web
        
        app = web.Application()
        
        # Add middleware for request logging
        @web.middleware
        async def logging_middleware(request, handler):
            start_time = datetime.now()
            
            try:
                response = await handler(request)
                
                # Log request
                processing_time = (datetime.now() - start_time).total_seconds()
                logger.info(f"{request.method} {request.path} - {response.status} - {processing_time:.3f}s")
                
                return response
                
            except Exception as e:
                processing_time = (datetime.now() - start_time).total_seconds()
                logger.error(f"{request.method} {request.path} - ERROR - {processing_time:.3f}s - {str(e)}")
                raise
        
        app.middlewares.append(logging_middleware)
        return app
    
    async def handle_chat_webhook(self, request):
        """Enhanced webhook handler with automation integration"""
        try:
            data = await request.json()
            logger.info(f"Received webhook data: {data}")
            
            # Extract and validate data
            user_id = data.get('user_id', f"user_{int(datetime.now().timestamp())}")
            message = data.get('message', '')
            language = data.get('language', 'auto')
            session_id = data.get('session_id')
            
            if not message:
                return self._error_response('Message is required', 400)
            
            # Create chat message
            chat_message = ChatMessage(
                user_id=user_id,
                message=message,
                language=language,
                timestamp=datetime.now(),
                session_id=session_id
            )
            
            # Process message through chatbot
            response = await self.chatbot.process_message(chat_message)
            
            # Trigger automation workflows
            if self.automation_engine:
                automation_data = {
                    'chat_data': {
                        'user_id': user_id,
                        'message': message,
                        'response': response.translated_response,
                        'language': response.target_language,
                        'processing_time': response.processing_time,
                        'session_id': session_id
                    }
                }
                
                # Trigger webhook-based workflows
                await self.automation_engine.trigger_webhook('/webhook/chat', automation_data)
            
            # Format response for Glide
            glide_response = {
                'response': response.translated_response,
                'original_response': response.response,
                'detected_language': response.target_language,
                'processing_time': response.processing_time,
                'timestamp': datetime.now().isoformat(),
                'status': 'success',
                'user_id': user_id,
                'session_id': session_id
            }
            
            logger.info(f"Sending response to user {user_id}: {response.translated_response[:100]}...")
            return self._json_response(glide_response)
            
        except Exception as e:
            logger.error(f"Webhook error: {str(e)}")
            return self._error_response(str(e), 500)
    
    async def get_analytics(self, request):
        """Get analytics data"""
        try:
            if not self.automation_engine:
                return self._error_response("Analytics not enabled", 404)
            
            days = int(request.query.get('days', 7))
            stats = self.automation_engine.db_manager.get_chat_stats(days)
            
            return self._json_response({
                'data': stats,
                'status': 'success'
            })
            
        except Exception as e:
            logger.error(f"Analytics error: {str(e)}")
            return self._error_response(str(e), 500)
    
    async def get_workflow_status(self, request):
        """Get workflow status"""
        try:
            if not self.automation_engine:
                return self._error_response("Automation not enabled", 404)
            
            status = self.automation_engine.get_workflow_status()
            
            return self._json_response({
                'data': status,
                'status': 'success'
            })
            
        except Exception as e:
            logger.error(f"Workflow status error: {str(e)}")
            return self._error_response(str(e), 500)
    
    def setup_routes(self):
        """Setup enhanced API routes"""
        # Call parent setup
        super().setup_routes()
        
        # Add new routes
        self.app.router.add_get('/api/analytics', self.get_analytics)
        self.app.router.add_get('/api/workflows', self.get_workflow_status)
        self.app.router.add_get('/api/config', self.get_config_info)
    
    async def get_config_info(self, request):
        """Get public configuration information"""
        try:
            config_info = {
                'supported_languages': self.config.supported_languages,
                'features': {
                    'automation': self.config.enable_automation,
                    'analytics': self.config.enable_analytics,
                    'email_notifications': self.config.email is not None
                },
                'version': '1.0.0',
                'endpoints': {
                    'webhook': '/webhook/chat',
                    'api': '/api/chat',
                    'languages': '/api/languages',
                    'health': '/api/health',
                    'analytics': '/api/analytics',
                    'workflows': '/api/workflows'
                }
            }
            
            return self._json_response({
                'data': config_info,
                'status': 'success'
            })
            
        except Exception as e:
            logger.error(f"Config info error: {str(e)}")
            return self._error_response(str(e), 500)
    
    def _json_response(self, data: Dict[str, Any], status: int = 200):
        """Helper method to create JSON response"""
        from aiohttp.web import json_response
        return json_response(data, status=status)
    
    def _error_response(self, message: str, status: int = 500):
        """Helper method to create error response"""
        return self._json_response({
            'error': message,
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }, status)

# CLI interface
def print_banner():
    """Print application banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                  🤖 MULTILINGUAL CHATBOT                     ║
    ║                                                              ║
    ║  Integrazione completa per app Glide con:                   ║
    ║  • Groq API per elaborazione AI                             ║
    ║  • LibreTranslate per traduzione automatica                ║
    ║  • Sistema di automazione (alternativa a Make.com)         ║
    ║  • Supporto per 12+ lingue africane ed europee             ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_help():
    """Print help information"""
    help_text = """
    Uso: python main_app.py [opzioni]
    
    Variabili d'ambiente richieste:
      GROQ_API_KEY          Chiave API Groq (obbligatoria)
    
    Variabili d'ambiente opzionali:
      LIBRETRANSLATE_URL    URL servizio LibreTranslate
      PORT                  Porta server (default: 8000)
      SMTP_SERVER           Server SMTP per notifiche email
      SMTP_PORT             Porta SMTP
      SMTP_USERNAME         Username SMTP
      SMTP_PASSWORD         Password SMTP
      ADMIN_EMAIL           Email amministratore
    
    Endpoints disponibili:
      POST /webhook/chat    Webhook per app Glide
      POST /api/chat        API diretta per chat
      GET  /api/languages   Lista lingue supportate
      GET  /api/health      Controllo stato sistema
      GET  /api/analytics   Statistiche utilizzo
      GET  /api/workflows   Stato workflow automazione
      GET  /                Interfaccia di test
    
    Lingue supportate:
      it (Italiano), fr (Français), en (English), wo (Wolof),
      bm (Bamanankan), ha (Hausa), sw (Kiswahili), ti (Tigrinya),
      am (Amharic), snk (Soninke), ff (Fulfulde), ln (Lingala)
    """
    print(help_text)

async def main():
    """Main entry point"""
    print_banner()
    
    # Check for help flag
    if '--help' in sys.argv or '-h' in sys.argv:
        print_help()
        return
    
    # Check for required environment variables
    import os
    if not os.getenv('GROQ_API_KEY'):
        logger.error("GROQ_API_KEY environment variable is required")
        logger.info("Get your API key from: https://console.groq.com/")
        print_help()
        return
    
    # Create and start application
    app = MultilingualChatbotApp()
    await app.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        sys.exit(1)