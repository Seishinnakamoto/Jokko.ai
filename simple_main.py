#!/usr/bin/env python3
"""
JOKKO AI - Server Backend Semplificato per Demo
FastAPI server con risposte mock per dimostrare l'integrazione frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
import random

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

# Risposte mock per categoria
MOCK_RESPONSES = {
    "it": {
        "permesso_soggiorno": [
            "Per ottenere il permesso di soggiorno in Italia, devi recarti presso la Questura della tua provincia con questi documenti: passaporto, foto, marca da bollo da €16, modulo compilato. Il permesso va richiesto entro 8 giorni dall'ingresso in Italia.",
            "Il permesso di soggiorno è obbligatorio per soggiorni superiori a 90 giorni. Puoi richiederlo online sul sito della Polizia di Stato o presso gli uffici postali abilitati. Ricorda di prenotare l'appuntamento in anticipo.",
        ],
        "sanita": [
            "In Italia hai diritto alle cure sanitarie. Per accedere al Servizio Sanitario Nazionale (SSN), devi iscriverti presso l'ASL della tua zona con il permesso di soggiorno e un documento d'identità. Riceverai la tessera sanitaria.",
            "Per emergenze sanitarie chiama il 118. Per cure non urgenti, contatta il tuo medico di base. Molti ospedali hanno mediatori culturali che parlano diverse lingue africane.",
        ],
        "lavoro": [
            "Per lavorare in Italia hai bisogno di un permesso di soggiorno per lavoro. Puoi cercare lavoro tramite i Centri per l'Impiego, agenzie interinali, o siti web come Indeed e InfoJobs. È importante avere un contratto regolare.",
            "I tuoi diritti lavorativi sono protetti dalla legge italiana. Hai diritto a: salario minimo, ferie pagate, contributi previdenziali, sicurezza sul lavoro. Se hai problemi, contatta i sindacati.",
        ],
        "casa": [
            "Per trovare casa in Italia puoi utilizzare siti come Immobiliare.it, Idealista, o rivolgerti alle agenzie immobiliari. Avrai bisogno di: permesso di soggiorno, codice fiscale, busta paga, e spesso una garanzia.",
            "Attenzione alle truffe immobiliari! Non pagare mai in anticipo senza aver visto la casa e firmato un contratto regolare. Chiedi sempre ricevute per ogni pagamento.",
        ],
        "educazione": [
            "In Italia l'istruzione è obbligatoria fino a 16 anni e gratuita nelle scuole pubbliche. Per iscrivere i tuoi figli, contatta la scuola del tuo quartiere con: permesso di soggiorno, certificato di nascita, e documenti scolastici del paese d'origine.",
            "Per gli adulti ci sono corsi di italiano gratuiti presso i CPIA (Centri Provinciali per l'Istruzione degli Adulti) e associazioni di volontariato. Anche le università offrono corsi per stranieri.",
        ],
        "generale": [
            "Ciao! Sono JOKKO, il tuo assistente virtuale per l'Italia. Posso aiutarti con informazioni su permesso di soggiorno, sanità, lavoro, casa e istruzione. Come posso aiutarti oggi?",
            "Benvenuto in Italia! Sono qui per aiutarti con tutte le procedure burocratiche e i tuoi diritti. Puoi farmi domande su qualsiasi argomento relativo alla vita in Italia.",
        ]
    },
    "en": {
        "permesso_soggiorno": [
            "To obtain a residence permit in Italy, you need to go to the Questura (police headquarters) in your province with these documents: passport, photos, €16 tax stamp, completed form. The permit must be requested within 8 days of entering Italy.",
        ],
        "sanita": [
            "In Italy you have the right to healthcare. To access the National Health Service (SSN), you must register at the local ASL with your residence permit and ID. You'll receive a health card.",
        ],
        "lavoro": [
            "To work in Italy you need a work residence permit. You can look for jobs through Job Centers, temp agencies, or websites like Indeed and InfoJobs. It's important to have a regular contract.",
        ],
        "casa": [
            "To find housing in Italy you can use sites like Immobiliare.it, Idealista, or contact real estate agencies. You'll need: residence permit, tax code, payslip, and often a guarantee.",
        ],
        "educazione": [
            "In Italy education is compulsory until 16 years old and free in public schools. To enroll your children, contact your neighborhood school with: residence permit, birth certificate, and school documents from your country of origin.",
        ],
        "generale": [
            "Hi! I'm JOKKO, your virtual assistant for Italy. I can help you with information about residence permits, healthcare, work, housing and education. How can I help you today?",
        ]
    },
    "fr": {
        "generale": [
            "Salut! Je suis JOKKO, votre assistant virtuel pour l'Italie. Je peux vous aider avec des informations sur les permis de séjour, la santé, le travail, le logement et l'éducation.",
        ]
    }
}

app = FastAPI(
    title="JOKKO AI",
    description="Chatbot AI multilingue per migranti africani in Italia",
    version="1.0.0"
)

# Configura CORS per permettere l'accesso dal frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In produzione limitare agli origins specifici
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    """Health check sistema"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "components": {
            "ai_engine": "operational",
            "translator": "mock", 
            "legal_processor": "mock"
        }
    }

@app.get("/api/languages")
async def get_supported_languages():
    """Ottieni lingue supportate"""
    return {
        "languages": {
            "it": "Italiano",
            "fr": "Français", 
            "en": "English",
            "wo": "Wolof",
            "bm": "Bambara",
            "ha": "Hausa",
            "sw": "Swahili",
            "ti": "Tigrinya",
            "am": "Amarico",
            "snk": "Soninke",
            "ff": "Pulaar",
            "ln": "Lingala"
        }
    }

def detect_category(message: str) -> str:
    """Rileva la categoria della domanda"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["permesso", "soggiorno", "questura", "documenti"]):
        return "permesso_soggiorno"
    elif any(word in message_lower for word in ["sanità", "medico", "ospedale", "salute", "cure"]):
        return "sanita"
    elif any(word in message_lower for word in ["lavoro", "lavorare", "contratto", "stipendio"]):
        return "lavoro"
    elif any(word in message_lower for word in ["casa", "affitto", "abitazione", "alloggio"]):
        return "casa"
    elif any(word in message_lower for word in ["scuola", "studio", "educazione", "università", "corso"]):
        return "educazione"
    else:
        return "generale"

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest):
    """Endpoint principale per chat AI"""
    try:
        # Rileva categoria
        category = detect_category(chat_request.message)
        
        # Seleziona lingua (fallback all'italiano)
        language = chat_request.language if chat_request.language in MOCK_RESPONSES else "it"
        
        # Seleziona risposta appropriata
        responses = MOCK_RESPONSES[language].get(category, MOCK_RESPONSES["it"]["generale"])
        response_text = random.choice(responses)
        
        # Simula fonti per alcune categorie
        sources = []
        if category != "generale":
            sources = [
                {
                    "title": "Portale Immigrazione - Ministero dell'Interno",
                    "url": "https://www.interno.gov.it/it/temi/immigrazione-e-asilo",
                    "content": "Informazioni ufficiali su immigrazione e procedure"
                }
            ]
        
        return ChatResponse(
            response=response_text,
            language=language,
            sources=sources,
            category=category,
            confidence=0.95
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel processing: {str(e)}")

@app.post("/api/translate")
async def translate_text(text: str, target_language: str, source_language: str = "auto"):
    """Endpoint per traduzione testi (mock)"""
    # Simulazione semplice di traduzione
    return {
        "translation": f"[Tradotto in {target_language}] {text}",
        "target_language": target_language
    }

if __name__ == "__main__":
    print("🚀 Avvio JOKKO AI Backend (versione semplificata)...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
