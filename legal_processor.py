#!/usr/bin/env python3
"""
JOKKO AI - Processore Documenti Legali
Sistema per scraping, indicizzazione e ricerca normative italiane

Autore: MiniMax Agent
Data: 2025-06-20
"""

import asyncio
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import sqlite3
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalProcessor:
    """Processore documenti legali per JOKKO AI"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            self.data_dir = Path(__file__).parent.parent.parent / "data" 
        else:
            self.data_dir = Path(data_dir)
            
        self.legal_docs_dir = self.data_dir / "legal_docs"
        self.embeddings_dir = self.data_dir / "embeddings"
        
        # Crea directory se non esistono
        self.legal_docs_dir.mkdir(parents=True, exist_ok=True)
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
        
        self.setup_database()
        self.setup_legal_sources()
        self.setup_search_index()
        
    def setup_database(self):
        """Configura database SQLite per documenti legali"""
        
        self.db_path = self.data_dir / "legal_database.db"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabella documenti legali
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS legal_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source_url TEXT,
                    category TEXT,
                    publication_date DATE,
                    last_updated DATE,
                    content_hash TEXT UNIQUE,
                    keywords TEXT,
                    relevance_score REAL DEFAULT 0.0
                )
            ''')
            
            # Tabella metadati scraping
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scraping_metadata (
                    source_name TEXT PRIMARY KEY,
                    last_scraped DATE,
                    documents_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0
                )
            ''')
            
            # Indice per ricerca testuale
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_content_search 
                ON legal_documents(category, keywords)
            ''')
            
            conn.commit()
            
    def setup_legal_sources(self):
        """Configura fonti legali italiane da monitorare"""
        
        self.legal_sources = {
            "gazzetta_ufficiale": {
                "name": "Gazzetta Ufficiale",
                "base_url": "https://www.gazzettaufficiale.it",
                "categories": ["immigrazione", "permessi", "cittadinanza"],
                "selectors": {
                    "title": ".title",
                    "content": ".content", 
                    "date": ".date"
                }
            },
            
            "normattiva": {
                "name": "Normattiva",
                "base_url": "https://www.normattiva.it",
                "categories": ["testo-unico-immigrazione", "decreto-flussi"],
                "api_endpoint": "/api/search"
            },
            
            "interno_gov": {
                "name": "Ministero dell'Interno",
                "base_url": "https://www.interno.gov.it",
                "categories": ["immigrazione", "cittadinanza", "permessi-soggiorno"],
                "sections": ["/temi/immigrazione-e-asilo/", "/cittadinanza/"]
            },
            
            "lavoro_gov": {
                "name": "Ministero del Lavoro",
                "base_url": "https://www.lavoro.gov.it", 
                "categories": ["immigrazione", "lavoro-stranieri"],
                "sections": ["/temi-e-priorita/immigrazione/"]
            }
        }
        
        # Documenti base precaricati
        self.preload_essential_documents()
        
    def preload_essential_documents(self):
        """Precarica documenti essenziali nella base di conoscenza"""
        
        essential_docs = [
            {
                "title": "Testo Unico Immigrazione - Art. 5 Permesso di Soggiorno",
                "content": """Il permesso di soggiorno è obbligatorio per tutti i cittadini di Paesi non appartenenti all'Unione europea che intendano soggiornare in Italia per più di tre mesi. 

La richiesta deve essere presentata entro otto giorni dall'ingresso nel territorio dello Stato presso:
- La Questura competente per territorio
- Gli uffici postali autorizzati (kit postale)
- I patronati e gli enti autorizzati

Documenti necessari:
1. Passaporto con visto d'ingresso valido
2. Modulo di richiesta compilato
3. Fotografie formato tessera
4. Marca da bollo da €16,00
5. Ricevuta del versamento di €30,46

Il permesso ha validità variabile secondo il motivo del soggiorno:
- Lavoro subordinato: durata del contratto, max 2 anni
- Lavoro autonomo: 2 anni
- Studio: durata del corso, max 1 anno
- Ricongiungimento familiare: 2 anni""",
                "category": "permesso_soggiorno",
                "source_url": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:1998-07-25;286",
                "keywords": "permesso soggiorno cittadini non UE questura documenti richiesta"
            },
            
            {
                "title": "Accesso al Servizio Sanitario Nazionale per Stranieri",
                "content": """I cittadini stranieri regolarmente soggiornanti hanno diritto all'assistenza sanitaria al pari dei cittadini italiani.

Iscrizione obbligatoria al SSN per:
- Stranieri con permesso di soggiorno superiore a 3 mesi
- Lavoratori subordinati e autonomi
- Familiari ricongiunti

Procedura di iscrizione:
1. Recarsi all'ASL di residenza
2. Presentare: permesso di soggiorno, codice fiscale, documento di identità
3. Scegliere il medico di base
4. Ricevere la tessera sanitaria

Prestazioni garantite:
- Assistenza medica di base
- Ricoveri ospedalieri
- Medicina specialistica
- Farmaci essenziali
- Assistenza materno-infantile

Costo: gratuito per redditi bassi, ticket per altre prestazioni""",
                "category": "sanita",
                "source_url": "https://www.salute.gov.it/portale/temi/p2_6.jsp?lingua=italiano&id=1122",
                "keywords": "sanità SSN stranieri iscrizione ASL medico base tessera sanitaria"
            },
            
            {
                "title": "Diritti e Doveri del Lavoratore Straniero",
                "content": """I lavoratori stranieri con regolare permesso di soggiorno per lavoro hanno gli stessi diritti e doveri dei lavoratori italiani.

Diritti del lavoratore straniero:
- Parità di trattamento economico e normativo
- Stessi diritti sindacali
- Accesso alla formazione professionale
- Protezione in caso di infortunio
- Accesso agli ammortizzatori sociali

Tipologie di permesso per lavoro:
- Lavoro subordinato: richiede nulla osta al lavoro
- Lavoro autonomo: richiede requisiti specifici
- Lavoro stagionale: durata limitata

Documenti necessari per lavorare:
1. Permesso di soggiorno per lavoro
2. Codice fiscale
3. Contratto di lavoro regolare
4. Iscrizione INPS/INAIL

Conversione permesso:
È possibile convertire altri tipi di permesso in permesso per lavoro subordinato se si trova un'occupazione regolare.""",
                "category": "lavoro", 
                "source_url": "https://www.lavoro.gov.it/temi-e-priorita/immigrazione/Pagine/default.aspx",
                "keywords": "lavoro stranieri diritti doveri permesso contratto codice fiscale INPS"
            }
        ]
        
        # Inserisci documenti nel database se non esistono già
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for doc in essential_docs:
                content_hash = hashlib.md5(doc["content"].encode()).hexdigest()
                
                cursor.execute('''
                    INSERT OR IGNORE INTO legal_documents 
                    (title, content, source_url, category, publication_date, 
                     last_updated, content_hash, keywords, relevance_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    doc["title"],
                    doc["content"], 
                    doc["source_url"],
                    doc["category"],
                    datetime.now().date(),
                    datetime.now().date(),
                    content_hash,
                    doc["keywords"],
                    1.0
                ))
                
            conn.commit()
            logger.info(f"Precaricati {len(essential_docs)} documenti essenziali")
            
    def setup_search_index(self):
        """Configura indice di ricerca semplificato"""
        
        # In produzione: integrare con Elasticsearch o Whoosh
        self.search_weights = {
            "title": 3.0,
            "keywords": 2.5, 
            "category": 2.0,
            "content": 1.0
        }
        
    async def search_legal_content(self, query: str, category: str = None, limit: int = 5) -> List[Dict]:
        """Ricerca contenuti legali nel database"""
        
        try:
            query_terms = query.lower().split()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Costruisci query SQL
                base_query = '''
                    SELECT id, title, content, source_url, category, relevance_score
                    FROM legal_documents 
                    WHERE 1=1
                '''
                params = []
                
                # Filtro per categoria se specificato
                if category:
                    base_query += " AND category = ?"
                    params.append(category)
                    
                # Ricerca testuale semplificata
                search_conditions = []
                for term in query_terms:
                    search_conditions.append('''
                        (title LIKE ? OR content LIKE ? OR keywords LIKE ?)
                    ''')
                    params.extend([f"%{term}%", f"%{term}%", f"%{term}%"])
                    
                if search_conditions:
                    base_query += " AND (" + " OR ".join(search_conditions) + ")"
                    
                base_query += " ORDER BY relevance_score DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(base_query, params)
                results = cursor.fetchall()
                
                # Formatta risultati
                formatted_results = []
                for row in results:
                    doc_id, title, content, source_url, cat, relevance = row
                    
                    # Calcola score di rilevanza basato su query
                    relevance_score = self.calculate_relevance(query, title, content, cat)
                    
                    formatted_results.append({
                        "id": doc_id,
                        "title": title,
                        "excerpt": self.extract_relevant_excerpt(content, query_terms),
                        "source_url": source_url,
                        "category": cat,
                        "relevance_score": relevance_score
                    })
                    
                # Ordina per rilevanza calcolata
                formatted_results.sort(key=lambda x: x["relevance_score"], reverse=True)
                
                logger.info(f"Trovati {len(formatted_results)} risultati per query: {query}")
                return formatted_results
                
        except Exception as e:
            logger.error(f"Errore nella ricerca legale: {str(e)}")
            return []
            
    def calculate_relevance(self, query: str, title: str, content: str, category: str) -> float:
        """Calcola score di rilevanza per un documento"""
        
        query_lower = query.lower()
        title_lower = title.lower() 
        content_lower = content.lower()
        
        score = 0.0
        
        # Score basato su presenza termini nel titolo
        if query_lower in title_lower:
            score += self.search_weights["title"]
            
        # Score basato su presenza termini nel contenuto
        query_terms = query_lower.split()
        for term in query_terms:
            if term in title_lower:
                score += self.search_weights["title"] * 0.5
            if term in content_lower:
                score += self.search_weights["content"]
                
        # Bonus per categoria matching
        if category and any(term in category for term in query_terms):
            score += self.search_weights["category"]
            
        return score
        
    def extract_relevant_excerpt(self, content: str, query_terms: List[str], max_length: int = 200) -> str:
        """Estrae excerpt rilevante dal contenuto"""
        
        content_lower = content.lower()
        
        # Trova la posizione del primo termine della query
        best_position = 0
        for term in query_terms:
            pos = content_lower.find(term.lower())
            if pos != -1:
                best_position = max(0, pos - 50)  # Inizia 50 caratteri prima
                break
                
        # Estrai excerpt
        excerpt = content[best_position:best_position + max_length]
        
        # Aggiungi ellipsis se necessario
        if best_position > 0:
            excerpt = "..." + excerpt
        if len(content) > best_position + max_length:
            excerpt = excerpt + "..."
            
        return excerpt.strip()
        
    async def get_document_by_category(self, category: str, limit: int = 3) -> List[Dict]:
        """Ottieni documenti per categoria specifica"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT title, content, source_url, relevance_score
                FROM legal_documents 
                WHERE category = ?
                ORDER BY relevance_score DESC 
                LIMIT ?
            ''', (category, limit))
            
            results = cursor.fetchall()
            
            return [
                {
                    "title": row[0],
                    "content": row[1][:300] + "..." if len(row[1]) > 300 else row[1],
                    "source_url": row[2],
                    "relevance_score": row[3]
                }
                for row in results
            ]
            
    async def update_legal_database(self) -> Dict[str, int]:
        """Aggiorna database con nuovi documenti legali (placeholder per scraping)"""
        
        # In produzione: implementare scraping real-time
        # Per ora simula aggiornamento
        
        logger.info("Simulazione aggiornamento database legale...")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Conta documenti attuali per categoria
            cursor.execute('''
                SELECT category, COUNT(*) 
                FROM legal_documents 
                GROUP BY category
            ''')
            
            results = cursor.fetchall()
            stats = dict(results)
            
            # Aggiorna metadata scraping
            cursor.execute('''
                INSERT OR REPLACE INTO scraping_metadata 
                (source_name, last_scraped, documents_count, success_rate)
                VALUES (?, ?, ?, ?)
            ''', ("sistema_interno", datetime.now().date(), sum(stats.values()), 1.0))
            
            conn.commit()
            
        logger.info(f"Database aggiornato. Statistiche: {stats}")
        return stats
        
    def get_database_statistics(self) -> Dict:
        """Ottieni statistiche database documenti legali"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Conta totale documenti
            cursor.execute("SELECT COUNT(*) FROM legal_documents")
            total_docs = cursor.fetchone()[0]
            
            # Conta per categoria
            cursor.execute('''
                SELECT category, COUNT(*) 
                FROM legal_documents 
                GROUP BY category 
                ORDER BY COUNT(*) DESC
            ''')
            by_category = dict(cursor.fetchall())
            
            # Ultimo aggiornamento
            cursor.execute('''
                SELECT MAX(last_updated) FROM legal_documents
            ''')
            last_update = cursor.fetchone()[0]
            
        return {
            "total_documents": total_docs,
            "by_category": by_category,
            "last_update": last_update,
            "database_path": str(self.db_path)
        }

# Test del processore legale
if __name__ == "__main__":
    async def test_legal_processor():
        processor = LegalProcessor()
        
        # Test ricerca
        test_queries = [
            ("permesso di soggiorno", None),
            ("sanità stranieri", "sanita"),
            ("diritti lavoratori", "lavoro")
        ]
        
        for query, category in test_queries:
            print(f"\n--- Ricerca: '{query}' (categoria: {category}) ---")
            results = await processor.search_legal_content(query, category)
            
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['title']}")
                print(f"   Score: {result['relevance_score']:.2f}")
                print(f"   Excerpt: {result['excerpt'][:100]}...")
                
        # Test statistiche
        print("\n--- Statistiche Database ---")
        stats = processor.get_database_statistics()
        print(f"Documenti totali: {stats['total_documents']}")
        print(f"Per categoria: {stats['by_category']}")
        
    asyncio.run(test_legal_processor())
