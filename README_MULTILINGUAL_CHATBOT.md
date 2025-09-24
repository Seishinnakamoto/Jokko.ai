# 🤖 Sistema Chatbot Multilingue

Sistema completo per creare un chatbot multilingue con integrazione Glide App, elaborazione tramite Groq API, traduzione automatica con LibreTranslate, e automazione avanzata come alternativa gratuita a Make.com.

## 🌟 Caratteristiche Principali

- **🌍 Supporto Multilingue**: 12+ lingue africane ed europee
- **🚀 Integrazione Glide**: Webhook e API per app Glide
- **🧠 AI Avanzata**: Elaborazione tramite Groq API (Mixtral)
- **🔄 Traduzione Automatica**: LibreTranslate per traduzioni real-time
- **⚡ Automazione**: Sistema completo alternativo a Make.com
- **📊 Analytics**: Statistiche dettagliate e monitoraggio
- **📧 Notifiche**: Sistema email per amministratori
- **🔒 Sicurezza**: CORS, validazione input, logging

## 🗣️ Lingue Supportate

| Codice | Lingua | Nome Nativo |
|--------|--------|-------------|
| `it` | Italiano | Italiano |
| `fr` | Francese | Français |
| `en` | Inglese | English |
| `wo` | Wolof | Wolof |
| `bm` | Bambara | Bamanankan |
| `ha` | Hausa | هَرْشَن هَوْسَ |
| `sw` | Swahili | Kiswahili |
| `ti` | Tigrino | ትግርኛ |
| `am` | Amarico | አማርኛ |
| `snk` | Soninke | Soninkanxanne |
| `ff` | Fulfulde | Fulfulde |
| `ln` | Lingala | Lingála |

## 🏗️ Architettura del Sistema

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Glide App     │───▶│  Webhook Server  │───▶│ Multilingual    │
│                 │    │                  │    │ Chatbot         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ Automation       │    │ Groq API        │
                       │ Engine           │    │ (Mixtral)       │
                       └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ Database         │    │ LibreTranslate  │
                       │ (SQLite)         │    │ API             │
                       └──────────────────┘    └─────────────────┘
```

## 🚀 Installazione e Configurazione

### 1. Prerequisiti

```bash
# Python 3.8+
python --version

# Clona il repository
git clone <repository-url>
cd multilingual-chatbot
```

### 2. Installa Dipendenze

```bash
pip install -r requirements.txt
```

### 3. Configurazione Variabili d'Ambiente

Crea un file `.env`:

```bash
# OBBLIGATORIO: Groq API
GROQ_API_KEY=your_groq_api_key_here

# OPZIONALE: LibreTranslate
LIBRETRANSLATE_URL=https://libretranslate.com/translate
LIBRETRANSLATE_API_KEY=your_api_key_if_private

# OPZIONALE: Configurazione Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
ADMIN_EMAIL=admin@yourdomain.com

# OPZIONALE: Server
HOST=0.0.0.0
PORT=8000
DEBUG=false

# OPZIONALE: Database
DATABASE_PATH=automation.db
DB_BACKUP_INTERVAL=24

# OPZIONALE: Funzionalità
ENABLE_AUTOMATION=true
ENABLE_ANALYTICS=true
LOG_LEVEL=INFO
```

### 4. Ottieni API Keys

#### Groq API (Obbligatoria)
1. Vai su [console.groq.com](https://console.groq.com/)
2. Crea un account
3. Genera una API key
4. Aggiungi `GROQ_API_KEY=your_key` al file `.env`

#### LibreTranslate (Opzionale)
- **Servizio pubblico**: Usa `https://libretranslate.com/translate`
- **Istanza privata**: Configura `LIBRETRANSLATE_API_KEY`

## 🎯 Utilizzo

### Avvio del Server

```bash
python main_app.py
```

Il server sarà disponibile su `http://localhost:8000`

### Test dell'Interfaccia

Visita `http://localhost:8000` per l'interfaccia di test interattiva.

## 🔗 Integrazione con Glide App

### 1. Configurazione Webhook in Glide

1. **Aggiungi Action**: Webhook
2. **URL**: `https://your-domain.com/webhook/chat`
3. **Metodo**: POST
4. **Headers**: `Content-Type: application/json`

### 2. Formato Dati Glide

```json
{
  "user_id": "user123",
  "message": "Come posso ottenere il permesso di soggiorno?",
  "language": "it",
  "session_id": "session456"
}
```

### 3. Risposta del Sistema

```json
{
  "response": "Per ottenere il permesso di soggiorno...",
  "original_response": "To obtain a residence permit...",
  "detected_language": "it",
  "processing_time": 1.23,
  "timestamp": "2024-01-15T10:30:00Z",
  "status": "success",
  "user_id": "user123",
  "session_id": "session456"
}
```

## 📊 API Endpoints

### Chat API

#### POST `/api/chat`
Elaborazione messaggi chat

**Request:**
```json
{
  "user_id": "user123",
  "message": "Hello, I need help",
  "language": "en"
}
```

**Response:**
```json
{
  "data": {
    "response": "Hello! I'm JOKKO AI...",
    "detected_language": "en",
    "processing_time": 0.85
  },
  "status": "success"
}
```

#### POST `/webhook/chat`
Webhook per app Glide (stesso formato)

### Informazioni Sistema

#### GET `/api/languages`
Lista lingue supportate

#### GET `/api/health`
Controllo stato sistema

#### GET `/api/analytics`
Statistiche utilizzo (richiede `?days=7`)

#### GET `/api/workflows`
Stato workflow automazione

#### GET `/api/config`
Informazioni configurazione pubblica

## ⚙️ Sistema di Automazione (Alternativa Make.com)

### Workflow Predefiniti

1. **Chat Logging**: Registra tutte le interazioni
2. **Daily Stats**: Report giornalieri via email
3. **Error Notification**: Notifiche errori in tempo reale

### Creazione Workflow Personalizzati

```python
from automation_engine import Workflow, AutomationTrigger, AutomationAction

# Definisci workflow
workflow = Workflow(
    workflow_id="custom_workflow",
    name="My Custom Workflow",
    description="Custom automation workflow",
    trigger=AutomationTrigger(
        trigger_id="webhook_trigger",
        trigger_type=TriggerType.WEBHOOK,
        config={"endpoint": "/webhook/custom"}
    ),
    actions=[
        AutomationAction(
            action_id="send_email",
            action_type=ActionType.SEND_EMAIL,
            config={"template": "custom_template"}
        )
    ]
)

# Aggiungi al motore
automation_engine.add_workflow(workflow)
```

### Triggers Disponibili

- `WEBHOOK`: Attivazione via webhook
- `SCHEDULE`: Attivazione programmata
- `EMAIL`: Attivazione via email
- `DATABASE`: Attivazione da database
- `API_CALL`: Attivazione via API

### Actions Disponibili

- `SEND_EMAIL`: Invio email
- `LOG_DATABASE`: Registrazione database
- `API_REQUEST`: Richiesta API esterna
- `NOTIFY_ADMIN`: Notifica amministratore
- `TRANSLATE_TEXT`: Traduzione testo
- `PROCESS_CHAT`: Elaborazione chat

## 📈 Analytics e Monitoraggio

### Metriche Disponibili

- **Messaggi Totali**: Conteggio interazioni
- **Utenti Unici**: Utenti distinti
- **Distribuzione Lingue**: Utilizzo per lingua
- **Tempo Elaborazione**: Performance sistema
- **Tasso Errori**: Monitoraggio affidabilità

### Dashboard Analytics

```bash
# Ottieni statistiche ultimi 7 giorni
curl http://localhost:8000/api/analytics?days=7
```

### Database Schema

```sql
-- Chat interactions
CREATE TABLE chat_logs (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    language TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    processing_time REAL,
    session_id TEXT
);

-- Workflow executions
CREATE TABLE workflow_executions (
    id INTEGER PRIMARY KEY,
    execution_id TEXT UNIQUE NOT NULL,
    workflow_id TEXT NOT NULL,
    status TEXT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    error_message TEXT,
    results TEXT
);

-- User analytics
CREATE TABLE user_analytics (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    language TEXT NOT NULL,
    message_count INTEGER DEFAULT 1,
    last_interaction DATETIME DEFAULT CURRENT_TIMESTAMP,
    topics TEXT
);
```

## 🛠️ Sviluppo e Testing

### Test Locale

```bash
# Test configurazione
python config.py

# Test chatbot
python multilingual_chatbot.py

# Test automazione
python automation_engine.py

# Test server completo
python main_app.py
```

### Test API

```bash
# Test health check
curl http://localhost:8000/api/health

# Test chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Ciao, come stai?", "language": "it"}'

# Test lingue supportate
curl http://localhost:8000/api/languages
```

## 🚀 Deployment

### Deployment su Cloud

#### Heroku
```bash
# Crea app Heroku
heroku create your-chatbot-app

# Configura variabili
heroku config:set GROQ_API_KEY=your_key

# Deploy
git push heroku main
```

#### Railway
```bash
# Installa Railway CLI
npm install -g @railway/cli

# Login e deploy
railway login
railway init
railway up
```

#### DigitalOcean App Platform
1. Connetti repository GitHub
2. Configura variabili d'ambiente
3. Deploy automatico

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main_app.py"]
```

```bash
# Build e run
docker build -t multilingual-chatbot .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key multilingual-chatbot
```

## 🔧 Personalizzazione

### Aggiungere Nuove Lingue

1. **Aggiorna config.py**:
```python
SUPPORTED_LANGUAGES['new_lang'] = 'Nome Lingua'
```

2. **Aggiorna pattern di rilevamento**:
```python
patterns = {
    'new_lang': ['parola1', 'parola2', 'parola3']
}
```

3. **Aggiungi prompt di sistema**:
```python
SYSTEM_PROMPTS['new_lang'] = "You are JOKKO AI..."
```

### Personalizzare Risposte AI

Modifica i prompt di sistema in `config.py` per adattare le risposte alle tue esigenze specifiche.

### Aggiungere Nuovi Workflow

Crea workflow personalizzati estendendo la classe `AutomationEngine`.

## 🐛 Troubleshooting

### Problemi Comuni

#### 1. Errore API Key
```
ERROR: GROQ_API_KEY environment variable is required
```
**Soluzione**: Configura la variabile d'ambiente `GROQ_API_KEY`

#### 2. Errore Porta
```
ERROR: Port 8000 is already in use
```
**Soluzione**: Cambia porta con `PORT=8001`

#### 3. Errore Traduzione
```
WARNING: LibreTranslate API error: 500
```
**Soluzione**: Verifica URL LibreTranslate o usa servizio alternativo

#### 4. Errore Database
```
ERROR: Database connection failed
```
**Soluzione**: Verifica permessi directory e spazio disco

### Log di Debug

```bash
# Abilita debug logging
export LOG_LEVEL=DEBUG
python main_app.py
```

## 📚 Risorse Aggiuntive

### Documentazione API
- [Groq API Docs](https://console.groq.com/docs)
- [LibreTranslate API](https://libretranslate.com/docs)
- [Glide Apps Webhooks](https://docs.glideapps.com)

### Community e Supporto
- [GitHub Issues](https://github.com/your-repo/issues)
- [Discord Community](https://discord.gg/your-server)
- Email: support@yourdomain.com

## 📄 Licenza

MIT License - vedi file LICENSE per dettagli.

## 🤝 Contributi

I contributi sono benvenuti! Per contribuire:

1. Fork del repository
2. Crea branch feature (`git checkout -b feature/AmazingFeature`)
3. Commit modifiche (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri Pull Request

## 🙏 Ringraziamenti

- **Groq** per l'API AI veloce e potente
- **LibreTranslate** per il servizio di traduzione open source
- **Glide** per la piattaforma no-code
- **Community open source** per i contributi e feedback

---

**Creato con ❤️ per supportare migranti e rifugiati in Italia**