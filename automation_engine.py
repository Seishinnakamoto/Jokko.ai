#!/usr/bin/env python3
"""
Automation Engine - Make.com Alternative
Handles automated workflows, integrations, and data processing

Features:
- Workflow automation
- Email notifications
- Database logging
- Webhook triggers
- Scheduled tasks
- Integration with external services
"""

import asyncio
import json
import logging
import os
import smtplib
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import schedule
import threading
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TriggerType(Enum):
    """Types of automation triggers"""
    WEBHOOK = "webhook"
    SCHEDULE = "schedule"
    EMAIL = "email"
    DATABASE = "database"
    API_CALL = "api_call"

class ActionType(Enum):
    """Types of automation actions"""
    SEND_EMAIL = "send_email"
    LOG_DATABASE = "log_database"
    API_REQUEST = "api_request"
    PROCESS_CHAT = "process_chat"
    TRANSLATE_TEXT = "translate_text"
    NOTIFY_ADMIN = "notify_admin"

@dataclass
class AutomationTrigger:
    """Automation trigger configuration"""
    trigger_id: str
    trigger_type: TriggerType
    config: Dict[str, Any]
    enabled: bool = True

@dataclass
class AutomationAction:
    """Automation action configuration"""
    action_id: str
    action_type: ActionType
    config: Dict[str, Any]
    enabled: bool = True

@dataclass
class Workflow:
    """Complete automation workflow"""
    workflow_id: str
    name: str
    description: str
    trigger: AutomationTrigger
    actions: List[AutomationAction]
    enabled: bool = True
    created_at: datetime = None
    last_run: datetime = None

@dataclass
class WorkflowExecution:
    """Workflow execution record"""
    execution_id: str
    workflow_id: str
    trigger_data: Dict[str, Any]
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    results: Dict[str, Any] = None

class DatabaseManager:
    """SQLite database manager for automation data"""
    
    def __init__(self, db_path: str = "automation.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Chat logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                language TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                processing_time REAL,
                session_id TEXT
            )
        ''')
        
        # Workflow executions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflow_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id TEXT UNIQUE NOT NULL,
                workflow_id TEXT NOT NULL,
                trigger_data TEXT,
                status TEXT NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                error_message TEXT,
                results TEXT
            )
        ''')
        
        # User analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                language TEXT NOT NULL,
                message_count INTEGER DEFAULT 1,
                last_interaction DATETIME DEFAULT CURRENT_TIMESTAMP,
                topics TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_chat(self, user_id: str, message: str, response: str, language: str, 
                 processing_time: float, session_id: str = None):
        """Log chat interaction"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chat_logs 
            (user_id, message, response, language, processing_time, session_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, message, response, language, processing_time, session_id))
        
        conn.commit()
        conn.close()
    
    def log_workflow_execution(self, execution: WorkflowExecution):
        """Log workflow execution"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO workflow_executions 
            (execution_id, workflow_id, trigger_data, status, start_time, end_time, error_message, results)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            execution.execution_id,
            execution.workflow_id,
            json.dumps(execution.trigger_data),
            execution.status,
            execution.start_time,
            execution.end_time,
            execution.error_message,
            json.dumps(execution.results) if execution.results else None
        ))
        
        conn.commit()
        conn.close()
    
    def update_user_analytics(self, user_id: str, language: str, topics: List[str] = None):
        """Update user analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT * FROM user_analytics WHERE user_id = ?', (user_id,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE user_analytics 
                SET message_count = message_count + 1, 
                    last_interaction = CURRENT_TIMESTAMP,
                    language = ?,
                    topics = ?
                WHERE user_id = ?
            ''', (language, json.dumps(topics) if topics else None, user_id))
        else:
            cursor.execute('''
                INSERT INTO user_analytics (user_id, language, topics)
                VALUES (?, ?, ?)
            ''', (user_id, language, json.dumps(topics) if topics else None))
        
        conn.commit()
        conn.close()
    
    def get_chat_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get chat statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_date = datetime.now() - timedelta(days=days)
        
        # Total messages
        cursor.execute('SELECT COUNT(*) FROM chat_logs WHERE timestamp > ?', (since_date,))
        total_messages = cursor.fetchone()[0]
        
        # Messages by language
        cursor.execute('''
            SELECT language, COUNT(*) FROM chat_logs 
            WHERE timestamp > ? 
            GROUP BY language
        ''', (since_date,))
        by_language = dict(cursor.fetchall())
        
        # Unique users
        cursor.execute('SELECT COUNT(DISTINCT user_id) FROM chat_logs WHERE timestamp > ?', (since_date,))
        unique_users = cursor.fetchone()[0]
        
        # Average processing time
        cursor.execute('SELECT AVG(processing_time) FROM chat_logs WHERE timestamp > ?', (since_date,))
        avg_processing_time = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_messages': total_messages,
            'unique_users': unique_users,
            'messages_by_language': by_language,
            'average_processing_time': round(avg_processing_time, 2),
            'period_days': days
        }

class EmailManager:
    """Email notification manager"""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    async def send_email(self, to_email: str, subject: str, body: str, html_body: str = None):
        """Send email notification"""
        try:
            msg = MimeMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.username
            msg['To'] = to_email
            
            # Text part
            text_part = MimeText(body, 'plain')
            msg.attach(text_part)
            
            # HTML part if provided
            if html_body:
                html_part = MimeText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Email sending failed: {str(e)}")
            return False
    
    async def send_admin_notification(self, subject: str, message: str, data: Dict[str, Any] = None):
        """Send notification to admin"""
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        
        body = f"""
        Notification: {subject}
        
        Message: {message}
        
        Timestamp: {datetime.now().isoformat()}
        """
        
        if data:
            body += f"\nData: {json.dumps(data, indent=2)}"
        
        html_body = f"""
        <html>
        <body>
            <h2>🤖 Chatbot Notification</h2>
            <h3>{subject}</h3>
            <p>{message}</p>
            <p><strong>Timestamp:</strong> {datetime.now().isoformat()}</p>
            {f'<pre>{json.dumps(data, indent=2)}</pre>' if data else ''}
        </body>
        </html>
        """
        
        await self.send_email(admin_email, f"[Chatbot] {subject}", body, html_body)

class AutomationEngine:
    """Main automation engine - Make.com alternative"""
    
    def __init__(self, db_manager: DatabaseManager, email_manager: EmailManager = None):
        self.db_manager = db_manager
        self.email_manager = email_manager
        self.workflows: Dict[str, Workflow] = {}
        self.running = False
        self.scheduler_thread = None
        
        # Setup default workflows
        self.setup_default_workflows()
    
    def setup_default_workflows(self):
        """Setup default automation workflows"""
        
        # Workflow 1: Log all chat interactions
        chat_logging_workflow = Workflow(
            workflow_id="chat_logging",
            name="Chat Interaction Logging",
            description="Log all chat interactions to database",
            trigger=AutomationTrigger(
                trigger_id="chat_trigger",
                trigger_type=TriggerType.WEBHOOK,
                config={"endpoint": "/webhook/chat"}
            ),
            actions=[
                AutomationAction(
                    action_id="log_chat",
                    action_type=ActionType.LOG_DATABASE,
                    config={"table": "chat_logs"}
                )
            ]
        )
        
        # Workflow 2: Daily statistics email
        daily_stats_workflow = Workflow(
            workflow_id="daily_stats",
            name="Daily Statistics Report",
            description="Send daily usage statistics to admin",
            trigger=AutomationTrigger(
                trigger_id="daily_schedule",
                trigger_type=TriggerType.SCHEDULE,
                config={"schedule": "daily", "time": "09:00"}
            ),
            actions=[
                AutomationAction(
                    action_id="send_stats_email",
                    action_type=ActionType.SEND_EMAIL,
                    config={"template": "daily_stats"}
                )
            ]
        )
        
        # Workflow 3: Error notification
        error_notification_workflow = Workflow(
            workflow_id="error_notification",
            name="Error Notification",
            description="Notify admin of system errors",
            trigger=AutomationTrigger(
                trigger_id="error_trigger",
                trigger_type=TriggerType.API_CALL,
                config={"endpoint": "/api/error"}
            ),
            actions=[
                AutomationAction(
                    action_id="notify_admin",
                    action_type=ActionType.NOTIFY_ADMIN,
                    config={"priority": "high"}
                )
            ]
        )
        
        # Register workflows
        self.workflows = {
            "chat_logging": chat_logging_workflow,
            "daily_stats": daily_stats_workflow,
            "error_notification": error_notification_workflow
        }
    
    def add_workflow(self, workflow: Workflow):
        """Add a new workflow"""
        self.workflows[workflow.workflow_id] = workflow
        logger.info(f"Added workflow: {workflow.name}")
    
    def remove_workflow(self, workflow_id: str):
        """Remove a workflow"""
        if workflow_id in self.workflows:
            del self.workflows[workflow_id]
            logger.info(f"Removed workflow: {workflow_id}")
    
    async def execute_workflow(self, workflow_id: str, trigger_data: Dict[str, Any]) -> WorkflowExecution:
        """Execute a specific workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        if not workflow.enabled:
            logger.info(f"Workflow {workflow_id} is disabled, skipping")
            return None
        
        execution_id = f"{workflow_id}_{int(time.time())}"
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            trigger_data=trigger_data,
            status="running",
            start_time=datetime.now()
        )
        
        try:
            logger.info(f"Executing workflow: {workflow.name}")
            
            results = {}
            for action in workflow.actions:
                if not action.enabled:
                    continue
                
                action_result = await self.execute_action(action, trigger_data)
                results[action.action_id] = action_result
            
            execution.status = "completed"
            execution.end_time = datetime.now()
            execution.results = results
            
            # Update workflow last run time
            workflow.last_run = datetime.now()
            
            logger.info(f"Workflow {workflow.name} completed successfully")
            
        except Exception as e:
            execution.status = "failed"
            execution.end_time = datetime.now()
            execution.error_message = str(e)
            
            logger.error(f"Workflow {workflow.name} failed: {str(e)}")
        
        # Log execution
        self.db_manager.log_workflow_execution(execution)
        
        return execution
    
    async def execute_action(self, action: AutomationAction, trigger_data: Dict[str, Any]) -> Any:
        """Execute a specific action"""
        
        if action.action_type == ActionType.LOG_DATABASE:
            return await self.action_log_database(action, trigger_data)
        
        elif action.action_type == ActionType.SEND_EMAIL:
            return await self.action_send_email(action, trigger_data)
        
        elif action.action_type == ActionType.NOTIFY_ADMIN:
            return await self.action_notify_admin(action, trigger_data)
        
        elif action.action_type == ActionType.API_REQUEST:
            return await self.action_api_request(action, trigger_data)
        
        else:
            logger.warning(f"Unknown action type: {action.action_type}")
            return None
    
    async def action_log_database(self, action: AutomationAction, trigger_data: Dict[str, Any]):
        """Log data to database"""
        if 'chat_data' in trigger_data:
            chat_data = trigger_data['chat_data']
            self.db_manager.log_chat(
                user_id=chat_data.get('user_id'),
                message=chat_data.get('message'),
                response=chat_data.get('response'),
                language=chat_data.get('language'),
                processing_time=chat_data.get('processing_time'),
                session_id=chat_data.get('session_id')
            )
            return "Chat logged successfully"
        return "No chat data to log"
    
    async def action_send_email(self, action: AutomationAction, trigger_data: Dict[str, Any]):
        """Send email action"""
        if not self.email_manager:
            return "Email manager not configured"
        
        template = action.config.get('template')
        
        if template == 'daily_stats':
            stats = self.db_manager.get_chat_stats(days=1)
            subject = "Daily Chatbot Statistics"
            body = f"""
            Daily Statistics Report:
            
            Total Messages: {stats['total_messages']}
            Unique Users: {stats['unique_users']}
            Average Processing Time: {stats['average_processing_time']}s
            
            Messages by Language:
            {json.dumps(stats['messages_by_language'], indent=2)}
            """
            
            admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
            await self.email_manager.send_email(admin_email, subject, body)
            return "Daily stats email sent"
        
        return "Unknown email template"
    
    async def action_notify_admin(self, action: AutomationAction, trigger_data: Dict[str, Any]):
        """Notify admin action"""
        if not self.email_manager:
            return "Email manager not configured"
        
        subject = trigger_data.get('subject', 'System Notification')
        message = trigger_data.get('message', 'No message provided')
        
        await self.email_manager.send_admin_notification(subject, message, trigger_data)
        return "Admin notification sent"
    
    async def action_api_request(self, action: AutomationAction, trigger_data: Dict[str, Any]):
        """Make API request action"""
        url = action.config.get('url')
        method = action.config.get('method', 'POST')
        headers = action.config.get('headers', {})
        
        if not url:
            return "No URL specified"
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, json=trigger_data, headers=headers) as response:
                result = await response.text()
                return f"API request completed: {response.status}"
    
    def start_scheduler(self):
        """Start the scheduler thread"""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        logger.info("Automation scheduler started")
    
    def stop_scheduler(self):
        """Stop the scheduler thread"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        
        logger.info("Automation scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler in a separate thread"""
        # Schedule daily stats
        schedule.every().day.at("09:00").do(self._run_daily_stats)
        
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _run_daily_stats(self):
        """Run daily statistics workflow"""
        asyncio.create_task(self.execute_workflow("daily_stats", {}))
    
    async def trigger_webhook(self, endpoint: str, data: Dict[str, Any]):
        """Trigger workflows based on webhook"""
        for workflow in self.workflows.values():
            if (workflow.trigger.trigger_type == TriggerType.WEBHOOK and 
                workflow.trigger.config.get('endpoint') == endpoint):
                await self.execute_workflow(workflow.workflow_id, data)
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get status of all workflows"""
        status = {
            'total_workflows': len(self.workflows),
            'enabled_workflows': sum(1 for w in self.workflows.values() if w.enabled),
            'workflows': []
        }
        
        for workflow in self.workflows.values():
            status['workflows'].append({
                'id': workflow.workflow_id,
                'name': workflow.name,
                'enabled': workflow.enabled,
                'last_run': workflow.last_run.isoformat() if workflow.last_run else None
            })
        
        return status

# Factory function to create automation engine
def create_automation_engine() -> AutomationEngine:
    """Create and configure automation engine"""
    
    # Database manager
    db_manager = DatabaseManager()
    
    # Email manager (optional)
    email_manager = None
    if all(os.getenv(key) for key in ['SMTP_SERVER', 'SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD']):
        email_manager = EmailManager(
            smtp_server=os.getenv('SMTP_SERVER'),
            smtp_port=int(os.getenv('SMTP_PORT')),
            username=os.getenv('SMTP_USERNAME'),
            password=os.getenv('SMTP_PASSWORD')
        )
    
    # Create automation engine
    engine = AutomationEngine(db_manager, email_manager)
    
    return engine

# Test the automation engine
async def test_automation():
    """Test the automation engine"""
    engine = create_automation_engine()
    
    # Test chat logging workflow
    chat_data = {
        'chat_data': {
            'user_id': 'test_user',
            'message': 'Test message',
            'response': 'Test response',
            'language': 'it',
            'processing_time': 1.5,
            'session_id': 'test_session'
        }
    }
    
    execution = await engine.execute_workflow("chat_logging", chat_data)
    print(f"Workflow execution: {execution.status}")
    
    # Get statistics
    stats = engine.db_manager.get_chat_stats()
    print(f"Chat statistics: {stats}")
    
    # Get workflow status
    status = engine.get_workflow_status()
    print(f"Workflow status: {status}")

if __name__ == "__main__":
    asyncio.run(test_automation())