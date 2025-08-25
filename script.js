// Stato globale dell'applicazione
let appState = {
    currentScreen: 'setup',
    quizConfig: {},
    currentQuiz: null,
    currentQuestionIndex: 0,
    userAnswers: [],
    score: 0,
    timeRemaining: 0,
    timerInterval: null,
    startTime: null
};

// Database simulato di domande per diversi argomenti
const questionDatabase = {
    matematica: [
        {
            question: "Qual è il risultato di 2³ + 3²?",
            options: ["17", "13", "15", "11"],
            correct: 0,
            explanation: "2³ = 8 e 3² = 9, quindi 8 + 9 = 17"
        },
        {
            question: "Quale è la derivata di x²?",
            options: ["x", "2x", "x²", "2"],
            correct: 1,
            explanation: "La derivata di x² è 2x secondo la regola di derivazione delle potenze"
        },
        {
            question: "Quanto vale sin(90°)?",
            options: ["0", "1", "√2/2", "-1"],
            correct: 1,
            explanation: "Il seno di 90° (π/2 radianti) è uguale a 1"
        }
    ],
    fisica: [
        {
            question: "Qual è la formula dell'energia cinetica?",
            options: ["E = mc²", "E = ½mv²", "E = mgh", "E = Pt"],
            correct: 1,
            explanation: "L'energia cinetica è data da E = ½mv², dove m è la massa e v è la velocità"
        },
        {
            question: "Qual è l'unità di misura della forza nel Sistema Internazionale?",
            options: ["Joule", "Watt", "Newton", "Pascal"],
            correct: 2,
            explanation: "Il Newton (N) è l'unità di misura della forza nel Sistema Internazionale"
        }
    ],
    chimica: [
        {
            question: "Qual è il simbolo chimico dell'oro?",
            options: ["Go", "Au", "Ag", "Or"],
            correct: 1,
            explanation: "Il simbolo chimico dell'oro è Au, dal latino 'aurum'"
        },
        {
            question: "Quanti elettroni può contenere il primo guscio elettronico?",
            options: ["2", "8", "18", "32"],
            correct: 0,
            explanation: "Il primo guscio elettronico (K) può contenere al massimo 2 elettroni"
        }
    ],
    storia: [
        {
            question: "In che anno è caduto il Muro di Berlino?",
            options: ["1987", "1989", "1991", "1993"],
            correct: 1,
            explanation: "Il Muro di Berlino è caduto il 9 novembre 1989"
        },
        {
            question: "Chi era l'imperatore romano durante la nascita di Gesù?",
            options: ["Giulio Cesare", "Augusto", "Nerone", "Traiano"],
            correct: 1,
            explanation: "Augusto (Ottaviano) era l'imperatore romano al tempo della nascita di Gesù"
        }
    ],
    geografia: [
        {
            question: "Qual è la capitale dell'Australia?",
            options: ["Sydney", "Melbourne", "Canberra", "Perth"],
            correct: 2,
            explanation: "Canberra è la capitale dell'Australia, non Sydney come molti pensano"
        },
        {
            question: "Quale è il fiume più lungo del mondo?",
            options: ["Nilo", "Amazzonia", "Yangtze", "Mississippi"],
            correct: 0,
            explanation: "Il Nilo, con i suoi 6.650 km, è considerato il fiume più lungo del mondo"
        }
    ],
    inglese: [
        {
            question: "Qual è il past participle di 'go'?",
            options: ["went", "gone", "going", "goes"],
            correct: 1,
            explanation: "Il past participle di 'go' è 'gone' (go-went-gone)"
        },
        {
            question: "Cosa significa 'serendipity'?",
            options: ["Tristezza profonda", "Scoperta casuale e piacevole", "Paura del buio", "Amore per la natura"],
            correct: 1,
            explanation: "'Serendipity' significa fare una scoperta piacevole e inaspettata per caso"
        }
    ],
    informatica: [
        {
            question: "Cosa significa HTML?",
            options: ["High Text Markup Language", "HyperText Markup Language", "Home Tool Markup Language", "Hyperlink Text Markup Language"],
            correct: 1,
            explanation: "HTML sta per HyperText Markup Language, il linguaggio di markup per creare pagine web"
        },
        {
            question: "Quale di questi è un linguaggio di programmazione?",
            options: ["HTML", "CSS", "Python", "HTTP"],
            correct: 2,
            explanation: "Python è un linguaggio di programmazione, mentre HTML e CSS sono linguaggi di markup e stile"
        }
    ]
};

// Inizializzazione dell'app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    setupEventListeners();
    updateRangeDisplays();
    showScreen('setup');
}

function setupEventListeners() {
    // Setup screen
    document.getElementById('num-questions').addEventListener('input', updateQuestionCount);
    document.getElementById('time-limit').addEventListener('input', updateTimeDisplay);
    document.getElementById('generate-quiz').addEventListener('click', generateQuiz);
    
    // Quiz screen
    document.getElementById('prev-question').addEventListener('click', previousQuestion);
    document.getElementById('next-question').addEventListener('click', nextQuestion);
    document.getElementById('finish-quiz').addEventListener('click', finishQuiz);
    
    // Results screen
    document.getElementById('restart-quiz').addEventListener('click', restartQuiz);
    document.getElementById('review-answers').addEventListener('click', toggleAnswerReview);
}

function updateRangeDisplays() {
    updateQuestionCount();
    updateTimeDisplay();
}

function updateQuestionCount() {
    const numQuestions = document.getElementById('num-questions').value;
    document.getElementById('question-count').textContent = numQuestions;
}

function updateTimeDisplay() {
    const timeLimit = document.getElementById('time-limit').value;
    document.getElementById('time-display').textContent = timeLimit;
}

function showScreen(screenName) {
    // Nasconde tutti gli schermi
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    
    // Mostra lo schermo richiesto
    document.getElementById(screenName + '-screen').classList.add('active');
    appState.currentScreen = screenName;
}

async function generateQuiz() {
    // Validazione input
    const examType = document.getElementById('exam-type').value;
    const topics = document.getElementById('topics').value.trim();
    const numQuestions = parseInt(document.getElementById('num-questions').value);
    const difficulty = document.getElementById('difficulty').value;
    const timeLimit = parseInt(document.getElementById('time-limit').value);
    
    if (!examType || !topics) {
        alert('Per favore compila tutti i campi obbligatori');
        return;
    }
    
    // Salva configurazione
    appState.quizConfig = {
        examType,
        topics: topics.split(',').map(t => t.trim().toLowerCase()),
        numQuestions,
        difficulty,
        timeLimit
    };
    
    // Mostra schermata di caricamento
    showScreen('loading');
    
    // Simula generazione AI
    await simulateAIGeneration();
    
    // Genera il quiz
    const quiz = await generateQuizQuestions();
    appState.currentQuiz = quiz;
    appState.currentQuestionIndex = 0;
    appState.userAnswers = new Array(quiz.length).fill(null);
    appState.score = 0;
    appState.timeRemaining = timeLimit * 60; // Converti in secondi
    appState.startTime = Date.now();
    
    // Inizia il quiz
    startQuiz();
}

async function simulateAIGeneration() {
    return new Promise(resolve => {
        let progress = 0;
        const progressBar = document.querySelector('.progress-bar');
        
        const interval = setInterval(() => {
            progress += Math.random() * 15 + 5;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                resolve();
            }
            progressBar.style.width = progress + '%';
        }, 200);
    });
}

async function generateQuizQuestions() {
    const { topics, numQuestions, difficulty } = appState.quizConfig;
    const availableQuestions = [];
    
    // Raccoglie domande dai topic richiesti
    topics.forEach(topic => {
        if (questionDatabase[topic]) {
            availableQuestions.push(...questionDatabase[topic]);
        }
    });
    
    // Se non ci sono abbastanza domande, genera domande generiche
    if (availableQuestions.length < numQuestions) {
        availableQuestions.push(...generateGenericQuestions(numQuestions - availableQuestions.length, topics));
    }
    
    // Mescola e seleziona il numero richiesto di domande
    const shuffled = shuffleArray([...availableQuestions]);
    const selectedQuestions = shuffled.slice(0, numQuestions);
    
    // Applica difficoltà
    return applyDifficulty(selectedQuestions, difficulty);
}

function generateGenericQuestions(count, topics) {
    const genericQuestions = [];
    const topicsText = topics.join(', ');
    
    for (let i = 0; i < count; i++) {
        genericQuestions.push({
            question: `Domanda generata per ${topicsText} - ${i + 1}`,
            options: [
                `Opzione A per ${topicsText}`,
                `Opzione B per ${topicsText}`,
                `Opzione C per ${topicsText}`,
                `Opzione D per ${topicsText}`
            ],
            correct: Math.floor(Math.random() * 4),
            explanation: `Questa è una spiegazione generata automaticamente per una domanda su ${topicsText}. In un'implementazione reale, l'AI genererebbe contenuti specifici e accurati.`
        });
    }
    
    return genericQuestions;
}

function applyDifficulty(questions, difficulty) {
    // In una implementazione reale, questo modificherebbe la complessità delle domande
    return questions.map(q => ({
        ...q,
        difficulty: difficulty
    }));
}

function shuffleArray(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

function startQuiz() {
    showScreen('quiz');
    displayCurrentQuestion();
    startTimer();
    updateQuizProgress();
}

function displayCurrentQuestion() {
    const question = appState.currentQuiz[appState.currentQuestionIndex];
    const totalQuestions = appState.currentQuiz.length;
    const currentNum = appState.currentQuestionIndex + 1;
    
    // Aggiorna header
    document.getElementById('current-question').textContent = currentNum;
    document.getElementById('total-questions').textContent = totalQuestions;
    document.getElementById('current-score').textContent = appState.score;
    
    // Aggiorna domanda
    document.getElementById('q-number').textContent = currentNum;
    document.getElementById('question-text').textContent = question.question;
    
    // Genera opzioni di risposta
    const answersContainer = document.getElementById('answers-container');
    answersContainer.innerHTML = '';
    
    question.options.forEach((option, index) => {
        const answerDiv = document.createElement('div');
        answerDiv.className = 'answer-option';
        answerDiv.dataset.index = index;
        
        const selectedAnswer = appState.userAnswers[appState.currentQuestionIndex];
        if (selectedAnswer === index) {
            answerDiv.classList.add('selected');
        }
        
        answerDiv.innerHTML = `
            <div class="answer-letter">${String.fromCharCode(65 + index)}</div>
            <div class="answer-text">${option}</div>
        `;
        
        answerDiv.addEventListener('click', () => selectAnswer(index));
        answersContainer.appendChild(answerDiv);
    });
    
    // Aggiorna pulsanti navigazione
    updateNavigationButtons();
}

function selectAnswer(answerIndex) {
    // Rimuovi selezione precedente
    document.querySelectorAll('.answer-option').forEach(option => {
        option.classList.remove('selected');
    });
    
    // Seleziona nuova risposta
    document.querySelector(`[data-index="${answerIndex}"]`).classList.add('selected');
    appState.userAnswers[appState.currentQuestionIndex] = answerIndex;
    
    // Abilita pulsante next
    document.getElementById('next-question').disabled = false;
    
    // Calcola punteggio dinamico
    updateScore();
}

function updateScore() {
    const question = appState.currentQuiz[appState.currentQuestionIndex];
    const userAnswer = appState.userAnswers[appState.currentQuestionIndex];
    const timeElapsed = (Date.now() - appState.startTime) / 1000;
    const timePerQuestion = appState.quizConfig.timeLimit * 60 / appState.currentQuiz.length;
    
    if (userAnswer === question.correct) {
        // Punteggio base per risposta corretta
        let points = 100;
        
        // Bonus per velocità (max 50 punti extra)
        const questionStartTime = timeElapsed - (appState.currentQuestionIndex * timePerQuestion);
        const speedBonus = Math.max(0, 50 - (questionStartTime / timePerQuestion) * 50);
        points += speedBonus;
        
        // Bonus difficoltà
        const difficultyMultiplier = {
            'facile': 1,
            'medio': 1.2,
            'difficile': 1.5,
            'misto': 1.3
        };
        points *= difficultyMultiplier[appState.quizConfig.difficulty] || 1;
        
        appState.score += Math.round(points);
    }
    
    document.getElementById('current-score').textContent = appState.score;
}

function updateNavigationButtons() {
    const prevBtn = document.getElementById('prev-question');
    const nextBtn = document.getElementById('next-question');
    const finishBtn = document.getElementById('finish-quiz');
    
    // Pulsante precedente
    prevBtn.disabled = appState.currentQuestionIndex === 0;
    
    // Pulsante successivo
    const hasAnswer = appState.userAnswers[appState.currentQuestionIndex] !== null;
    nextBtn.disabled = !hasAnswer;
    
    // Pulsante fine quiz
    const isLastQuestion = appState.currentQuestionIndex === appState.currentQuiz.length - 1;
    if (isLastQuestion) {
        nextBtn.style.display = 'none';
        finishBtn.style.display = 'inline-flex';
        finishBtn.disabled = !hasAnswer;
    } else {
        nextBtn.style.display = 'inline-flex';
        finishBtn.style.display = 'none';
    }
}

function previousQuestion() {
    if (appState.currentQuestionIndex > 0) {
        appState.currentQuestionIndex--;
        displayCurrentQuestion();
        updateQuizProgress();
    }
}

function nextQuestion() {
    if (appState.currentQuestionIndex < appState.currentQuiz.length - 1) {
        appState.currentQuestionIndex++;
        displayCurrentQuestion();
        updateQuizProgress();
    }
}

function updateQuizProgress() {
    const progress = ((appState.currentQuestionIndex + 1) / appState.currentQuiz.length) * 100;
    document.getElementById('quiz-progress').style.width = progress + '%';
}

function startTimer() {
    updateTimerDisplay();
    
    appState.timerInterval = setInterval(() => {
        appState.timeRemaining--;
        updateTimerDisplay();
        
        if (appState.timeRemaining <= 0) {
            clearInterval(appState.timerInterval);
            finishQuiz();
        }
    }, 1000);
}

function updateTimerDisplay() {
    const minutes = Math.floor(appState.timeRemaining / 60);
    const seconds = appState.timeRemaining % 60;
    const timeString = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    
    const timerElement = document.getElementById('time-remaining');
    timerElement.textContent = timeString;
    
    // Cambia colore in base al tempo rimanente
    const timerContainer = timerElement.parentElement;
    if (appState.timeRemaining <= 60) {
        timerContainer.classList.add('danger');
    } else if (appState.timeRemaining <= 300) {
        timerContainer.classList.add('warning');
    }
}

function finishQuiz() {
    clearInterval(appState.timerInterval);
    calculateFinalResults();
    showResults();
}

function calculateFinalResults() {
    let correctAnswers = 0;
    
    appState.currentQuiz.forEach((question, index) => {
        if (appState.userAnswers[index] === question.correct) {
            correctAnswers++;
        }
    });
    
    const totalQuestions = appState.currentQuiz.length;
    const percentage = Math.round((correctAnswers / totalQuestions) * 100);
    
    appState.results = {
        correctAnswers,
        totalQuestions,
        percentage,
        finalScore: appState.score,
        timeUsed: appState.quizConfig.timeLimit * 60 - appState.timeRemaining
    };
}

function showResults() {
    showScreen('results');
    
    const { correctAnswers, totalQuestions, percentage, finalScore } = appState.results;
    
    // Aggiorna statistiche principali
    document.getElementById('final-percentage').textContent = percentage;
    document.getElementById('correct-answers').textContent = correctAnswers;
    document.getElementById('total-answers').textContent = totalQuestions;
    document.getElementById('final-points').textContent = finalScore;
    
    // Genera feedback prestazione
    generatePerformanceFeedback();
    
    // Genera revisione domande
    generateQuestionReview();
    
    // Anima il punteggio
    animateScore(percentage);
}

function generatePerformanceFeedback() {
    const percentage = appState.results.percentage;
    let feedback = '';
    let color = '';
    
    if (percentage >= 90) {
        feedback = '🎉 Eccellente! Hai dimostrato una conoscenza approfondita degli argomenti. Continua così!';
        color = '#28a745';
    } else if (percentage >= 75) {
        feedback = '👍 Molto bene! Hai una buona comprensione degli argomenti, con alcuni aspetti da approfondire.';
        color = '#20c997';
    } else if (percentage >= 60) {
        feedback = '📚 Discreto. Hai le basi ma ci sono diversi argomenti che potrebbero beneficiare di ulteriore studio.';
        color = '#ffc107';
    } else if (percentage >= 40) {
        feedback = '📖 Sufficiente. È consigliabile rivedere gli argomenti e praticare di più prima del prossimo tentativo.';
        color = '#fd7e14';
    } else {
        feedback = '📝 Necessario maggiore studio. Ti consiglio di rivedere attentamente tutti gli argomenti prima di riprovare.';
        color = '#dc3545';
    }
    
    const feedbackElement = document.getElementById('performance-feedback');
    feedbackElement.textContent = feedback;
    feedbackElement.style.borderLeft = `4px solid ${color}`;
}

function generateQuestionReview() {
    const reviewContainer = document.getElementById('questions-review');
    reviewContainer.innerHTML = '';
    
    appState.currentQuiz.forEach((question, index) => {
        const userAnswer = appState.userAnswers[index];
        const isCorrect = userAnswer === question.correct;
        
        const reviewDiv = document.createElement('div');
        reviewDiv.className = `question-review ${isCorrect ? 'correct' : 'incorrect'}`;
        
        let userAnswerText = userAnswer !== null ? question.options[userAnswer] : 'Nessuna risposta';
        let correctAnswerText = question.options[question.correct];
        
        reviewDiv.innerHTML = `
            <div class="review-question">
                <strong>Domanda ${index + 1}:</strong> ${question.question}
            </div>
            <div class="review-answer user-answer">
                <strong>La tua risposta:</strong> ${userAnswerText} ${isCorrect ? '✓' : '✗'}
            </div>
            ${!isCorrect ? `
                <div class="review-answer correct-answer">
                    <strong>Risposta corretta:</strong> ${correctAnswerText} ✓
                </div>
            ` : ''}
            <div class="review-explanation">
                <strong>Spiegazione:</strong> ${question.explanation}
            </div>
        `;
        
        reviewContainer.appendChild(reviewDiv);
    });
}

function animateScore(targetPercentage) {
    const scoreElement = document.getElementById('final-percentage');
    let currentPercentage = 0;
    const increment = targetPercentage / 50; // 50 frame per l'animazione
    
    const animation = setInterval(() => {
        currentPercentage += increment;
        if (currentPercentage >= targetPercentage) {
            currentPercentage = targetPercentage;
            clearInterval(animation);
        }
        scoreElement.textContent = Math.round(currentPercentage);
    }, 20);
}

function restartQuiz() {
    // Reset stato
    appState.currentQuestionIndex = 0;
    appState.userAnswers = [];
    appState.score = 0;
    appState.timeRemaining = 0;
    appState.currentQuiz = null;
    
    if (appState.timerInterval) {
        clearInterval(appState.timerInterval);
    }
    
    // Torna alla configurazione
    showScreen('setup');
}

function toggleAnswerReview() {
    const reviewContainer = document.getElementById('questions-review');
    const button = document.getElementById('review-answers');
    
    if (reviewContainer.style.display === 'none') {
        reviewContainer.style.display = 'block';
        button.innerHTML = '<i class="fas fa-eye-slash"></i> Nascondi Risposte';
    } else {
        reviewContainer.style.display = 'none';
        button.innerHTML = '<i class="fas fa-eye"></i> Rivedi Risposte';
    }
}

// Gestione eventi tastiera
document.addEventListener('keydown', function(e) {
    if (appState.currentScreen === 'quiz') {
        switch(e.key) {
            case 'ArrowLeft':
                if (!document.getElementById('prev-question').disabled) {
                    previousQuestion();
                }
                break;
            case 'ArrowRight':
                if (!document.getElementById('next-question').disabled) {
                    nextQuestion();
                } else if (!document.getElementById('finish-quiz').disabled) {
                    finishQuiz();
                }
                break;
            case '1':
            case '2':
            case '3':
            case '4':
                const answerIndex = parseInt(e.key) - 1;
                if (answerIndex < appState.currentQuiz[appState.currentQuestionIndex].options.length) {
                    selectAnswer(answerIndex);
                }
                break;
        }
    }
});

// Gestione visibilità pagina (pausa timer quando la pagina non è visibile)
document.addEventListener('visibilitychange', function() {
    if (appState.currentScreen === 'quiz' && appState.timerInterval) {
        if (document.hidden) {
            clearInterval(appState.timerInterval);
        } else {
            startTimer();
        }
    }
});

// Prevenzione chiusura accidentale durante il quiz
window.addEventListener('beforeunload', function(e) {
    if (appState.currentScreen === 'quiz') {
        e.preventDefault();
        e.returnValue = 'Sei sicuro di voler uscire? Il tuo progresso andrà perso.';
        return e.returnValue;
    }
});