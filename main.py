#!/usr/bin/env python3
"""
JOKKO AI - Server Backend Deployabile
Server HTTP per deployment su piattaforme cloud
"""

import json
import random
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Risposte mock complete per tutte le lingue
MOCK_RESPONSES = {
    "it": {
        "permesso_soggiorno": [
            "Per ottenere il permesso di soggiorno in Italia, devi recarti presso la Questura della tua provincia con questi documenti: passaporto, foto, marca da bollo da €16, modulo compilato. Il permesso va richiesto entro 8 giorni dall'ingresso in Italia. 📄✅",
            "Il permesso di soggiorno è obbligatorio per soggiorni superiori a 90 giorni. Puoi richiederlo online sul sito della Polizia di Stato o presso gli uffici postali abilitati. Ricorda di prenotare l'appuntamento in anticipo! 🏛️📅",
            "Esistono diversi tipi di permesso di soggiorno: lavoro, famiglia, studio, asilo. Per il rinnovo, presenta la domanda 60 giorni prima della scadenza. Il costo è di circa 100-200€ tra bolli e spese postali. 💰📋"
        ],
        "sanita": [
            "In Italia hai diritto alle cure sanitarie! 🏥 Per accedere al Servizio Sanitario Nazionale (SSN), devi iscriverti presso l'ASL della tua zona con il permesso di soggiorno e un documento d'identità. Riceverai la tessera sanitaria.",
            "Per emergenze sanitarie chiama il 118 🚑. Per cure non urgenti, contatta il tuo medico di base. Molti ospedali hanno mediatori culturali che parlano diverse lingue africane. La sanità pubblica è gratuita!",
            "Hai diritto a: medico di base gratuito, visite specialistiche con ticket (circa 25€), pronto soccorso gratuito per emergenze, farmaci con ricetta a prezzo ridotto. Per gravidanza e bambini tutto è gratuito! 👶💊"
        ],
        "lavoro": [
            "Per lavorare in Italia hai bisogno di un permesso di soggiorno per lavoro 💼. Puoi cercare lavoro tramite i Centri per l'Impiego, agenzie interinali, o siti web come Indeed e InfoJobs. È importante avere un contratto regolare.",
            "I tuoi diritti lavorativi sono protetti dalla legge italiana ⚖️. Hai diritto a: salario minimo, ferie pagate, contributi previdenziali, sicurezza sul lavoro. Se hai problemi, contatta i sindacati CGIL, CISL o UIL.",
            "Settori che assumono spesso stranieri: agricoltura, ristorazione, edilizia, assistenza anziani, pulizie. Importante: diffida del lavoro in nero! Chiedi sempre contratto regolare e busta paga. 📝✅"
        ],
        "casa": [
            "Per trovare casa in Italia puoi utilizzare siti come Immobiliare.it, Idealista 🏠, o rivolgerti alle agenzie immobiliari. Avrai bisogno di: permesso di soggiorno, codice fiscale, busta paga, e spesso una garanzia bancaria.",
            "⚠️ Attenzione alle truffe immobiliari! Non pagare mai in anticipo senza aver visto la casa e firmato un contratto regolare. Chiedi sempre ricevute per ogni pagamento e diffida di offerte troppo convenienti.",
            "Costi tipici: caparra (1-3 mensilità), prima mensilità, spese agenzia (1 mensilità). Per case popolari contatta il Comune. Esistono anche case di accoglienza per i primi mesi. 🏠💰"
        ],
        "educazione": [
            "In Italia l'istruzione è obbligatoria fino a 16 anni e gratuita nelle scuole pubbliche 🎓. Per iscrivere i tuoi figli, contatta la scuola del tuo quartiere con: permesso di soggiorno, certificato di nascita, e documenti scolastici del paese d'origine.",
            "Per gli adulti ci sono corsi di italiano gratuiti presso i CPIA (Centri Provinciali per l'Istruzione degli Adulti) e associazioni di volontariato 📚. Anche le università offrono corsi per stranieri. L'italiano è fondamentale per l'integrazione!",
            "Opportunità di studio: corsi di italiano (livello A1-C2), formazione professionale, riconoscimento titoli esteri, borse di studio per università. Il livello B1 di italiano è richiesto per il permesso UE! 🎯📖"
        ],
        "generale": [
            "Ciao! 👋 Sono JOKKO, il tuo assistente virtuale per l'Italia. Posso aiutarti con informazioni su permesso di soggiorno, sanità, lavoro, casa e istruzione. Come posso aiutarti oggi?",
            "Benvenuto in Italia! 🇮🇹 Sono qui per aiutarti con tutte le procedure burocratiche e i tuoi diritti. Puoi farmi domande su qualsiasi argomento relativo alla vita in Italia. Non esitare a chiedere!",
            "Ricorda: in Italia hai diritti e doveri. Rispetta le leggi, paga le tasse, integrati nella comunità. L'Italia è un paese accogliente per chi rispetta le regole e contribuisce alla società! 🤝🌟"
        ]
    },
    "en": {
        "permesso_soggiorno": [
            "To obtain a residence permit in Italy, you need to go to the Questura (police headquarters) in your province with these documents: passport, photos, €16 tax stamp, completed form. The permit must be requested within 8 days of entering Italy. 📄✅",
            "Different types of residence permits exist: work, family, study, asylum. For renewal, apply 60 days before expiration. Cost is around €100-200 including stamps and postal fees. 💰📋"
        ],
        "sanita": [
            "In Italy you have the right to healthcare! 🏥 To access the National Health Service (SSN), you must register at the local ASL with your residence permit and ID. You'll receive a health card and public healthcare is free!",
            "For medical emergencies call 118 🚑. For non-urgent care, contact your family doctor. Many hospitals have cultural mediators speaking African languages. Emergency care is always free!"
        ],
        "lavoro": [
            "To work in Italy you need a work residence permit 💼. You can look for jobs through Job Centers, temp agencies, or websites like Indeed and InfoJobs. It's important to have a regular contract with full workers' rights protection.",
            "Your labor rights are protected by Italian law ⚖️. You have the right to: minimum wage, paid holidays, social security contributions, workplace safety. Contact unions CGIL, CISL or UIL if you have problems."
        ],
        "casa": [
            "To find housing in Italy you can use sites like Immobiliare.it, Idealista 🏠, or contact real estate agencies. You'll need: residence permit, tax code, payslip, and often a bank guarantee. Be careful of rental scams!",
            "Typical costs: deposit (1-3 months), first month, agency fees (1 month). For social housing contact the Municipality. Temporary accommodation centers exist for the first months. 🏠💰"
        ],
        "educazione": [
            "In Italy education is compulsory until 16 years old and free in public schools 🎓. To enroll your children, contact your neighborhood school with: residence permit, birth certificate, and school documents from your country of origin.",
            "For adults there are free Italian courses at CPIA (Adult Education Centers) and volunteer associations 📚. Universities also offer courses for foreigners. B1 Italian level is required for EU permit! 🎯📖"
        ],
        "generale": [
            "Hi! 👋 I'm JOKKO, your virtual assistant for Italy. I can help you with information about residence permits, healthcare, work, housing and education. How can I help you today?",
            "Welcome to Italy! 🇮🇹 I'm here to help you with all bureaucratic procedures and your rights. Remember: respect laws, pay taxes, integrate into the community! 🤝🌟"
        ]
    },
    "fr": {
        "permesso_soggiorno": [
            "Pour obtenir un permis de séjour en Italie, vous devez vous rendre à la Questura de votre province avec ces documents: passeport, photos, timbre fiscal de 16€, formulaire rempli. Le permis doit être demandé dans les 8 jours suivant l'entrée en Italie. 📄✅"
        ],
        "sanita": [
            "En Italie, vous avez droit aux soins de santé! 🏥 Pour accéder au Service de Santé National (SSN), vous devez vous inscrire à l'ASL locale avec votre permis de séjour et une pièce d'identité. Les soins d'urgence sont toujours gratuits!"
        ],
        "lavoro": [
            "Pour travailler en Italie, vous avez besoin d'un permis de séjour pour le travail 💼. Vos droits du travail sont protégés par la loi italienne. Méfiez-vous du travail au noir!"
        ],
        "generale": [
            "Salut! 👋 Je suis JOKKO, votre assistant virtuel pour l'Italie. Je peux vous aider avec des informations sur les permis de séjour, la santé, le travail, le logement et l'éducation. Comment puis-je vous aider aujourd'hui?"
        ]
    }
}

def detect_category(message: str) -> str:
    """Rileva la categoria della domanda"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["permesso", "soggiorno", "questura", "documenti", "residence", "permit", "permis"]):
        return "permesso_soggiorno"
    elif any(word in message_lower for word in ["sanità", "medico", "ospedale", "salute", "cure", "health", "medical", "santé"]):
        return "sanita"
    elif any(word in message_lower for word in ["lavoro", "lavorare", "contratto", "stipendio", "work", "job", "travail"]):
        return "lavoro"
    elif any(word in message_lower for word in ["casa", "affitto", "abitazione", "alloggio", "house", "housing", "logement"]):
        return "casa"
    elif any(word in message_lower for word in ["scuola", "studio", "educazione", "università", "corso", "school", "education", "école"]):
        return "educazione"
    else:
        return "generale"

class JokkoHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # Headers CORS
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        if parsed_path.path == '/api/health':
            response = {
                "status": "healthy",
                "version": "1.0.0",
                "components": {
                    "ai_engine": "operational",
                    "translator": "operational", 
                    "legal_processor": "operational"
                },
                "message": "JOKKO AI Backend is running! 🚀"
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif parsed_path.path == '/api/languages':
            response = {
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
            self.wfile.write(json.dumps(response).encode())
        else:
            response = {"error": "Endpoint not found", "available_endpoints": ["/api/health", "/api/languages", "/api/chat", "/api/translate"]}
            self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        # Headers CORS
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/chat':
            try:
                data = json.loads(post_data.decode())
                message = data.get('message', '')
                language = data.get('language', 'it')
                
                # Rileva categoria
                category = detect_category(message)
                
                # Seleziona lingua (fallback all'italiano)
                if language not in MOCK_RESPONSES:
                    language = "it"
                
                # Se la categoria non esiste nella lingua selezionata, usa l'italiano
                if category not in MOCK_RESPONSES[language]:
                    if category in MOCK_RESPONSES["it"]:
                        responses = MOCK_RESPONSES["it"][category]
                        language = "it"  # Cambia lingua per la risposta
                    else:
                        responses = MOCK_RESPONSES["it"]["generale"]
                        category = "generale"
                        language = "it"
                else:
                    responses = MOCK_RESPONSES[language][category]
                
                response_text = random.choice(responses)
                
                # Simula fonti per alcune categorie
                sources = []
                if category != "generale":
                    sources = [
                        {
                            "title": "Portale Immigrazione - Ministero dell'Interno",
                            "url": "https://www.interno.gov.it/it/temi/immigrazione-e-asilo",
                            "content": "Informazioni ufficiali su immigrazione e procedure"
                        },
                        {
                            "title": "Servizio Sanitario Nazionale",
                            "url": "https://www.salute.gov.it/",
                            "content": "Informazioni su sanità e diritti sanitari"
                        }
                    ]
                
                response = {
                    "response": response_text,
                    "language": language,
                    "sources": sources[:1] if sources else [],  # Limitiamo a 1 fonte per non appesantire
                    "category": category,
                    "confidence": round(random.uniform(0.88, 0.98), 2)
                }
                
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                error_response = {
                    "response": "Mi dispiace, ho avuto un problema nel processare la tua richiesta. Puoi riprovare? 🤔",
                    "language": "it",
                    "sources": [],
                    "category": "errore",
                    "confidence": 0.0,
                    "error": str(e)
                }
                self.wfile.write(json.dumps(error_response).encode())
                
        elif parsed_path.path == '/api/translate':
            try:
                data = json.loads(post_data.decode())
                text = data.get('text', '')
                target_language = data.get('target_language', 'it')
                
                # Simulazione di traduzione più realistica
                translations = {
                    "it": "🇮🇹 " + text,
                    "en": "🇬🇧 " + text,
                    "fr": "🇫🇷 " + text
                }
                
                translated_text = translations.get(target_language, f"[{target_language}] {text}")
                
                response = {
                    "translation": translated_text,
                    "target_language": target_language,
                    "confidence": 0.92
                }
                
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                error_response = {"error": f"Errore traduzione: {str(e)}"}
                self.wfile.write(json.dumps(error_response).encode())
        else:
            error_response = {"error": "Endpoint not found"}
            self.wfile.write(json.dumps(error_response).encode())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print("🚀 Avvio JOKKO AI Backend Server...")
    print(f"🌐 Server in ascolto su http://{host}:{port}")
    print("📋 Endpoint disponibili:")
    print("   GET  /api/health")
    print("   GET  /api/languages") 
    print("   POST /api/chat")
    print("   POST /api/translate")
    print("🎯 JOKKO AI ready to help migrants in Italy!")
    
    server = HTTPServer((host, port), JokkoHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⛔ Server fermato dall'utente")
        server.server_close()
