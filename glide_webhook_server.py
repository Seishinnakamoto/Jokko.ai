#!/usr/bin/env python3
"""
Glide Webhook Server for Multilingual Chatbot
Handles incoming requests from Glide apps and processes them through the chatbot system

Features:
- REST API endpoints for Glide integration
- Webhook handling for real-time chat
- JSON response formatting for Glide
- Error handling and logging
- CORS support for web apps
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from aiohttp import web, ClientSession
from aiohttp.web import Request, Response, json_response
from aiohttp_cors import setup, CorsConfig, ResourceOptions
import uuid

from multilingual_chatbot import MultilingualChatbot, ChatMessage

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GlideWebhookServer:
    """Webhook server for Glide app integration"""
    
    def __init__(self, groq_api_key: str, libretranslate_url: str = None, port: int = 8000):
        self.port = port
        self.chatbot = MultilingualChatbot(groq_api_key, libretranslate_url)
        self.app = web.Application()
        self.setup_routes()
        self.setup_cors()
        
    def setup_routes(self):
        """Setup API routes"""
        self.app.router.add_post('/webhook/chat', self.handle_chat_webhook)
        self.app.router.add_post('/api/chat', self.handle_chat_api)
        self.app.router.add_get('/api/languages', self.get_supported_languages)
        self.app.router.add_get('/api/health', self.health_check)
        self.app.router.add_delete('/api/chat/{user_id}/history', self.clear_chat_history)
        
        # Static file serving for testing
        self.app.router.add_get('/', self.serve_test_page)
        
    def setup_cors(self):
        """Setup CORS for cross-origin requests"""
        cors = setup(self.app, defaults={
            "*": ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Add CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    async def handle_chat_webhook(self, request: Request) -> Response:
        """Handle webhook requests from Glide apps"""
        try:
            data = await request.json()
            logger.info(f"Received webhook data: {data}")
            
            # Extract data from Glide webhook format
            user_id = data.get('user_id', str(uuid.uuid4()))
            message = data.get('message', '')
            language = data.get('language', 'auto')
            session_id = data.get('session_id')
            
            if not message:
                return json_response({
                    'error': 'Message is required',
                    'status': 'error'
                }, status=400)
            
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
            
            # Format response for Glide
            glide_response = {
                'response': response.translated_response,
                'original_response': response.response,
                'detected_language': response.target_language,
                'processing_time': response.processing_time,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
            logger.info(f"Sending response: {glide_response}")
            return json_response(glide_response)
            
        except Exception as e:
            logger.error(f"Webhook error: {str(e)}")
            return json_response({
                'error': str(e),
                'status': 'error'
            }, status=500)
    
    async def handle_chat_api(self, request: Request) -> Response:
        """Handle direct API requests (alternative to webhook)"""
        try:
            data = await request.json()
            
            # Validate required fields
            required_fields = ['message']
            for field in required_fields:
                if field not in data:
                    return json_response({
                        'error': f'Missing required field: {field}',
                        'status': 'error'
                    }, status=400)
            
            user_id = data.get('user_id', str(uuid.uuid4()))
            message = data['message']
            language = data.get('language', 'auto')
            session_id = data.get('session_id')
            
            # Create chat message
            chat_message = ChatMessage(
                user_id=user_id,
                message=message,
                language=language,
                timestamp=datetime.now(),
                session_id=session_id
            )
            
            # Process message
            response = await self.chatbot.process_message(chat_message)
            
            # Return structured response
            return json_response({
                'data': {
                    'response': response.translated_response,
                    'original_response': response.response,
                    'detected_language': response.target_language,
                    'original_language': response.original_language,
                    'processing_time': response.processing_time,
                    'user_id': user_id,
                    'session_id': session_id
                },
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"API error: {str(e)}")
            return json_response({
                'error': str(e),
                'status': 'error',
                'timestamp': datetime.now().isoformat()
            }, status=500)
    
    async def get_supported_languages(self, request: Request) -> Response:
        """Get list of supported languages"""
        try:
            languages = self.chatbot.get_supported_languages()
            
            # Format for Glide dropdown/selection
            language_options = [
                {
                    'code': code,
                    'name': name,
                    'display_name': f"{name} ({code.upper()})"
                }
                for code, name in languages.items()
            ]
            
            return json_response({
                'data': {
                    'languages': language_options,
                    'total_count': len(language_options)
                },
                'status': 'success'
            })
            
        except Exception as e:
            logger.error(f"Languages API error: {str(e)}")
            return json_response({
                'error': str(e),
                'status': 'error'
            }, status=500)
    
    async def health_check(self, request: Request) -> Response:
        """Health check endpoint"""
        return json_response({
            'status': 'healthy',
            'service': 'Multilingual Chatbot Webhook Server',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    
    async def clear_chat_history(self, request: Request) -> Response:
        """Clear chat history for a specific user"""
        try:
            user_id = request.match_info['user_id']
            self.chatbot.clear_conversation_history(user_id)
            
            return json_response({
                'message': f'Chat history cleared for user {user_id}',
                'status': 'success'
            })
            
        except Exception as e:
            logger.error(f"Clear history error: {str(e)}")
            return json_response({
                'error': str(e),
                'status': 'error'
            }, status=500)
    
    async def serve_test_page(self, request: Request) -> Response:
        """Serve a simple test page"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Multilingual Chatbot Test</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .chat-box { border: 1px solid #ddd; padding: 20px; margin: 20px 0; }
                input, select, button { margin: 10px 0; padding: 10px; width: 100%; }
                button { background: #007bff; color: white; border: none; cursor: pointer; }
                button:hover { background: #0056b3; }
                .response { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Multilingual Chatbot Test Interface</h1>
                <div class="chat-box">
                    <h3>Test the chatbot API</h3>
                    <input type="text" id="userId" placeholder="User ID (optional)" />
                    <select id="language">
                        <option value="auto">Auto-detect</option>
                        <option value="it">Italiano</option>
                        <option value="en">English</option>
                        <option value="fr">Français</option>
                        <option value="wo">Wolof</option>
                        <option value="ha">Hausa</option>
                        <option value="sw">Kiswahili</option>
                    </select>
                    <input type="text" id="message" placeholder="Type your message here..." />
                    <button onclick="sendMessage()">Send Message</button>
                    <div id="response" class="response" style="display:none;"></div>
                </div>
            </div>
            
            <script>
                async function sendMessage() {
                    const userId = document.getElementById('userId').value || 'test-user';
                    const language = document.getElementById('language').value;
                    const message = document.getElementById('message').value;
                    
                    if (!message) {
                        alert('Please enter a message');
                        return;
                    }
                    
                    try {
                        const response = await fetch('/api/chat', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                user_id: userId,
                                language: language,
                                message: message
                            })
                        });
                        
                        const data = await response.json();
                        
                        const responseDiv = document.getElementById('response');
                        if (data.status === 'success') {
                            responseDiv.innerHTML = `
                                <h4>Response:</h4>
                                <p><strong>Bot:</strong> ${data.data.response}</p>
                                <p><small>Language: ${data.data.detected_language} | Time: ${data.data.processing_time.toFixed(2)}s</small></p>
                            `;
                        } else {
                            responseDiv.innerHTML = `<p style="color:red;">Error: ${data.error}</p>`;
                        }
                        responseDiv.style.display = 'block';
                        
                    } catch (error) {
                        document.getElementById('response').innerHTML = `<p style="color:red;">Network error: ${error.message}</p>`;
                        document.getElementById('response').style.display = 'block';
                    }
                }
                
                // Allow Enter key to send message
                document.getElementById('message').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        sendMessage();
                    }
                });
            </script>
        </body>
        </html>
        """
        
        return web.Response(text=html_content, content_type='text/html')
    
    async def start_server(self):
        """Start the webhook server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        
        logger.info(f"Webhook server started on port {self.port}")
        logger.info(f"Test interface available at: http://localhost:{self.port}")
        logger.info(f"Webhook endpoint: http://localhost:{self.port}/webhook/chat")
        logger.info(f"API endpoint: http://localhost:{self.port}/api/chat")
        
        # Keep server running
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
        finally:
            await runner.cleanup()

# Main execution
async def main():
    """Main function to start the server"""
    # Get configuration from environment variables
    groq_api_key = os.getenv('GROQ_API_KEY')
    libretranslate_url = os.getenv('LIBRETRANSLATE_URL', 'https://libretranslate.com/translate')
    port = int(os.getenv('PORT', 8000))
    
    if not groq_api_key:
        logger.error("GROQ_API_KEY environment variable is required")
        return
    
    # Create and start server
    server = GlideWebhookServer(groq_api_key, libretranslate_url, port)
    await server.start_server()

if __name__ == "__main__":
    asyncio.run(main())