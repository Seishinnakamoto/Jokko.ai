#!/usr/bin/env python3
"""
Setup script for Multilingual Chatbot System
Handles installation, configuration, and initial setup
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print setup banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                  🤖 MULTILINGUAL CHATBOT SETUP               ║
    ║                                                              ║
    ║  Configurazione automatica del sistema chatbot multilingue  ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check Python version compatibility"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ è richiesto")
        print(f"   Versione attuale: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} compatibile")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installazione dipendenze...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dipendenze installate con successo")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore installazione dipendenze: {e}")
        return False

def create_env_file():
    """Create .env file with configuration template"""
    env_path = Path('.env')
    
    if env_path.exists():
        response = input("\n⚠️  File .env già esistente. Sovrascrivere? (y/N): ")
        if response.lower() != 'y':
            print("✅ Configurazione esistente mantenuta")
            return True
    
    print("\n📝 Creazione file di configurazione...")
    
    # Get Groq API key
    groq_api_key = input("🔑 Inserisci la tua Groq API key (obbligatoria): ").strip()
    if not groq_api_key:
        print("❌ Groq API key è obbligatoria")
        return False
    
    # Optional configurations
    print("\n📧 Configurazione email (opzionale - premi Enter per saltare):")
    smtp_server = input("   SMTP Server (es. smtp.gmail.com): ").strip()
    smtp_port = input("   SMTP Port (es. 587): ").strip()
    smtp_username = input("   SMTP Username: ").strip()
    smtp_password = input("   SMTP Password: ").strip()
    admin_email = input("   Admin Email: ").strip()
    
    print("\n🌐 Configurazione server (opzionale):")
    port = input("   Porta server (default: 8000): ").strip() or "8000"
    
    # Create .env content
    env_content = f"""# Multilingual Chatbot Configuration
# Generato automaticamente da setup.py

# OBBLIGATORIO: Groq API
GROQ_API_KEY={groq_api_key}
GROQ_MODEL=mixtral-8x7b-32768
GROQ_TEMPERATURE=0.7
GROQ_MAX_TOKENS=1000

# LibreTranslate
LIBRETRANSLATE_URL=https://libretranslate.com/translate

# Server Configuration
HOST=0.0.0.0
PORT={port}
DEBUG=false

# Database
DATABASE_PATH=automation.db
DB_BACKUP_INTERVAL=24

# Features
ENABLE_AUTOMATION=true
ENABLE_ANALYTICS=true
LOG_LEVEL=INFO
"""
    
    # Add email configuration if provided
    if all([smtp_server, smtp_port, smtp_username, smtp_password]):
        env_content += f"""
# Email Configuration
SMTP_SERVER={smtp_server}
SMTP_PORT={smtp_port}
SMTP_USERNAME={smtp_username}
SMTP_PASSWORD={smtp_password}
ADMIN_EMAIL={admin_email or smtp_username}
"""
    
    # Write .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ File .env creato con successo")
        return True
    except Exception as e:
        print(f"❌ Errore creazione .env: {e}")
        return False

def test_configuration():
    """Test the configuration"""
    print("\n🧪 Test configurazione...")
    
    try:
        # Load environment variables from .env
        if Path('.env').exists():
            with open('.env', 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
        
        # Test configuration loading
        from config import load_config, validate_config
        
        config = load_config()
        issues = validate_config(config)
        
        if issues:
            print("❌ Problemi di configurazione trovati:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ Configurazione valida")
            print(f"   Lingue supportate: {len(config.supported_languages)}")
            print(f"   Server: {config.server.host}:{config.server.port}")
            return True
            
    except Exception as e:
        print(f"❌ Errore test configurazione: {e}")
        return False

def create_startup_scripts():
    """Create startup scripts for different platforms"""
    print("\n📜 Creazione script di avvio...")
    
    # Windows batch script
    windows_script = """@echo off
echo Starting Multilingual Chatbot...
python main_app.py
pause
"""
    
    # Unix shell script
    unix_script = """#!/bin/bash
echo "Starting Multilingual Chatbot..."
python3 main_app.py
"""
    
    try:
        # Create Windows script
        with open('start_chatbot.bat', 'w') as f:
            f.write(windows_script)
        
        # Create Unix script
        with open('start_chatbot.sh', 'w') as f:
            f.write(unix_script)
        
        # Make Unix script executable
        os.chmod('start_chatbot.sh', 0o755)
        
        print("✅ Script di avvio creati:")
        print("   - start_chatbot.bat (Windows)")
        print("   - start_chatbot.sh (Linux/Mac)")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore creazione script: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("""
    🎉 SETUP COMPLETATO CON SUCCESSO!
    
    📋 Prossimi passi:
    
    1. 🚀 Avvia il chatbot:
       python main_app.py
       
       Oppure usa gli script:
       - Windows: start_chatbot.bat
       - Linux/Mac: ./start_chatbot.sh
    
    2. 🌐 Apri il browser su:
       http://localhost:8000
    
    3. 🔗 Per integrare con Glide App:
       - Webhook URL: http://your-domain.com/webhook/chat
       - API URL: http://your-domain.com/api/chat
    
    4. 📊 Endpoints disponibili:
       - GET  /api/health       - Controllo stato
       - GET  /api/languages    - Lingue supportate
       - POST /api/chat         - Chat API
       - GET  /api/analytics    - Statistiche
    
    5. 📚 Documentazione completa:
       README_MULTILINGUAL_CHATBOT.md
    
    🆘 Supporto:
       - Controlla i log per eventuali errori
       - Verifica le variabili d'ambiente in .env
       - Consulta la documentazione per troubleshooting
    """)

def main():
    """Main setup function"""
    print_banner()
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup fallito durante l'installazione delle dipendenze")
        sys.exit(1)
    
    # Create configuration
    if not create_env_file():
        print("\n❌ Setup fallito durante la configurazione")
        sys.exit(1)
    
    # Test configuration
    if not test_configuration():
        print("\n❌ Setup fallito durante il test della configurazione")
        sys.exit(1)
    
    # Create startup scripts
    create_startup_scripts()
    
    # Print success message
    print_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrotto dall'utente")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Errore durante il setup: {e}")
        sys.exit(1)