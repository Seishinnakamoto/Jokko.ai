#!/usr/bin/env python3
"""
JOKKO AI - Sistema Traduzione Multilingue
Gestisce traduzione automatica per 12 lingue africane e europee

Autore: MiniMax Agent
Data: 2025-06-20
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
import json
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultilingualTranslator:
    """Sistema traduzione multilingue per JOKKO AI"""
    
    def __init__(self, supported_languages: Dict[str, str]):
        self.supported_languages = supported_languages
        self.setup_translation_mappings()
        self.setup_basic_dictionaries()
        
    def setup_translation_mappings(self):
        """Configura mapping linguistici per Google Translate API"""
        self.google_translate_codes = {
            'it': 'it',    # Italiano
            'fr': 'fr',    # Français
            'en': 'en',    # English
            'wo': 'wo',    # Wolof
            'bm': 'bm',    # Bambara
            'ha': 'ha',    # Hausa
            'sw': 'sw',    # Kiswahili
            'ti': 'ti',    # Tigrinya
            'am': 'am',    # Amharic
            'snk': 'snk',  # Soninke
            'ff': 'ff',    # Pulaar/Fulfulde
            'ln': 'ln'     # Lingala
        }
        
    def setup_basic_dictionaries(self):
        """Configura dizionari base per traduzioni essenziali"""
        
        # Termini essenziali per assistenza migranti
        self.essential_terms = {
            # Documenti
            "permesso_soggiorno": {
                "it": "permesso di soggiorno",
                "fr": "permis de séjour", 
                "en": "residence permit",
                "wo": "takku dalal",
                "bm": "ka sigilen",
                "ha": "takardar zama",
                "sw": "kibali cha makazi",
                "ti": "ፍቃድ ትሪፎ",
                "am": "የመኖሪያ ፈቃድ",
                "snk": "seera yaaxu",
                "ff": "jaynde mo yaasi",
                "ln": "ndembo ya kovanda"
            },
            
            # Salute
            "ospedale": {
                "it": "ospedale",
                "fr": "hôpital",
                "en": "hospital", 
                "wo": "hôpital",
                "bm": "banakisɛbaga",
                "ha": "asibiti",
                "sw": "hospitali",
                "ti": "ሆስፒታል",
                "am": "ሆስፒታል",
                "snk": "banaku sababu",
                "ff": "hôpital",
                "ln": "lopitalo"
            },
            
            # Emergenza
            "aiuto": {
                "it": "aiuto",
                "fr": "aide",
                "en": "help",
                "wo": "ndimbal",
                "bm": "dɛmɛ",
                "ha": "taimako",
                "sw": "msaada", 
                "ti": "ሓገዝ",
                "am": "እርዳታ",
                "snk": "ballal",
                "ff": "ballal",
                "ln": "lisalisi"
            },
            
            # Lavoro
            "lavoro": {
                "it": "lavoro",
                "fr": "travail",
                "en": "work",
                "wo": "liggéey",
                "bm": "baara",
                "ha": "aiki",
                "sw": "kazi",
                "ti": "ሥራሕ",
                "am": "ሥራ",
                "snk": "gani",
                "ff": "golle",
                "ln": "mosala"
            },
            
            # Casa
            "casa": {
                "it": "casa",
                "fr": "maison",
                "en": "house",
                "wo": "kër",
                "bm": "so",
                "ha": "gida",
                "sw": "nyumba",
                "ti": "ቤት",
                "am": "ቤት",
                "snk": "bundu",
                "ff": "suudu",
                "ln": "ndako"
            }
        }
        
        # Frasi comuni per navigazione interfaccia
        self.ui_phrases = {
            "benvenuto": {
                "it": "Benvenuto in JOKKO AI",
                "fr": "Bienvenue dans JOKKO AI",
                "en": "Welcome to JOKKO AI",
                "wo": "Dalal ak JOKKO AI",
                "bm": "An ka bɛn na JOKKO AI",
                "ha": "Maraba da JOKKO AI",
                "sw": "Karibu kwenye JOKKO AI",
                "ti": "ናብ JOKKO AI ርሕበኻ",
                "am": "ወደ JOKKO AI እንኳን በደህና መጡ",
                "snk": "Xinna JOKKO AI",
                "ff": "A waali e JOKKO AI",
                "ln": "Boyei malamu na JOKKO AI"
            },
            
            "scrivi_messaggio": {
                "it": "Scrivi il tuo messaggio...",
                "fr": "Écrivez votre message...",
                "en": "Write your message...",
                "wo": "Bind sa bataaxal...",
                "bm": "I ka cikan sɛbɛn...",
                "ha": "Rubuta sakonka...",
                "sw": "Andika ujumbe wako...",
                "ti": "መልእኽትኻ ጽሓፍ...",
                "am": "መልእክትዎን ይጻፉ...",
                "snk": "A faaba sɛbɛ...",
                "ff": "Winndito kartal maa...",
                "ln": "Koma nsango na yo..."
            },
            
            "invia": {
                "it": "Invia",
                "fr": "Envoyer", 
                "en": "Send",
                "wo": "Yónn",
                "bm": "A ci",
                "ha": "Aiko",
                "sw": "Tuma",
                "ti": "ላእክ",
                "am": "ላክ",
                "snk": "Kii",
                "ff": "Neld",
                "ln": "Tinda"
            }
        }
        
    def detect_language_simple(self, text: str) -> str:
        """Rileva lingua con metodo semplificato basato su pattern"""
        
        text_lower = text.lower()
        
        # Pattern linguistici caratteristici
        patterns = {
            'it': ['che', 'per', 'con', 'del', 'una', 'sono', 'dove', 'come'],
            'fr': ['que', 'pour', 'avec', 'des', 'une', 'suis', 'où', 'comment'],
            'en': ['that', 'for', 'with', 'the', 'and', 'are', 'where', 'how'],
            'wo': ['ku', 'ak', 'ci', 'la', 'nga', 'am', 'fan', 'naka'],
            'ha': ['da', 'mai', 'na', 'ta', 'ka', 'ba', 'ina', 'yaya'],
            'sw': ['na', 'wa', 'ya', 'za', 'la', 'ni', 'wapi', 'jinsi']
        }
        
        scores = {}
        for lang, words in patterns.items():
            score = sum(1 for word in words if word in text_lower)
            scores[lang] = score
            
        # Trova lingua con score più alto
        if scores:
            detected = max(scores, key=scores.get)
            if scores[detected] > 0:
                return detected
                
        return 'it'  # Default italiano
        
    async def translate_with_fallback(self, text: str, target_lang: str, source_lang: str = "auto") -> str:
        """Traduce testo con sistema di fallback"""
        
        try:
            # Prova traduzione con dizionario interno per termini essenziali
            internal_translation = self.translate_essential_terms(text, target_lang)
            if internal_translation != text:
                return internal_translation
                
            # Simula traduzione (in produzione usare Google Translate API)
            return await self.simulate_translation(text, target_lang, source_lang)
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return text  # Ritorna testo originale se traduzione fallisce
            
    def translate_essential_terms(self, text: str, target_lang: str) -> str:
        """Traduce termini essenziali usando dizionario interno"""
        
        translated_text = text
        
        for term_key, translations in self.essential_terms.items():
            for source_lang, source_term in translations.items():
                if source_term.lower() in text.lower():
                    target_term = translations.get(target_lang, source_term)
                    translated_text = translated_text.replace(source_term, target_term)
                    
        return translated_text
        
    async def simulate_translation(self, text: str, target_lang: str, source_lang: str) -> str:
        """Simula traduzione (placeholder per API reale)"""
        
        # Simulazione base - in produzione integrare con Google Translate
        if target_lang == source_lang:
            return text
            
        # Simulazioni per test
        if target_lang == 'en' and 'permesso' in text.lower():
            return text.replace('permesso di soggiorno', 'residence permit')
        elif target_lang == 'fr' and 'permesso' in text.lower():
            return text.replace('permesso di soggiorno', 'permis de séjour')
            
        # Aggiunge indicatore di traduzione per debug
        return f"[{target_lang.upper()}] {text}"
        
    async def translate(self, text: str, target_lang: str, source_lang: str = "auto") -> str:
        """Metodo principale per traduzione"""
        
        # Validazione input
        if not text or not text.strip():
            return ""
            
        if target_lang not in self.supported_languages:
            logger.warning(f"Lingua non supportata: {target_lang}")
            return text
            
        # Rileva lingua sorgente se necessario
        if source_lang == "auto":
            source_lang = self.detect_language_simple(text)
            
        # Se lingue sono uguali, ritorna testo originale
        if source_lang == target_lang:
            return text
            
        # Esegui traduzione
        return await self.translate_with_fallback(text, target_lang, source_lang)
        
    def get_ui_phrase(self, phrase_key: str, language: str) -> str:
        """Ottieni frase UI tradotta"""
        
        if phrase_key in self.ui_phrases:
            return self.ui_phrases[phrase_key].get(language, 
                   self.ui_phrases[phrase_key].get('it', phrase_key))
        return phrase_key
        
    async def batch_translate(self, texts: List[str], target_lang: str, source_lang: str = "auto") -> List[str]:
        """Traduce multipli testi in parallelo"""
        
        tasks = [self.translate(text, target_lang, source_lang) for text in texts]
        return await asyncio.gather(*tasks)
        
    def get_supported_languages_list(self) -> List[Dict[str, str]]:
        """Ottieni lista lingue supportate con nomi nativi"""
        
        native_names = {
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
        
        return [
            {
                'code': code,
                'name': name,
                'native_name': native_names.get(code, name)
            }
            for code, name in self.supported_languages.items()
        ]

# Test del traduttore
if __name__ == "__main__":
    async def test_translator():
        supported_langs = {
            'it': 'Italiano', 'fr': 'Français', 'en': 'English',
            'wo': 'Wolof', 'ha': 'Hausa', 'sw': 'Kiswahili'
        }
        
        translator = MultilingualTranslator(supported_langs)
        
        test_texts = [
            "Come faccio il permesso di soggiorno?",
            "Ho bisogno di aiuto per trovare lavoro",
            "Dove si trova l'ospedale più vicino?"
        ]
        
        target_langs = ['en', 'fr', 'wo']
        
        for text in test_texts:
            print(f"\nTesto originale: {text}")
            for lang in target_langs:
                translation = await translator.translate(text, lang)
                print(f"  {lang}: {translation}")
                
        # Test frasi UI
        print("\n--- Test UI Phrases ---")
        for lang in ['it', 'en', 'wo']:
            welcome = translator.get_ui_phrase('benvenuto', lang)
            print(f"{lang}: {welcome}")
            
    asyncio.run(test_translator())
