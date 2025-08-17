# 🧠 AI Quiz Generator

Un'applicazione web avanzata che genera quiz personalizzati tramite intelligenza artificiale. Permette agli utenti di creare test su misura inserendo il tipo di esame, gli argomenti specifici e il numero di domande desiderate.

## ✨ Caratteristiche Principali

### 🎯 **Generazione Intelligente di Quiz**
- **AI-Powered**: Algoritmi avanzati per la creazione di domande pertinenti
- **Personalizzazione Completa**: Scegli tipo di esame, argomenti e numero di domande
- **Difficoltà Adattiva**: Domande che si adattano al livello dell'utente

### ⏱️ **Sistema di Quiz Interattivo**
- **Timer Dinamico**: 1 minuto per domanda con countdown visivo
- **Progresso in Tempo Reale**: Barra di avanzamento e indicatori di stato
- **Navigazione Fluida**: Possibilità di tornare alle domande precedenti

### 📊 **Analisi Dettagliate**
- **Punteggio Dinamico**: Calcolo percentuale in tempo reale
- **Statistiche Avanzate**: Performance per difficoltà e argomento
- **Raccomandazioni Personalizzate**: Suggerimenti di studio basati sui risultati

### 🎨 **Interfaccia Moderna**
- **Design Responsive**: Ottimizzato per desktop, tablet e mobile
- **Animazioni Fluide**: Transizioni e effetti visivi accattivanti
- **UX Intuitiva**: Interfaccia user-friendly e accessibile

## 🚀 Avvio Rapido

### Prerequisiti
- Python 3.7 o superiore
- Browser web moderno

### Installazione

1. **Clona il repository**
```bash
git clone <repository-url>
cd ai-quiz-generator
```

2. **Avvia il server**
```bash
python quiz_backend.py
```

3. **Apri il browser**
```
http://localhost:8080
```

## 📚 Materie e Argomenti Supportati

### 💻 **Informatica**
- Programmazione (OOP, Java, Python, etc.)
- Database (SQL, Progettazione DB, ACID)
- Algoritmi (Complessità, Strutture Dati)

### 🔢 **Matematica**
- Algebra (Equazioni, Funzioni)
- Geometria (Aree, Teoremi)
- Analisi (Derivate, Integrali)

### 📖 **Storia**
- Storia Moderna (Guerre Mondiali, etc.)
- Storia Antica (Impero Romano, etc.)
- Storia Contemporanea

### 🔬 **Scienze**
- Fisica (Meccanica, Relatività)
- Chimica (Elementi, Reazioni)
- Biologia (Cellule, Genetica)

### 📝 **Altre Materie**
- Letteratura Italiana
- Lingue Straniere
- Filosofia
- Diritto

## 🛠️ Architettura Tecnica

### Frontend
- **React 18**: Libreria UI moderna
- **CSS3**: Styling avanzato con gradients e animazioni
- **Font Awesome**: Icone professionali
- **Responsive Design**: Mobile-first approach

### Backend
- **Python HTTP Server**: Server built-in per massima compatibilità
- **AI Engine**: Sistema intelligente di generazione domande
- **JSON API**: RESTful endpoints per comunicazione client-server
- **CORS Support**: Accesso cross-origin abilitato

### Caratteristiche AI

```python
class QuizAI:
    def generate_questions(self, exam_type, topics, num_questions, difficulty_level):
        # Algoritmo di selezione intelligente
        # Adattamento difficoltà
        # Generazione dinamica
        # Personalizzazione contenuti
```

## 📡 API Endpoints

### `GET /`
Serve l'applicazione web principale

### `GET /health`
Health check del server

### `GET /api/topics`
Ritorna gli argomenti disponibili per materia

### `POST /api/generate-quiz`
Genera un nuovo quiz personalizzato

**Request Body:**
```json
{
    "examType": "Informatica",
    "topics": "Programmazione, Database",
    "numQuestions": 10,
    "difficulty": "medio"
}
```

**Response:**
```json
{
    "success": true,
    "questions": [...],
    "metadata": {
        "examType": "Informatica",
        "topics": "Programmazione, Database",
        "numQuestions": 10,
        "difficulty": "medio",
        "generatedAt": 1640995200
    }
}
```

### `POST /api/submit-quiz`
Invia le risposte e calcola i risultati

**Request Body:**
```json
{
    "questions": [...],
    "answers": {"0": 2, "1": 0, "2": 3},
    "timeSpent": 450
}
```

## 🎯 Funzionalità Avanzate

### 🧮 **Algoritmo di Punteggio Dinamico**
- Calcolo percentuale in tempo reale
- Peso per difficoltà delle domande
- Bonus per velocità di risposta
- Penalità per risposte sbagliate

### 📈 **Analytics e Reporting**
- Statistiche per difficoltà
- Performance per argomento
- Tempo medio per domanda
- Trend di miglioramento

### 🎨 **Personalizzazione UI**
- Temi colore adattivi
- Animazioni personalizzabili
- Layout responsivo
- Accessibilità completa

## 🔧 Configurazione Avanzata

### Variabili d'Ambiente
```bash
PORT=8080                    # Porta del server
DEBUG=true                   # Modalità debug
QUIZ_TIMEOUT=3600           # Timeout quiz (secondi)
MAX_QUESTIONS=50            # Numero massimo domande
```

### Personalizzazione Domande
Modifica il file `quiz_backend.py` per aggiungere nuove materie o domande:

```python
self.question_templates = {
    "NuovaMateria": {
        "NuovoArgomento": [
            {
                "question": "La tua domanda qui?",
                "options": ["A", "B", "C", "D"],
                "correct": 2,
                "explanation": "Spiegazione dettagliata",
                "difficulty": "medio"
            }
        ]
    }
}
```

## 🚀 Deployment

### Locale
```bash
python quiz_backend.py
```

### Docker
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
EXPOSE 8080
CMD ["python", "quiz_backend.py"]
```

### Cloud Platforms
- **Heroku**: Deploy diretto con `git push`
- **Vercel**: Supporto per Python serverless
- **AWS**: EC2 o Lambda deployment
- **Google Cloud**: App Engine ready

## 🤝 Contribuire

1. Fork del repository
2. Crea un branch per la feature (`git checkout -b feature/AmazingFeature`)
3. Commit delle modifiche (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## 📄 Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi `LICENSE` per maggiori dettagli.

## 🙏 Ringraziamenti

- **React Team** per l'eccellente libreria UI
- **Font Awesome** per le icone professionali
- **Python Community** per gli strumenti di sviluppo
- **AI Research Community** per gli algoritmi di ML

## 📞 Supporto

Per supporto, bug report o richieste di funzionalità:
- 📧 Email: support@aiquizgenerator.com
- 🐛 Issues: GitHub Issues
- 💬 Chat: Discord Community
- 📚 Docs: Wiki del progetto

---

**Sviluppato con ❤️ per rendere l'apprendimento più interattivo e personalizzato**
