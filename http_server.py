#!/usr/bin/env python3
"""
JOKKO AI - Server HTTP Semplice per Demo
Server HTTP con librerie standard Python
"""

import json
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import ssl

# Risposte mock
MOCK_RESPONSES = {
    "it": {
        "permesso_soggiorno": [
            "Per ottenere il permesso di soggiorno in Italia, devi recarti presso la Questura della tua provincia con questi documenti: passaporto, foto, marca da bollo da €16, modulo compilato. Il permesso va richiesto entro 8 giorni dall'ingresso in Italia. 📄✅",
            "Il permesso di soggiorno è obbligatorio per soggiorni superiori a 90 giorni. Puoi richiederlo online sul sito della Polizia di Stato o presso gli uffici postali abilitati. Ricorda di prenotare l'appuntamento in anticipo! 🏛️📅",
        ],
        "sanita": [
            "In Italia hai diritto alle cure sanitarie! 🏥 Per accedere al Servizio Sanitario Nazionale (SSN), devi iscriverti presso l'ASL della tua zona con il permesso di soggiorno e un documento d'identità. Riceverai la tessera sanitaria.",
            "Per emergenze sanitarie chiama il 118 🚑. Per cure non urgenti, contatta il tuo medico di base. Molti ospedali hanno mediatori culturali che parlano diverse lingue africane. La sanità pubblica è gratuita!",
        ],
        "lavoro": [
            "Per lavorare in Italia hai bisogno di un permesso di soggiorno per lavoro 💼. Puoi cercare lavoro tramite i Centri per l'Impiego, agenzie interinali, o siti web come Indeed e InfoJobs. È importante avere un contratto regolare.",
            "I tuoi diritti lavorativi sono protetti dalla legge italiana ⚖️. Hai diritto a: salario minimo, ferie pagate, contributi previdenziali, sicurezza sul lavoro. Se hai problemi, contatta i sindacati CGIL, CISL o UIL.",
        ],
        "casa": [
            "Per trovare casa in Italia puoi utilizzare siti come Immobiliare.it, Idealista 🏠, o rivolgerti alle agenzie immobiliari. Avrai bisogno di: permesso di soggiorno, codice fiscale, busta paga, e spesso una garanzia bancaria.",
            "⚠️ Attenzione alle truffe immobiliari! Non pagare mai in anticipo senza aver visto la casa e firmato un contratto regolare. Chiedi sempre ricevute per ogni pagamento e diffida di offerte troppo convenienti.",
        ],
        "educazione": [
            "In Italia l'istruzione è obbligatoria fino a 16 anni e gratuita nelle scuole pubbliche 🎓. Per iscrivere i tuoi figli, contatta la scuola del tuo quartiere con: permesso di soggiorno, certificato di nascita, e documenti scolastici del paese d'origine.",
            "Per gli adulti ci sono corsi di italiano gratuiti presso i CPIA (Centri Provinciali per l'Istruzione degli Adulti) e associazioni di volontariato 📚. Anche le università offrono corsi per stranieri. L'italiano è fondamentale per l'integrazione!",
        ],
        "generale": [
            "Ciao! 👋 Sono JOKKO, il tuo assistente virtuale per l'Italia. Posso aiutarti con informazioni su permesso di soggiorno, sanità, lavoro, casa e istruzione. Come posso aiutarti oggi?",
            "Benvenuto in Italia! 🇮🇹 Sono qui per aiutarti con tutte le procedure burocratiche e i tuoi diritti. Puoi farmi domande su qualsiasi argomento relativo alla vita in Italia. Non esitare a chiedere!",
        ]
    },
    "en": {
        "permesso_soggiorno": [
            "To obtain a residence permit in Italy, you need to go to the Questura (police headquarters) in your province with these documents: passport, photos, €16 tax stamp, completed form. The permit must be requested within 8 days of entering Italy. 📄✅",
        ],
        "sanita": [
            "In Italy you have the right to healthcare! 🏥 To access the National Health Service (SSN), you must register at the local ASL with your residence permit and ID. You'll receive a health card and public healthcare is free!",
        ],
        "lavoro": [
            "To work in Italy you need a work residence permit 💼. You can look for jobs through Job Centers, temp agencies, or websites like Indeed and InfoJobs. It's important to have a regular contract with full workers' rights protection.",
        ],
        "casa": [
            "To find housing in Italy you can use sites like Immobiliare.it, Idealista 🏠, or contact real estate agencies. You'll need: residence permit, tax code, payslip, and often a bank guarantee. Be careful of rental scams!",
        ],
        "educazione": [
            "In Italy education is compulsory until 16 years old and free in public schools 🎓. To enroll your children, contact your neighborhood school with: residence permit, birth certificate, and school documents from your country of origin.",
        ],
        "generale": [
            "Hi! 👋 I'm JOKKO, your virtual assistant for Italy. I can help you with information about residence permits, healthcare, work, housing and education. How can I help you today?",
        ]
    },
    "fr": {
        "generale": [
            "Salut! 👋 Je suis JOKKO, votre assistant virtuel pour l'Italie. Je peux vous aider avec des informations sur les permis de séjour, la santé, le travail, le logement et l'éducation. Comment puis-je vous aider aujourd'hui?",
        ],
        "permesso_soggiorno": [
            "Pour obtenir un permis de séjour en Italie, vous devez vous rendre à la Questura de votre province avec ces documents: passeport, photos, timbre fiscal de 16€, formulaire rempli. Le permis doit être demandé dans les 8 jours suivant l'entrée en Italie. 📄✅",
        ]
    }
}

def detect_category(message: str) -> str:
    """Rileva la categoria della domanda"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["permesso", "soggiorno", "questura", "documenti", "residence", "permit"]):
        return "permesso_soggiorno"
    elif any(word in message_lower for word in ["sanità", "medico", "ospedale", "salute", "cure", "health", "medical"]):
        return "sanita"
    elif any(word in message_lower for word in ["lavoro", "lavorare", "contratto", "stipendio", "work", "job"]):
        return "lavoro"
    elif any(word in message_lower for word in ["casa", "affitto", "abitazione", "alloggio", "house", "housing"]):
        return "casa"
    elif any(word in message_lower for word in ["scuola", "studio", "educazione", "università", "corso", "school", "education"]):
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
                    "translator": "mock", 
                    "legal_processor": "mock"
                }
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
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

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
                
                response = {
                    "response": response_text,
                    "language": language,
                    "sources": sources,
                    "category": category,
                    "confidence": 0.95
                }
                
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                error_response = {"error": f"Errore nel processing: {str(e)}"}
                self.wfile.write(json.dumps(error_response).encode())
                
        elif parsed_path.path == '/api/translate':
            try:
                data = json.loads(post_data.decode())
                text = data.get('text', '')
                target_language = data.get('target_language', 'it')
                
                response = {
                    "translation": f"[Tradotto in {target_language}] {text}",
                    "target_language": target_language
                }
                
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                error_response = {"error": f"Errore traduzione: {str(e)}"}
                self.wfile.write(json.dumps(error_response).encode())
        else:
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

if __name__ == '__main__':
    print("🚀 Avvio JOKKO AI Backend HTTP Server...")
    print("🌐 Server in ascolto su http://localhost:8000")
    print("📋 Endpoint disponibili:")
    print("   GET  /api/health")
    print("   GET  /api/languages") 
    print("   POST /api/chat")
    print("   POST /api/translate")
    
    server = HTTPServer(('0.0.0.0', 8000), JokkoHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⛔ Server fermato dall'utente")
        server.server_close()
