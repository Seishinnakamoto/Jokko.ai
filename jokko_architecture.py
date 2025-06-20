#!/usr/bin/env python3
"""
JOKKO AI - Architettura e Configurazione Sistema
Chatbot AI multilingue per migranti africani in Italia

Autore: MiniMax Agent
Data: 2025-06-20
"""

import os
import json
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path

@dataclass
class JokkoConfig:
    """Configurazione principale sistema JOKKO AI"""
    
    # Lingue supportate
    SUPPORTED_LANGUAGES = {
        'it': 'Italiano',
        'fr': 'Français', 
        'en': 'English',
        'wo': 'Wolof',
        'bm': 'Bambara',
        'ha': 'Hausa',
        'sw': 'Kiswahili',
        'ti': 'ትግርኛ (Tigrinya)',
        'am': 'አማርኛ (Amharic)',
        'snk': 'Soninke',
        'ff': 'Pulaar',
        'ln': 'Lingala'
    }
    
    # Configurazione AI/LLM
    AI_CONFIG = {
        'primary_model': 'mistral',
        'fallback_model': 'ollama',
        'max_tokens': 2048,
        'temperature': 0.3,  # Precisione per contenuti legali
        'context_window': 4096
    }
    
    # Fonti legali italiane
    LEGAL_SOURCES = {
        'gazzetta_ufficiale': 'https://www.gazzettaufficiale.it',
        'normattiva': 'https://www.normattiva.it',
        'interno_gov': 'https://www.interno.gov.it',
        'lavoro_gov': 'https://www.lavoro.gov.it',
        'salute_gov': 'https://www.salute.gov.it'
    }
    
    # Categorie principali di assistenza
    ASSISTANCE_CATEGORIES = {
        'permesso_soggiorno': {
            'it': 'Permesso di Soggiorno',
            'fr': 'Permis de Séjour',
            'en': 'Residence Permit',
            'keywords': ['permesso', 'soggiorno', 'questura', 'rinnovo']
        },
        'sanita': {
            'it': 'Sanità e Salute',
            'fr': 'Santé',
            'en': 'Healthcare',
            'keywords': ['salute', 'medico', 'ospedale', 'tessera sanitaria']
        },
        'lavoro': {
            'it': 'Lavoro e Occupazione',
            'fr': 'Travail et Emploi',
            'en': 'Work and Employment',
            'keywords': ['lavoro', 'contratto', 'centro impiego', 'stipendio']
        },
        'casa': {
            'it': 'Casa e Abitazione',
            'fr': 'Logement',
            'en': 'Housing',
            'keywords': ['casa', 'affitto', 'contratto', 'comune']
        },
        'educazione': {
            'it': 'Educazione e Formazione',
            'fr': 'Éducation et Formation',
            'en': 'Education and Training',
            'keywords': ['scuola', 'università', 'corso', 'formazione']
        }
    }

class JokkoArchitecture:
    """Classe principale per gestire l'architettura JOKKO AI"""
    
    def __init__(self, project_root: str = "/workspace/jokko_ai"):
        self.project_root = Path(project_root)
        self.config = JokkoConfig()
        
    def create_project_structure(self):
        """Crea la struttura completa del progetto"""
        
        structure = {
            'backend': {
                'api': [],
                'ai_engine': [],
                'translation': [], 
                'legal_scraper': [],
                'database': [],
                'config': []
            },
            'frontend': {
                'static': ['css', 'js', 'images'],
                'templates': [],
                'components': []
            },
            'data': {
                'legal_docs': [],
                'embeddings': [],
                'translations': [],
                'logs': []
            },
            'tests': [],
            'docs': [],
            'deploy': []
        }
        
        # Crea tutte le directory
        for folder, subfolders in structure.items():
            folder_path = self.project_root / folder
            folder_path.mkdir(parents=True, exist_ok=True)
            
            if isinstance(subfolders, dict):
                for subfolder, subsubfolders in subfolders.items():
                    subfolder_path = folder_path / subfolder
                    subfolder_path.mkdir(exist_ok=True)
                    
                    if isinstance(subsubfolders, list):
                        for subsubfolder in subsubfolders:
                            (subfolder_path / subsubfolder).mkdir(exist_ok=True)
            elif isinstance(subfolders, list):
                for subfolder in subfolders:
                    (folder_path / subfolder).mkdir(exist_ok=True)
        
        print(f"✅ Struttura progetto creata in: {self.project_root}")
        
    def generate_requirements_txt(self):
        """Genera file requirements.txt con tutte le dipendenze"""
        
        requirements = [
            "# JOKKO AI - Dipendenze Python",
            "# Framework Web",
            "fastapi==0.104.1",
            "uvicorn==0.24.0",
            "jinja2==3.1.2",
            "python-multipart==0.0.6",
            "",
            "# AI e Machine Learning", 
            "langchain==0.1.0",
            "langchain-community==0.0.10",
            "transformers==4.36.0",
            "torch==2.1.0",
            "sentence-transformers==2.2.2",
            "",
            "# Traduzione multilingue",
            "googletrans==3.1.0a0",
            "polyglot==16.7.4",
            "deep-translator==1.11.4",
            "",
            "# Web Scraping e Processing",
            "requests==2.31.0", 
            "beautifulsoup4==4.12.2",
            "selenium==4.15.0",
            "scrapy==2.11.0",
            "",
            "# Database e Storage",
            "sqlite3",  # Built-in
            "chromadb==0.4.18",
            "faiss-cpu==1.7.4",
            "",
            "# Utilities",
            "python-dotenv==1.0.0",
            "pydantic==2.5.0",
            "httpx==0.25.0",
            "pandas==2.1.0",
            "numpy==1.24.0"
        ]
        
        requirements_path = self.project_root / "requirements.txt"
        with open(requirements_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(requirements))
            
        print(f"✅ Requirements creati in: {requirements_path}")
        
    def create_config_files(self):
        """Crea file di configurazione sistema"""
        
        # Config principale
        main_config = {
            "app_name": "JOKKO AI",
            "version": "1.0.0",
            "description": "Chatbot AI multilingue per migranti africani",
            "supported_languages": self.config.SUPPORTED_LANGUAGES,
            "ai_config": self.config.AI_CONFIG,
            "legal_sources": self.config.LEGAL_SOURCES,
            "categories": self.config.ASSISTANCE_CATEGORIES,
            "debug": True,
            "port": 8000,
            "host": "0.0.0.0"
        }
        
        config_path = self.project_root / "backend" / "config" / "main_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(main_config, f, indent=2, ensure_ascii=False)
            
        # Configurazione environment
        env_config = [
            "# JOKKO AI - Configurazione Environment",
            "JOKKO_DEBUG=True",
            "JOKKO_PORT=8000",
            "JOKKO_HOST=0.0.0.0",
            "",
            "# AI Configuration",
            "MISTRAL_API_KEY=your_mistral_key_here",
            "OPENAI_API_KEY=your_openai_key_here", 
            "OLLAMA_BASE_URL=http://localhost:11434",
            "",
            "# Database",
            "DATABASE_URL=sqlite:///./data/jokko.db",
            "VECTOR_DB_PATH=./data/embeddings/",
            "",
            "# External APIs",
            "GOOGLE_TRANSLATE_API_KEY=your_google_translate_key",
            "LEGAL_API_ENDPOINTS=https://www.normattiva.it/api/",
            "",
            "# Security",
            "SECRET_KEY=your_secret_key_here_change_in_production",
            "CORS_ORIGINS=http://localhost:3000,http://localhost:8000"
        ]
        
        env_path = self.project_root / ".env.example"
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(env_config))
            
        print(f"✅ File di configurazione creati")
        
    def create_documentation(self):
        """Crea documentazione base del progetto"""
        
        readme_content = """# 🥁 JOKKO AI - La tua voce, la tua strada

## Descrizione
JOKKO è una chatbot AI multilingue progettata per aiutare i migranti africani in Italia a comprendere i loro diritti, doveri e possibilità legali, con particolare attenzione al permesso di soggiorno e all'accesso ai servizi pubblici.

## 🎯 Obiettivi Principali
- Fornire informazioni legali chiare e aggiornate
- Usare un linguaggio accessibile, tradotto in diverse lingue africane
- Semplificare l'accesso a leggi e regolamenti italiani
- Offrire supporto semplice, mobile e gratuito

## 🌍 Lingue Supportate
- Italiano, Francese, Inglese
- Wolof, Bambara, Hausa, Swahili
- Tigrinya, Amarico, Soninke, Pulaar, Lingala

## 🛠️ Tecnologie
- **Backend**: FastAPI + LangChain + Mistral AI
- **Frontend**: HTML/CSS/JavaScript (mobile-friendly)
- **Traduzione**: Sistema multilingue integrato
- **Fonti Legali**: Scraping automatico normative italiane
- **Database**: SQLite + ChromaDB per embeddings

## 🚀 Installazione e Avvio

```bash
# Clona e configura
cd jokko_ai
pip install -r requirements.txt

# Configura environment
cp .env.example .env
# Modifica .env con le tue API keys

# Avvia il server
python backend/main.py
```

## 📱 Utilizzo
1. Accedi all'interfaccia web
2. Seleziona la tua lingua
3. Fai domande sui tuoi diritti e doveri in Italia
4. Ricevi risposte chiare e fonti ufficiali

## 🧩 Funzionalità
- Chat testuale multilingue
- Accesso a normative aggiornate
- Traduzione automatica
- Interfaccia mobile-friendly
- Risposte contestuali con fonti

## ✊ Impatto Sociale
JOKKO favorisce l'inclusione, l'autonomia e la dignità delle persone migranti, abbattendo barriere linguistiche e burocratiche.

---
*Sviluppato da MiniMax Agent - 2025*
"""

        readme_path = self.project_root / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
            
        print(f"✅ Documentazione creata in: {readme_path}")
        
    def setup_complete_architecture(self):
        """Configura l'architettura completa del progetto"""
        
        print("🏗️ Configurazione architettura JOKKO AI...")
        
        # Crea directory principale
        self.project_root.mkdir(exist_ok=True)
        
        # Setup completo
        self.create_project_structure()
        self.generate_requirements_txt()
        self.create_config_files()
        self.create_documentation()
        
        print(f"""
🎉 ARCHITETTURA JOKKO AI COMPLETATA!

📁 Struttura progetto: {self.project_root}
🔧 Configurazioni: Setup completo
📚 Documentazione: README.md creato
📦 Dipendenze: requirements.txt generato

✨ Pronto per sviluppo backend AI (Step 2)
        """)

if __name__ == "__main__":
    # Inizializza e configura architettura JOKKO AI
    jokko = JokkoArchitecture()
    jokko.setup_complete_architecture()
