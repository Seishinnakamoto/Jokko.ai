#!/usr/bin/env python3
"""
Configuration file for Multilingual Chatbot System
Centralizes all configuration settings and environment variables
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class GroqConfig:
    """Groq API configuration"""
    api_key: str
    base_url: str = "https://api.groq.com/openai/v1/chat/completions"
    model: str = "mixtral-8x7b-32768"
    temperature: float = 0.7
    max_tokens: int = 1000

@dataclass
class LibreTranslateConfig:
    """LibreTranslate configuration"""
    base_url: str = "https://libretranslate.com/translate"
    api_key: Optional[str] = None  # For self-hosted instances

@dataclass
class EmailConfig:
    """Email configuration for notifications"""
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    admin_email: str

@dataclass
class ServerConfig:
    """Server configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

@dataclass
class DatabaseConfig:
    """Database configuration"""
    path: str = "automation.db"
    backup_interval_hours: int = 24

@dataclass
class ChatbotConfig:
    """Main chatbot configuration"""
    groq: GroqConfig
    libretranslate: LibreTranslateConfig
    email: Optional[EmailConfig]
    server: ServerConfig
    database: DatabaseConfig
    supported_languages: Dict[str, str]
    enable_automation: bool = True
    enable_analytics: bool = True
    log_level: str = "INFO"

# Supported languages mapping
SUPPORTED_LANGUAGES = {
    'it': 'Italiano',
    'fr': 'Français', 
    'en': 'English',
    'wo': 'Wolof',
    'bm': 'Bamanankan',
    'ha': 'هَرْشَن هَوْسَ',
    'sw': 'Kiswahili',
    'ti': 'ትግርኛ',
    'am': 'አማርኛ',
    'snk': 'Soninkanxanne',
    'ff': 'Fulfulde',
    'ln': 'Lingála'
}

# Default system prompts for different languages
SYSTEM_PROMPTS = {
    'it': """
    Sei JOKKO AI, un assistente virtuale multilingue specializzato nell'aiutare migranti e rifugiati in Italia.
    Fornisci informazioni accurate, pratiche e aggiornate su:
    - Procedure di immigrazione e permesso di soggiorno
    - Accesso ai servizi sanitari
    - Diritti lavorativi e ricerca del lavoro
    - Assistenza abitativa
    - Opportunità educative e corsi di italiano
    
    Sii empatico, culturalmente sensibile e fornisci consigli pratici.
    Rispondi sempre in italiano, anche se la domanda è in un'altra lingua.
    """,
    
    'en': """
    You are JOKKO AI, a multilingual virtual assistant specialized in helping migrants and refugees in Italy.
    Provide accurate, practical, and up-to-date information about:
    - Immigration procedures and residence permits
    - Healthcare access
    - Employment rights and job searching
    - Housing assistance
    - Educational opportunities and Italian language courses
    
    Be empathetic, culturally sensitive, and provide practical advice.
    Always respond in English, even if the question is in another language.
    """,
    
    'fr': """
    Tu es JOKKO AI, un assistant virtuel multilingue spécialisé dans l'aide aux migrants et réfugiés en Italie.
    Fournis des informations précises, pratiques et à jour sur:
    - Procédures d'immigration et permis de séjour
    - Accès aux soins de santé
    - Droits du travail et recherche d'emploi
    - Assistance au logement
    - Opportunités éducatives et cours d'italien
    
    Sois empathique, culturellement sensible et fournis des conseils pratiques.
    Réponds toujours en français, même si la question est dans une autre langue.
    """
}

# Glide App integration settings
GLIDE_WEBHOOK_CONFIG = {
    'webhook_endpoint': '/webhook/chat',
    'api_endpoint': '/api/chat',
    'expected_fields': ['user_id', 'message', 'language'],
    'response_format': {
        'response': 'string',
        'detected_language': 'string',
        'processing_time': 'float',
        'timestamp': 'string',
        'status': 'string'
    }
}

# Make.com alternative workflows
DEFAULT_WORKFLOWS = [
    {
        'id': 'chat_logging',
        'name': 'Chat Interaction Logging',
        'description': 'Log all chat interactions to database',
        'trigger': {'type': 'webhook', 'endpoint': '/webhook/chat'},
        'actions': [{'type': 'log_database', 'table': 'chat_logs'}]
    },
    {
        'id': 'daily_stats',
        'name': 'Daily Statistics Report',
        'description': 'Send daily usage statistics to admin',
        'trigger': {'type': 'schedule', 'time': '09:00'},
        'actions': [{'type': 'send_email', 'template': 'daily_stats'}]
    },
    {
        'id': 'error_notification',
        'name': 'Error Notification',
        'description': 'Notify admin of system errors',
        'trigger': {'type': 'api_call', 'endpoint': '/api/error'},
        'actions': [{'type': 'notify_admin', 'priority': 'high'}]
    }
]

def load_config() -> ChatbotConfig:
    """Load configuration from environment variables"""
    
    # Groq configuration
    groq_api_key = os.getenv('GROQ_API_KEY')
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable is required")
    
    groq_config = GroqConfig(
        api_key=groq_api_key,
        model=os.getenv('GROQ_MODEL', 'mixtral-8x7b-32768'),
        temperature=float(os.getenv('GROQ_TEMPERATURE', '0.7')),
        max_tokens=int(os.getenv('GROQ_MAX_TOKENS', '1000'))
    )
    
    # LibreTranslate configuration
    libretranslate_config = LibreTranslateConfig(
        base_url=os.getenv('LIBRETRANSLATE_URL', 'https://libretranslate.com/translate'),
        api_key=os.getenv('LIBRETRANSLATE_API_KEY')
    )
    
    # Email configuration (optional)
    email_config = None
    if all(os.getenv(key) for key in ['SMTP_SERVER', 'SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD']):
        email_config = EmailConfig(
            smtp_server=os.getenv('SMTP_SERVER'),
            smtp_port=int(os.getenv('SMTP_PORT')),
            username=os.getenv('SMTP_USERNAME'),
            password=os.getenv('SMTP_PASSWORD'),
            admin_email=os.getenv('ADMIN_EMAIL', 'admin@example.com')
        )
    
    # Server configuration
    server_config = ServerConfig(
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', '8000')),
        debug=os.getenv('DEBUG', 'false').lower() == 'true'
    )
    
    # Database configuration
    database_config = DatabaseConfig(
        path=os.getenv('DATABASE_PATH', 'automation.db'),
        backup_interval_hours=int(os.getenv('DB_BACKUP_INTERVAL', '24'))
    )
    
    # Main configuration
    config = ChatbotConfig(
        groq=groq_config,
        libretranslate=libretranslate_config,
        email=email_config,
        server=server_config,
        database=database_config,
        supported_languages=SUPPORTED_LANGUAGES,
        enable_automation=os.getenv('ENABLE_AUTOMATION', 'true').lower() == 'true',
        enable_analytics=os.getenv('ENABLE_ANALYTICS', 'true').lower() == 'true',
        log_level=os.getenv('LOG_LEVEL', 'INFO')
    )
    
    return config

def get_system_prompt(language: str) -> str:
    """Get system prompt for specified language"""
    return SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS['it'])

def validate_config(config: ChatbotConfig) -> List[str]:
    """Validate configuration and return list of issues"""
    issues = []
    
    if not config.groq.api_key:
        issues.append("Groq API key is required")
    
    if not config.libretranslate.base_url:
        issues.append("LibreTranslate URL is required")
    
    if config.server.port < 1 or config.server.port > 65535:
        issues.append("Server port must be between 1 and 65535")
    
    if config.email and not config.email.admin_email:
        issues.append("Admin email is required when email is configured")
    
    return issues

# Environment variables template for easy setup
ENV_TEMPLATE = """
# Multilingual Chatbot Configuration
# Copy this to .env file and fill in your values

# Required: Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=mixtral-8x7b-32768
GROQ_TEMPERATURE=0.7
GROQ_MAX_TOKENS=1000

# Optional: LibreTranslate Configuration
LIBRETRANSLATE_URL=https://libretranslate.com/translate
LIBRETRANSLATE_API_KEY=your_api_key_if_using_private_instance

# Optional: Email Configuration (for notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
ADMIN_EMAIL=admin@yourdomain.com

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Database Configuration
DATABASE_PATH=automation.db
DB_BACKUP_INTERVAL=24

# Feature Flags
ENABLE_AUTOMATION=true
ENABLE_ANALYTICS=true
LOG_LEVEL=INFO
"""

if __name__ == "__main__":
    # Test configuration loading
    try:
        config = load_config()
        issues = validate_config(config)
        
        if issues:
            print("Configuration issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("Configuration loaded successfully!")
            print(f"Supported languages: {list(config.supported_languages.keys())}")
            print(f"Server will run on {config.server.host}:{config.server.port}")
            
    except Exception as e:
        print(f"Configuration error: {e}")
        print("\nEnvironment variables template:")
        print(ENV_TEMPLATE)