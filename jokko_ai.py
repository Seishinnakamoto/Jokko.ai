#!/usr/bin/env python3
"""
JOKKO AI - Engine AI Principale
Gestisce logica chatbot, classificazione domande e generazione risposte

Autore: MiniMax Agent
Data: 2025-06-20
"""

import json
import asyncio
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JokkoAI:
    """Engine AI principale per JOKKO chatbot"""
    
    def __init__(self):
        self.load_knowledge_base()
        self.setup_response_patterns()
        self.conversation_history = {}
        
    def load_knowledge_base(self):
        """Carica base di conoscenza legale italiana"""
        self.knowledge_base = {
            "permesso_soggiorno": {
                "keywords": ["permesso", "soggiorno", "questura", "rinnovo", "scadenza"],
                "info": {
                    "it": "Il permesso di soggiorno è obbligatorio per tutti i cittadini non UE. Deve essere richiesto entro 8 giorni dall'ingresso in Italia presso la Questura competente.",
                    "fr": "Le permis de séjour est obligatoire pour tous les citoyens non-UE. Il doit être demandé dans les 8 jours suivant l'entrée en Italie auprès de la Questure compétente.",
                    "en": "The residence permit is mandatory for all non-EU citizens. It must be requested within 8 days of entry into Italy at the competent Police Headquarters."
                },
                "documenti": [
                    "Passaporto con visto",
                    "Modulo richiesta compilato",
                    "Foto tessera",
                    "Marca da bollo €16",
                    "Ricevuta pagamento €30.46"
                ],
                "link_ufficiali": [
                    "https://www.interno.gov.it/it/temi/immigrazione-e-asilo/modalita-dingresso-e-soggiorno-italia/permesso-soggiorno"
                ]
            },
            
            "sanita": {
                "keywords": ["salute", "medico", "ospedale", "tessera sanitaria", "cure"],
                "info": {
                    "it": "Tutti i cittadini stranieri regolarmente soggiornanti hanno diritto all'assistenza sanitaria. È necessario iscriversi al SSN.",
                    "fr": "Tous les citoyens étrangers en séjour régulier ont droit aux soins de santé. Il faut s'inscrire au SSN.",
                    "en": "All foreign citizens with regular residence have the right to healthcare. Registration with the SSN is required."
                },
                "documenti": [
                    "Permesso di soggiorno",
                    "Codice fiscale", 
                    "Documento identità",
                    "Certificato residenza"
                ],
                "link_ufficiali": [
                    "https://www.salute.gov.it/portale/temi/p2_6.jsp?lingua=italiano&id=1122"
                ]
            },
            
            "lavoro": {
                "keywords": ["lavoro", "contratto", "centro impiego", "stipendio", "diritti"],
                "info": {
                    "it": "I cittadini stranieri con permesso di soggiorno per lavoro hanno gli stessi diritti dei lavoratori italiani.",
                    "fr": "Les citoyens étrangers avec permis de séjour pour travail ont les mêmes droits que les travailleurs italiens.",
                    "en": "Foreign citizens with work residence permits have the same rights as Italian workers."
                },
                "documenti": [
                    "Permesso soggiorno per lavoro",
                    "Contratto di lavoro",
                    "Codice fiscale"
                ],
                "link_ufficiali": [
                    "https://www.lavoro.gov.it/temi-e-priorita/immigrazione/Pagine/default.aspx"
                ]
            },
            
            "casa": {
                "keywords": ["casa", "affitto", "contratto", "comune", "residenza"],
                "info": {
                    "it": "Per affittare una casa è necessario un contratto regolare e la registrazione della residenza al comune.",
                    "fr": "Pour louer une maison, il faut un contrat régulier et l'enregistrement de la résidence à la commune.",
                    "en": "To rent a house, a regular contract and registration of residence with the municipality are required."
                },
                "documenti": [
                    "Permesso di soggiorno",
                    "Codice fiscale",
                    "Buste paga",
                    "Garanzie economiche"
                ],
                "link_ufficiali": [
                    "https://www.interno.gov.it/it/temi/territorio-e-immigrazione"
                ]
            },
            
            "educazione": {
                "keywords": ["scuola", "università", "corso", "formazione", "studio"],
                "info": {
                    "it": "L'istruzione pubblica è gratuita e obbligatoria fino a 16 anni per tutti i minori presenti sul territorio italiano.",
                    "fr": "L'instruction publique est gratuite et obligatoire jusqu'à 16 ans pour tous les mineurs présents sur le territoire italien.",
                    "en": "Public education is free and compulsory until age 16 for all minors present on Italian territory."
                },
                "documenti": [
                    "Documenti scolastici del paese di origine",
                    "Traduzione giurata",
                    "Permesso di soggiorno (per maggiorenni)"
                ],
                "link_ufficiali": [
                    "https://www.miur.gov.it/web/guest/immigrazione"
                ]
            }
        }
        
    def setup_response_patterns(self):
        """Configura pattern di risposta personalizzati"""
        self.greeting_patterns = {
            "it": ["ciao", "salve", "buongiorno", "buonasera", "aiuto"],
            "fr": ["bonjour", "salut", "bonsoir", "aide"],
            "en": ["hello", "hi", "good morning", "help"],
            "wo": ["salaam", "nanga def"],
            "bm": ["i ni ce", "i ni sogoma"],
            "ha": ["sannu", "barka"],
            "sw": ["hujambo", "habari"]
        }
        
        self.emergency_keywords = {
            "it": ["emergenza", "urgente", "pronto soccorso", "polizia"],
            "fr": ["urgence", "urgent", "police", "secours"],
            "en": ["emergency", "urgent", "police", "help"]
        }
        
    def classify_query_category(self, message: str) -> Tuple[str, float]:
        """Classifica la categoria della domanda"""
        message_lower = message.lower()
        
        # Cerca category match
        best_category = "generale"
        best_score = 0.0
        
        for category, data in self.knowledge_base.items():
            keywords = data["keywords"]
            score = 0
            
            for keyword in keywords:
                if keyword in message_lower:
                    score += 1
                    
            # Calcola confidence score
            if len(keywords) > 0:
                confidence = score / len(keywords)
                if confidence > best_score:
                    best_category = category
                    best_score = confidence
                    
        return best_category, best_score
        
    def detect_language(self, message: str) -> str:
        """Rileva lingua del messaggio (semplificata)"""
        # Implementazione base - in produzione usare libreria specializzata
        italian_indicators = ["è", "perché", "così", "però", "già", "più"]
        french_indicators = ["est", "être", "avec", "pour", "que", "où"]
        english_indicators = ["the", "and", "for", "with", "this", "that"]
        
        message_lower = message.lower()
        
        scores = {
            "it": sum(1 for word in italian_indicators if word in message_lower),
            "fr": sum(1 for word in french_indicators if word in message_lower),
            "en": sum(1 for word in english_indicators if word in message_lower)
        }
        
        detected_lang = max(scores, key=scores.get)
        return detected_lang if scores[detected_lang] > 0 else "it"
        
    def is_greeting(self, message: str, language: str) -> bool:
        """Verifica se il messaggio è un saluto"""
        message_lower = message.lower()
        patterns = self.greeting_patterns.get(language, self.greeting_patterns["it"])
        
        return any(pattern in message_lower for pattern in patterns)
        
    def is_emergency(self, message: str, language: str) -> bool:
        """Verifica se il messaggio indica un'emergenza"""
        message_lower = message.lower()
        keywords = self.emergency_keywords.get(language, self.emergency_keywords["it"])
        
        return any(keyword in message_lower for keyword in keywords)
        
    def generate_greeting_response(self, language: str) -> Dict:
        """Genera risposta di saluto personalizzata"""
        greetings = {
            "it": """Ciao! Sono JOKKO AI 🥁, il tuo assistente personale per navigare la vita in Italia.
            
Sono qui per aiutarti con:
• 📋 Permesso di soggiorno e documenti
• 🏥 Sanità e assistenza medica  
• 💼 Lavoro e diritti lavorativi
• 🏠 Casa e residenza
• 📚 Educazione e formazione

Scrivi la tua domanda nella lingua che preferisci. Come posso aiutarti oggi?""",

            "fr": """Salut! Je suis JOKKO AI 🥁, votre assistant personnel pour naviguer la vie en Italie.

Je suis là pour vous aider avec:
• 📋 Permis de séjour et documents
• 🏥 Santé et assistance médicale
• 💼 Travail et droits du travail
• 🏠 Logement et résidence
• 📚 Éducation et formation

Écrivez votre question dans la langue que vous préférez. Comment puis-je vous aider aujourd'hui?""",

            "en": """Hello! I'm JOKKO AI 🥁, your personal assistant for navigating life in Italy.

I'm here to help you with:
• 📋 Residence permits and documents
• 🏥 Health and medical assistance
• 💼 Work and labor rights
• 🏠 Housing and residence
• 📚 Education and training

Write your question in your preferred language. How can I help you today?"""
        }
        
        return {
            "response": greetings.get(language, greetings["it"]),
            "category": "greeting",
            "confidence": 1.0,
            "sources": []
        }
        
    def generate_emergency_response(self, language: str) -> Dict:
        """Genera risposta per emergenze"""
        emergency_responses = {
            "it": """🚨 EMERGENZA - NUMERI UTILI IMMEDIATI:

• 🚑 Emergenza medica: 118
• 🚔 Polizia: 113
• 🚒 Vigili del Fuoco: 115
• 🆘 Carabinieri: 112

Se hai bisogno di assistenza immediata, chiama questi numeri. Per questioni non urgenti, continua pure a scrivermi e ti aiuterò con le informazioni che cerchi.""",

            "fr": """🚨 URGENCE - NUMÉROS UTILES IMMÉDIATS:

• 🚑 Urgence médicale: 118
• 🚔 Police: 113
• 🚒 Pompiers: 115
• 🆘 Carabiniers: 112

Si vous avez besoin d'une assistance immédiate, appelez ces numéros. Pour des questions non urgentes, continuez à m'écrire et je vous aiderai.""",

            "en": """🚨 EMERGENCY - IMMEDIATE USEFUL NUMBERS:

• 🚑 Medical emergency: 118
• 🚔 Police: 113
• 🚒 Fire department: 115
• 🆘 Carabinieri: 112

If you need immediate assistance, call these numbers. For non-urgent matters, continue writing to me and I'll help you."""
        }
        
        return {
            "response": emergency_responses.get(language, emergency_responses["it"]),
            "category": "emergency",
            "confidence": 1.0,
            "sources": [{"type": "emergency_numbers", "official": True}]
        }
        
    def generate_category_response(self, category: str, language: str, confidence: float) -> Dict:
        """Genera risposta basata sulla categoria identificata"""
        
        if category not in self.knowledge_base:
            return self.generate_fallback_response(language)
            
        data = self.knowledge_base[category]
        info = data["info"].get(language, data["info"]["it"])
        
        # Costruisci risposta completa
        response_parts = [f"📍 **{category.upper().replace('_', ' ')}**\n", info]
        
        # Aggiungi documenti necessari
        if "documenti" in data:
            response_parts.append(f"\n\n📄 **Documenti necessari:**")
            for doc in data["documenti"]:
                response_parts.append(f"• {doc}")
                
        # Aggiungi link ufficiali
        if "link_ufficiali" in data:
            response_parts.append(f"\n\n🔗 **Fonti ufficiali:**")
            for link in data["link_ufficiali"]:
                response_parts.append(f"• {link}")
                
        # Messaggio finale
        final_messages = {
            "it": "\n\n💭 Hai altre domande su questo argomento? Scrivimi per maggiori dettagli!",
            "fr": "\n\n💭 Avez-vous d'autres questions sur ce sujet? Écrivez-moi pour plus de détails!",
            "en": "\n\n💭 Do you have other questions on this topic? Write to me for more details!"
        }
        
        response_parts.append(final_messages.get(language, final_messages["it"]))
        
        return {
            "response": "\n".join(response_parts),
            "category": category,
            "confidence": confidence,
            "sources": data.get("link_ufficiali", [])
        }
        
    def generate_fallback_response(self, language: str) -> Dict:
        """Genera risposta di fallback quando non trova categoria"""
        fallback_responses = {
            "it": """Non sono sicuro di aver capito la tua domanda. Però sono qui per aiutarti! 

Prova a riformulare la domanda o scegli uno di questi argomenti:
• 📋 Permesso di soggiorno
• 🏥 Sanità e salute
• 💼 Lavoro
• 🏠 Casa e residenza
• 📚 Educazione

Oppure scrivi semplicemente quello che ti serve e farò del mio meglio per aiutarti!""",

            "fr": """Je ne suis pas sûr d'avoir compris votre question. Mais je suis là pour vous aider!

Essayez de reformuler la question ou choisissez l'un de ces sujets:
• 📋 Permis de séjour
• 🏥 Santé
• 💼 Travail
• 🏠 Logement
• 📚 Éducation

Ou écrivez simplement ce dont vous avez besoin et je ferai de mon mieux pour vous aider!""",

            "en": """I'm not sure I understood your question. But I'm here to help!

Try rephrasing the question or choose one of these topics:
• 📋 Residence permit
• 🏥 Health
• 💼 Work
• 🏠 Housing
• 📚 Education

Or simply write what you need and I'll do my best to help you!"""
        }
        
        return {
            "response": fallback_responses.get(language, fallback_responses["it"]),
            "category": "fallback",
            "confidence": 0.1,
            "sources": []
        }
        
    async def process_message(self, message: str, language: str = "it", user_id: Optional[str] = None) -> Dict:
        """Processa messaggio utente e genera risposta AI"""
        
        try:
            # Log della richiesta
            logger.info(f"Processing message: {message[:50]}... | Language: {language}")
            
            # Rileva lingua se non specificata correttamente
            if language == "auto":
                language = self.detect_language(message)
                
            # Verifica emergenza (priorità massima)
            if self.is_emergency(message, language):
                return self.generate_emergency_response(language)
                
            # Verifica saluto
            if self.is_greeting(message, language):
                return self.generate_greeting_response(language)
                
            # Classifica categoria della domanda
            category, confidence = self.classify_query_category(message)
            
            # Salva conversazione (opzionale)
            if user_id:
                if user_id not in self.conversation_history:
                    self.conversation_history[user_id] = []
                    
                self.conversation_history[user_id].append({
                    "timestamp": datetime.now().isoformat(),
                    "message": message,
                    "category": category,
                    "language": language
                })
                
            # Genera risposta basata su categoria
            if confidence > 0.2:  # Soglia di confidenza
                return self.generate_category_response(category, language, confidence)
            else:
                return self.generate_fallback_response(language)
                
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            
            error_responses = {
                "it": "Mi dispiace, ho avuto un problema tecnico. Puoi riprovare tra un momento?",
                "fr": "Désolé, j'ai eu un problème technique. Pouvez-vous réessayer dans un moment?",
                "en": "Sorry, I had a technical problem. Can you try again in a moment?"
            }
            
            return {
                "response": error_responses.get(language, error_responses["it"]),
                "category": "error",
                "confidence": 0.0,
                "sources": []
            }

# Test dell'engine AI
if __name__ == "__main__":
    async def test_jokko():
        ai = JokkoAI()
        
        test_messages = [
            ("Ciao, sono nuovo in Italia", "it"),
            ("Come faccio il permesso di soggiorno?", "it"),
            ("Emergenza medica aiuto", "it"),
            ("Hello, I need help with work", "en")
        ]
        
        for message, lang in test_messages:
            print(f"\n--- Test: {message} ({lang}) ---")
            response = await ai.process_message(message, lang)
            print(f"Category: {response['category']}")
            print(f"Response: {response['response'][:100]}...")
            
    asyncio.run(test_jokko())
