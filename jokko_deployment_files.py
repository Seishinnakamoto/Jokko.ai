# ==============================================
# FILE 1: app.py
# Salva come "app.py" nella root del progetto
# ==============================================

#!/usr/bin/env python3
"""
JOKKO AI - Versione semplificata per Vercel
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import json

# Modelli di risposta
class ChatRequest(BaseModel):
    message: str
    language: str = "it"
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    language: str
    sources: List[Dict] = []
    category: Optional[str] = None
    confidence: float = 0.0

# Configurazione lingue supportate
SUPPORTED_LANGUAGES = {
    "it": "Italiano", 
    "fr": "Français", 
    "en": "English",
    "wo": "Wolof", 
    "bm": "Bambara", 
    "ha": "Hausa",
    "am": "Amarico",
    "ti": "Tigrinya",
    "lg": "Lingala",
    "ff": "Pulaar",
    "so": "Soninke"
}

# Risposte di esempio per testing
SAMPLE_RESPONSES = {
    "it": {
        "permesso_soggiorno": "Per il permesso di soggiorno devi recarti in Questura con questi documenti: passaporto, foto tessera, marca da bollo da €16. Prenota appuntamento online sul sito della Polizia di Stato. Il processo può richiedere 2-6 mesi.",
        "lavoro": "Per cercare lavoro in Italia puoi: 1) Registrarti ai centri per l'impiego, 2) Usare siti come InfoJobs, Indeed, Monster, 3) Contattare agenzie interinali, 4) Networking attraverso comunità locali.",
        "casa": "Per trovare casa puoi: 1) Usare siti come Immobiliare.it, Subito.it, Idealista, 2) Contattare associazioni locali per migranti, 3) Cercare annunci nelle bacheche universitarie, 4) Chiedere supporto ai servizi sociali.",
        "sanita": "Il Servizio Sanitario Nazionale italiano garantisce cure gratuite. Devi: 1) Richiedere la tessera sanitaria in ASL, 2) Scegliere un medico di base, 3) Per emergenze vai al Pronto Soccorso, 4) Farmaci con ricetta sono gratuiti o scontati.",
        "diritti": "I tuoi diritti in Italia includono: assistenza legale gratuita, protezione dalla discriminazione, accesso all'istruzione, diritto al lavoro regolare, assistenza sanitaria. Contatta associazioni come ASGI, ARCI per supporto legale.",
        "default": "Ciao! Sono JOKKO AI, il tuo assistente per vivere meglio in Italia. Posso aiutarti con: permesso di soggiorno, lavoro, casa, sanità e diritti. Dimmi cosa ti serve!"
    },
    "en": {
        "permesso_soggiorno": "For residence permit go to Questura with: passport, ID photos, €16 tax stamp. Book appointment online on Police website. Process takes 2-6 months.",
        "lavoro": "To find work in Italy: 1) Register at employment centers, 2) Use sites like InfoJobs, Indeed, Monster, 3) Contact temp agencies, 4) Network through local communities.",
        "casa": "To find housing: 1) Use sites like Immobiliare.it, Subito.it, Idealista, 2) Contact local migrant associations, 3) Check university bulletin boards, 4) Ask social services for support.",
        "sanita": "Italian National Health Service provides free healthcare. You need to: 1) Request health card at ASL, 2) Choose family doctor, 3) For emergencies go to ER, 4) Prescription drugs are free or discounted.",
        "diritti": "Your rights in Italy include: free legal aid, protection from discrimination, access to education, right to regular work, healthcare assistance. Contact organizations like ASGI, ARCI for legal support.",
        "default": "Hello! I'm JOKKO AI, your assistant for living better in Italy. I can help with: residence permits, work, housing, healthcare and rights. What do you need?"
    },
    "fr": {
        "permesso_soggiorno": "Pour le titre de séjour allez à la Questura avec: passeport, photos d'identité, timbre fiscal de 16€. Réservez rendez-vous en ligne sur site Police. Processus prend 2-6 mois.",
        "lavoro": "Pour trouver du travail en Italie: 1) Inscrivez-vous aux centres pour l'emploi, 2) Utilisez sites comme InfoJobs, Indeed, Monster, 3) Contactez agences intérim, 4) Réseautage via communautés locales.",
        "casa": "Pour trouver logement: 1) Utilisez sites comme Immobiliare.it, Subito.it, Idealista, 2) Contactez associations locales migrants, 3) Vérifiez tableaux université, 4) Demandez aide services sociaux.",
        "sanita": "Service Sanitaire National italien garantit soins gratuits. Vous devez: 1) Demander carte sanitaire à ASL, 2) Choisir médecin famille, 3) Pour urgences allez aux urgences, 4) Médicaments prescription gratuits ou réduits.",
        "diritti": "Vos droits en Italie incluent: aide juridique gratuite, protection discrimination, accès éducation, droit travail régulier, assistance santé. Contactez organisations comme ASGI, ARCI pour soutien juridique.",
        "default": "Salut! Je suis JOKKO AI, votre assistant pour mieux vivre en Italie. Je peux aider avec: titres séjour, travail, logement, santé et droits. Que vous faut-il?"
    }
}

# Crea app FastAPI
app = FastAPI(
    title="JOKKO AI",
    description="Chatbot AI multilingue per migranti africani in Italia",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def homepage():
    """Homepage API"""
    return {
        "message": "JOKKO AI - La tua voce, la tua strada",
        "description": "Informazioni chiare per vivere meglio in Italia",
        "tagline": "Questa chatbot aiuta i migranti africani in Italia a ottenere informazioni su:",
        "services": [
            "Permesso di soggiorno",
            "Lavoro", 
            "Casa",
            "Sanità",
            "Diritti e leggi italiane"
        ],
        "supported_languages": SUPPORTED_LANGUAGES,
        "endpoints": {
            "chat": "/api/chat - Invia messaggio alla chatbot",
            "languages": "/api/languages - Lista lingue supportate", 
            "health": "/api/health - Status sistema"
        },
        "usage_example": {
            "endpoint": "/api/chat",
            "method": "POST",
            "body": {
                "message": "Come posso ottenere il permesso di soggiorno?",
                "language": "it"
            }
        }
    }

@app.get("/api/languages")
async def get_supported_languages():
    """Ottieni lingue supportate"""
    return {"languages": SUPPORTED_LANGUAGES}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest):
    """Endpoint principale per chat AI"""
    try:
        message = chat_request.message.lower()
        language = chat_request.language
        
        # Logica semplificata per demo
        response_lang = SAMPLE_RESPONSES.get(language, SAMPLE_RESPONSES["it"])
        
        # Keyword matching per categorie
        if any(word in message for word in ["permesso", "soggiorno", "permit", "séjour"]):
            response_text = response_lang.get("permesso_soggiorno", response_lang["default"])
            category = "permesso_soggiorno"
            confidence = 0.9
        elif any(word in message for word in ["lavoro", "work", "travail", "job", "emploi"]):
            response_text = response_lang.get("lavoro", response_lang["default"])
            category = "lavoro"
            confidence = 0.85
        elif any(word in message for word in ["casa", "house", "logement", "affitto", "rent"]):
            response_text = response_lang.get("casa", response_lang["default"])
            category = "casa"
            confidence = 0.85
        elif any(word in message for word in ["salute", "health", "santé", "medico", "doctor", "ospedale"]):
            response_text = response_lang.get("sanita", response_lang["default"])
            category = "sanita" 
            confidence = 0.85
        elif any(word in message for word in ["diritti", "rights", "droits", "legale", "legal"]):
            response_text = response_lang.get("diritti", response_lang["default"])
            category = "diritti"
            confidence = 0.85
        else:
            response_text = response_lang["default"] 
            category = "generale"
            confidence = 0.7
        
        return ChatResponse(
            response=response_text,
            language=language,
            sources=[
                {"title": "JOKKO Knowledge Base", "url": "https://ym.vercel.app"},
                {"title": "Ministero dell'Interno", "url": "https://www.interno.gov.it"}
            ],
            category=category,
            confidence=confidence
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel processing: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check sistema"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "message": "JOKKO AI is running successfully on Vercel!",
        "components": {
            "api": "operational",
            "chat": "operational",
            "multilingual": "operational"
        },
        "supported_languages": len(SUPPORTED_LANGUAGES),
        "uptime": "100%"
    }

# ==============================================
# FILE 2: vercel.json  
# Salva come "vercel.json" nella root del progetto
# ==============================================

{
  "version": 2,
  "functions": {
    "app.py": {
      "runtime": "python3.9"
    }
  },
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}

# ==============================================
# FILE 3: requirements.txt
# Salva come "requirements.txt" nella root del progetto  
# ==============================================

fastapi==0.104.1
pydantic==2.5.0
uvicorn[standard]==0.24.0

# ==============================================
# FILE 4: .gitignore
# Salva come ".gitignore" nella root del progetto
# ==============================================

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Vercel
.vercel

# ==============================================
# ISTRUZIONI PER L'USO:
# ==============================================

# 1. Copia il contenuto di ogni sezione nei rispettivi file
# 2. Struttura finale del progetto:
#    jokko/
#    ├── app.py
#    ├── vercel.json  
#    ├── requirements.txt
#    ├── .gitignore
#    └── (altri file esistenti)
#
# 3. Esegui questi comandi:
#    git add .
#    git commit -m "Fix: Simplified JOKKO for Vercel deployment"
#    git push origin main
#
# 4. Vercel ribuilderà automaticamente
# 5. Testa l'applicazione agli endpoint:
#    - https://ym.vercel.app/
#    - https://ym.vercel.app/api/health
#    - https://ym.vercel.app/api/chat (POST con JSON body)