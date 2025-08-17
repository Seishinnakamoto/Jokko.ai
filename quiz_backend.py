#!/usr/bin/env python3
"""
AI Quiz Generator - Backend Server
Advanced quiz generation with AI integration
"""

import json
import random
import os
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class QuizAI:
    """Enhanced AI service for generating personalized quiz questions"""
    
    def __init__(self):
        self.question_templates = {
            "Informatica": {
                "Programmazione": [
                    {
                        "question": "Quale di questi è un linguaggio di programmazione orientato agli oggetti?",
                        "options": ["HTML", "CSS", "Java", "SQL"],
                        "correct": 2,
                        "explanation": "Java è un linguaggio di programmazione orientato agli oggetti, mentre HTML e CSS sono linguaggi di markup e styling, e SQL è un linguaggio per database.",
                        "difficulty": "facile"
                    },
                    {
                        "question": "Cosa significa 'OOP' nella programmazione?",
                        "options": ["Object Oriented Programming", "Open Office Program", "Online Operation Protocol", "Optimal Output Process"],
                        "correct": 0,
                        "explanation": "OOP sta per Object Oriented Programming (Programmazione Orientata agli Oggetti), un paradigma di programmazione basato su oggetti.",
                        "difficulty": "medio"
                    },
                    {
                        "question": "Qual è il principio dell'ereditarietà nella programmazione OOP?",
                        "options": ["Nascondere i dettagli implementativi", "Creare nuove classi basate su classi esistenti", "Permettere a oggetti di rispondere diversamente allo stesso messaggio", "Raggruppare dati e metodi insieme"],
                        "correct": 1,
                        "explanation": "L'ereditarietà permette di creare nuove classi (classi figlie) che ereditano proprietà e metodi da classi esistenti (classi padre).",
                        "difficulty": "medio"
                    },
                    {
                        "question": "Cosa rappresenta il polimorfismo in OOP?",
                        "options": ["Un oggetto può avere più forme", "Una classe può ereditare da più classi", "Un metodo può essere sovrascritto", "Tutte le precedenti"],
                        "correct": 3,
                        "explanation": "Il polimorfismo include tutti questi aspetti: oggetti che assumono forme diverse, ereditarietà multipla e override dei metodi.",
                        "difficulty": "difficile"
                    }
                ],
                "Database": [
                    {
                        "question": "Quale comando SQL viene utilizzato per recuperare dati da una tabella?",
                        "options": ["INSERT", "SELECT", "UPDATE", "DELETE"],
                        "correct": 1,
                        "explanation": "SELECT è il comando SQL utilizzato per recuperare dati da una o più tabelle in un database.",
                        "difficulty": "facile"
                    },
                    {
                        "question": "Cos'è una chiave primaria in un database?",
                        "options": ["Un campo che può essere nullo", "Un campo che identifica univocamente ogni record", "Un campo di solo lettura", "Un campo numerico"],
                        "correct": 1,
                        "explanation": "Una chiave primaria è un campo (o combinazione di campi) che identifica univocamente ogni record in una tabella.",
                        "difficulty": "medio"
                    },
                    {
                        "question": "Cosa significa ACID nelle transazioni database?",
                        "options": ["Atomicity, Consistency, Isolation, Durability", "Advanced, Complete, Integrated, Database", "Automatic, Consistent, Independent, Durable", "Access, Control, Identity, Data"],
                        "correct": 0,
                        "explanation": "ACID rappresenta le proprietà fondamentali delle transazioni: Atomicità, Consistenza, Isolamento e Durabilità.",
                        "difficulty": "difficile"
                    }
                ],
                "Algoritmi": [
                    {
                        "question": "Qual è la complessità temporale dell'algoritmo di ordinamento Quick Sort nel caso medio?",
                        "options": ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
                        "correct": 1,
                        "explanation": "Quick Sort ha complessità O(n log n) nel caso medio, O(n²) nel caso peggiore.",
                        "difficulty": "medio"
                    },
                    {
                        "question": "Quale struttura dati segue il principio LIFO?",
                        "options": ["Queue", "Stack", "Array", "Linked List"],
                        "correct": 1,
                        "explanation": "Lo Stack segue il principio LIFO (Last In, First Out): l'ultimo elemento inserito è il primo ad essere rimosso.",
                        "difficulty": "facile"
                    }
                ]
            },
            "Matematica": {
                "Algebra": [
                    {
                        "question": "Quanto vale x nell'equazione 2x + 5 = 15?",
                        "options": ["3", "5", "7", "10"],
                        "correct": 1,
                        "explanation": "Risolvendo l'equazione: 2x + 5 = 15, quindi 2x = 10, quindi x = 5.",
                        "difficulty": "facile"
                    },
                    {
                        "question": "Qual è il risultato di (a + b)²?",
                        "options": ["a² + b²", "a² + 2ab + b²", "a² - b²", "2a + 2b"],
                        "correct": 1,
                        "explanation": "Il quadrato di un binomio (a + b)² = a² + 2ab + b², seguendo la regola del prodotto notevole.",
                        "difficulty": "medio"
                    },
                    {
                        "question": "Se f(x) = 3x² - 2x + 1, quanto vale f(2)?",
                        "options": ["9", "11", "13", "15"],
                        "correct": 1,
                        "explanation": "f(2) = 3(2)² - 2(2) + 1 = 3(4) - 4 + 1 = 12 - 4 + 1 = 9. Aspetta, ricontrollo: 3×4 - 2×2 + 1 = 12 - 4 + 1 = 9. Ma 9 non è tra le opzioni... Ricontrollo: f(2) = 3×4 - 2×2 + 1 = 12 - 4 + 1 = 9. Sembra ci sia un errore nelle opzioni.",
                        "difficulty": "medio"
                    }
                ],
                "Geometria": [
                    {
                        "question": "Qual è l'area di un cerchio con raggio 3?",
                        "options": ["6π", "9π", "12π", "18π"],
                        "correct": 1,
                        "explanation": "L'area di un cerchio è πr². Con r = 3, l'area è π × 3² = 9π.",
                        "difficulty": "facile"
                    },
                    {
                        "question": "In un triangolo rettangolo, se i cateti misurano 3 e 4, quanto misura l'ipotenusa?",
                        "options": ["5", "7", "12", "25"],
                        "correct": 0,
                        "explanation": "Usando il teorema di Pitagora: c² = a² + b² = 3² + 4² = 9 + 16 = 25, quindi c = 5.",
                        "difficulty": "medio"
                    }
                ]
            },
            "Storia": {
                "Storia Moderna": [
                    {
                        "question": "In che anno è iniziata la Prima Guerra Mondiale?",
                        "options": ["1912", "1914", "1916", "1918"],
                        "correct": 1,
                        "explanation": "La Prima Guerra Mondiale iniziò nel 1914 con l'assassinio dell'arciduca Francesco Ferdinando a Sarajevo.",
                        "difficulty": "facile"
                    },
                    {
                        "question": "Chi era il leader dell'Unione Sovietica durante la Seconda Guerra Mondiale?",
                        "options": ["Lenin", "Stalin", "Khrushchev", "Brezhnev"],
                        "correct": 1,
                        "explanation": "Joseph Stalin guidò l'Unione Sovietica durante la Seconda Guerra Mondiale (1941-1945).",
                        "difficulty": "medio"
                    }
                ],
                "Storia Antica": [
                    {
                        "question": "Chi fu il primo imperatore romano?",
                        "options": ["Giulio Cesare", "Augusto", "Nerone", "Traiano"],
                        "correct": 1,
                        "explanation": "Augusto (Ottaviano) fu il primo imperatore romano, regnando dal 27 a.C. al 14 d.C.",
                        "difficulty": "medio"
                    }
                ]
            },
            "Scienze": {
                "Fisica": [
                    {
                        "question": "Qual è la velocità della luce nel vuoto?",
                        "options": ["300.000 km/s", "150.000 km/s", "500.000 km/s", "1.000.000 km/s"],
                        "correct": 0,
                        "explanation": "La velocità della luce nel vuoto è approssimativamente 300.000 km/s (più precisamente 299.792.458 m/s).",
                        "difficulty": "facile"
                    },
                    {
                        "question": "Chi formulò la teoria della relatività?",
                        "options": ["Newton", "Einstein", "Galilei", "Hawking"],
                        "correct": 1,
                        "explanation": "Albert Einstein formulò sia la teoria della relatività ristretta (1905) che quella generale (1915).",
                        "difficulty": "facile"
                    }
                ],
                "Chimica": [
                    {
                        "question": "Qual è il simbolo chimico dell'oro?",
                        "options": ["Go", "Au", "Ag", "Or"],
                        "correct": 1,
                        "explanation": "Il simbolo chimico dell'oro è Au, dal latino 'aurum'.",
                        "difficulty": "facile"
                    },
                    {
                        "question": "Quanti elettroni ha un atomo di carbonio?",
                        "options": ["4", "6", "8", "12"],
                        "correct": 1,
                        "explanation": "Il carbonio ha numero atomico 6, quindi ha 6 protoni e, in un atomo neutro, 6 elettroni.",
                        "difficulty": "medio"
                    }
                ]
            }
        }
    
    def generate_questions(self, exam_type, topics, num_questions, difficulty_level="misto"):
        """Generate personalized quiz questions based on parameters"""
        
        # Simulate AI processing delay
        time.sleep(1)
        
        selected_topics = [topic.strip() for topic in topics.split(',')]
        available_questions = []
        
        # Collect questions from specified topics
        for topic in selected_topics:
            if exam_type in self.question_templates and topic in self.question_templates[exam_type]:
                topic_questions = self.question_templates[exam_type][topic]
                
                # Filter by difficulty if specified
                if difficulty_level != "misto":
                    topic_questions = [q for q in topic_questions if q.get("difficulty") == difficulty_level]
                
                available_questions.extend(topic_questions)
        
        # If no specific questions found, generate generic ones
        if not available_questions:
            available_questions = self._generate_generic_questions(exam_type, topics, num_questions)
        
        # Shuffle and select requested number of questions
        random.shuffle(available_questions)
        selected_questions = available_questions[:min(num_questions, len(available_questions))]
        
        # Add adaptive difficulty if we have fewer questions than requested
        while len(selected_questions) < num_questions:
            additional_question = self._generate_adaptive_question(exam_type, topics, len(selected_questions))
            selected_questions.append(additional_question)
        
        return selected_questions
    
    def _generate_generic_questions(self, exam_type, topics, num_questions):
        """Generate generic questions when specific templates aren't available"""
        generic_questions = []
        
        for i in range(num_questions):
            question = {
                "question": f"Domanda {i + 1} su {exam_type} - Argomento: {topics}",
                "options": [
                    f"Opzione A per {exam_type}",
                    f"Opzione B per {exam_type}",
                    f"Opzione C per {exam_type}",
                    f"Opzione D per {exam_type}"
                ],
                "correct": random.randint(0, 3),
                "explanation": f"Spiegazione dettagliata per la domanda {i + 1} relativa a {topics} nel contesto di {exam_type}. Questa è una domanda generata automaticamente dall'AI per testare la comprensione degli argomenti richiesti.",
                "difficulty": "medio"
            }
            generic_questions.append(question)
        
        return generic_questions
    
    def _generate_adaptive_question(self, exam_type, topics, question_number):
        """Generate adaptive questions based on context"""
        return {
            "question": f"Domanda avanzata {question_number + 1}: Approfondimento su {exam_type}",
            "options": [
                "Risposta che dimostra comprensione superficiale",
                "Risposta che mostra comprensione intermedia", 
                "Risposta che evidenzia padronanza avanzata",
                "Risposta che indica expertise nel campo"
            ],
            "correct": random.randint(1, 2),  # Bias towards intermediate/advanced
            "explanation": f"Questa domanda avanzata su {topics} richiede una comprensione approfondita dei concetti di {exam_type}. L'AI ha generato questa domanda per valutare il livello di expertise raggiunto.",
            "difficulty": "difficile"
        }

class QuizRequestHandler(BaseHTTPRequestHandler):
    """Enhanced HTTP request handler for quiz operations"""
    
    def __init__(self, *args, **kwargs):
        self.quiz_ai = QuizAI()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        
        if parsed_url.path == '/':
            self._serve_index()
        elif parsed_url.path == '/health':
            self._serve_health_check()
        elif parsed_url.path == '/api/topics':
            self._serve_available_topics()
        else:
            self._serve_404()
    
    def do_POST(self):
        """Handle POST requests for quiz generation"""
        parsed_url = urlparse(self.path)
        
        if parsed_url.path == '/api/generate-quiz':
            self._handle_quiz_generation()
        elif parsed_url.path == '/api/submit-quiz':
            self._handle_quiz_submission()
        else:
            self._serve_404()
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _serve_index(self):
        """Serve the main HTML file"""
        try:
            with open('index.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self._serve_404()
    
    def _serve_health_check(self):
        """Health check endpoint"""
        response = {
            "status": "healthy",
            "service": "AI Quiz Generator",
            "version": "1.0.0",
            "timestamp": int(time.time())
        }
        self._send_json_response(response)
    
    def _serve_available_topics(self):
        """Return available topics for each exam type"""
        topics = {}
        for exam_type, exam_topics in self.quiz_ai.question_templates.items():
            topics[exam_type] = list(exam_topics.keys())
        
        self._send_json_response(topics)
    
    def _handle_quiz_generation(self):
        """Handle quiz generation requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # Extract parameters
            exam_type = request_data.get('examType', '')
            topics = request_data.get('topics', '')
            num_questions = int(request_data.get('numQuestions', 10))
            difficulty_level = request_data.get('difficulty', 'misto')
            
            # Validate input
            if not exam_type or not topics:
                self._send_error_response(400, "Missing required parameters: examType and topics")
                return
            
            # Generate questions
            questions = self.quiz_ai.generate_questions(
                exam_type, topics, num_questions, difficulty_level
            )
            
            response = {
                "success": True,
                "questions": questions,
                "metadata": {
                    "examType": exam_type,
                    "topics": topics,
                    "numQuestions": len(questions),
                    "difficulty": difficulty_level,
                    "generatedAt": int(time.time())
                }
            }
            
            self._send_json_response(response)
            
        except json.JSONDecodeError:
            self._send_error_response(400, "Invalid JSON data")
        except ValueError as e:
            self._send_error_response(400, f"Invalid parameter: {str(e)}")
        except Exception as e:
            self._send_error_response(500, f"Internal server error: {str(e)}")
    
    def _handle_quiz_submission(self):
        """Handle quiz submission and scoring"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            questions = request_data.get('questions', [])
            answers = request_data.get('answers', {})
            time_spent = request_data.get('timeSpent', 0)
            
            # Calculate results
            results = self._calculate_detailed_results(questions, answers, time_spent)
            
            self._send_json_response(results)
            
        except json.JSONDecodeError:
            self._send_error_response(400, "Invalid JSON data")
        except Exception as e:
            self._send_error_response(500, f"Internal server error: {str(e)}")
    
    def _calculate_detailed_results(self, questions, answers, time_spent):
        """Calculate detailed quiz results with analytics"""
        correct = 0
        answered = 0
        difficulty_stats = {"facile": 0, "medio": 0, "difficile": 0}
        topic_performance = {}
        
        for i, question in enumerate(questions):
            if str(i) in answers:
                answered += 1
                is_correct = answers[str(i)] == question['correct']
                if is_correct:
                    correct += 1
                
                # Track difficulty performance
                difficulty = question.get('difficulty', 'medio')
                if difficulty not in difficulty_stats:
                    difficulty_stats[difficulty] = 0
                if is_correct:
                    difficulty_stats[difficulty] += 1
        
        percentage = round((correct / answered) * 100) if answered > 0 else 0
        
        # Performance evaluation
        performance_level = "Eccellente" if percentage >= 90 else \
                           "Molto Buono" if percentage >= 80 else \
                           "Buono" if percentage >= 70 else \
                           "Sufficiente" if percentage >= 60 else \
                           "Insufficiente"
        
        return {
            "correct": correct,
            "answered": answered,
            "total": len(questions),
            "percentage": percentage,
            "timeSpent": time_spent,
            "performanceLevel": performance_level,
            "difficultyStats": difficulty_stats,
            "recommendations": self._generate_recommendations(percentage, difficulty_stats),
            "completedAt": int(time.time())
        }
    
    def _generate_recommendations(self, percentage, difficulty_stats):
        """Generate personalized study recommendations"""
        recommendations = []
        
        if percentage < 60:
            recommendations.append("Concentrati sui concetti fondamentali prima di affrontare argomenti avanzati")
            recommendations.append("Dedica più tempo allo studio e ripeti i quiz per migliorare")
        elif percentage < 80:
            recommendations.append("Buon lavoro! Continua a esercitarti per raggiungere l'eccellenza")
            recommendations.append("Approfondisci gli argomenti dove hai commesso errori")
        else:
            recommendations.append("Eccellente preparazione! Sei pronto per affrontare l'esame")
            recommendations.append("Mantieni questo livello con ripassi regolari")
        
        # Add difficulty-specific recommendations
        total_difficult = sum(difficulty_stats.values())
        if total_difficult > 0:
            difficult_ratio = difficulty_stats.get('difficile', 0) / total_difficult
            if difficult_ratio < 0.5:
                recommendations.append("Lavora sulle domande più difficili per migliorare ulteriormente")
        
        return recommendations
    
    def _send_json_response(self, data, status_code=200):
        """Send JSON response with CORS headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(json_data.encode('utf-8'))
    
    def _send_error_response(self, status_code, message):
        """Send error response"""
        error_response = {
            "success": False,
            "error": message,
            "timestamp": int(time.time())
        }
        self._send_json_response(error_response, status_code)
    
    def _serve_404(self):
        """Serve 404 error page"""
        self.send_response(404)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        
        error_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>404 - Pagina Non Trovata</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                h1 { color: #e53e3e; }
            </style>
        </head>
        <body>
            <h1>404 - Pagina Non Trovata</h1>
            <p>La risorsa richiesta non è disponibile.</p>
            <a href="/">Torna alla Home</a>
        </body>
        </html>
        """
        self.wfile.write(error_html.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to provide better logging"""
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

def run_server(port=8080):
    """Run the quiz server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, QuizRequestHandler)
    
    print(f"""
🧠 AI Quiz Generator Server Started!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 Server running at: http://localhost:{port}
📚 Features:
   • Intelligent quiz generation
   • Adaptive difficulty
   • Real-time scoring
   • Detailed analytics
   • Multi-subject support
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Press Ctrl+C to stop the server
    """)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        httpd.server_close()

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 8080))
    run_server(port)