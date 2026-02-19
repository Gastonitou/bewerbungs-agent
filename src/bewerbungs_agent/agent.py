"""
Main agent orchestrator for the Bewerbungs-Agent
"""
from typing import List, Dict, Any, Optional
from datetime import datetime

from .config import Config
from .logger import setup_logging, get_logger
from .gmail_client import GmailClient
from .email_parser import EmailParser
from .attachment_processor import AttachmentProcessor
from .classifier import EmailClassifier
from .agent_team import AgentTeam


class BewerbungsAgent:
    """Main AI Agent for application management"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Bewerbungs-Agent
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = Config(config_path)
        
        # Setup logging
        self.logger = setup_logging(self.config.get_logging_config())
        self.logger.info("Initializing Bewerbungs-Agent")
        
        # Initialize components
        gmail_config = self.config.get_gmail_config()
        openai_config = self.config.get_openai_config()
        agent_config = self.config.get_agent_config()
        
        self.gmail_client = GmailClient(
            credentials_file=gmail_config.get('credentials_file', 'credentials.json'),
            token_file=gmail_config.get('token_file', 'token.json')
        )
        
        self.email_parser = EmailParser()
        self.attachment_processor = AttachmentProcessor()
        
        self.classifier = EmailClassifier(
            api_key=openai_config.get('api_key', ''),
            model=openai_config.get('model', 'gpt-4'),
            temperature=openai_config.get('temperature', 0.3)
        )
        
        self.agent_team = AgentTeam(agent_config.get('team', []))
        
        self.features = agent_config.get('features', {})
        self.folders = gmail_config.get('folders', {})
        
        self.processing_history: List[Dict[str, Any]] = []
        
        self.logger.info("Bewerbungs-Agent initialized successfully")
    
    def run(self, query: str = "is:unread", max_emails: int = 10) -> Dict[str, Any]:
        """
        Run the agent to process emails
        
        Args:
            query: Gmail search query
            max_emails: Maximum number of emails to process
            
        Returns:
            Processing results
        """
        self.logger.info(f"Starting agent run with query: {query}")
        
        # Fetch emails
        messages = self.gmail_client.list_messages(query=query, max_results=max_emails)
        self.logger.info(f"Found {len(messages)} messages to process")
        
        results = {
            'processed': 0,
            'acceptances': 0,
            'rejections': 0,
            'unknown': 0,
            'errors': 0,
            'details': []
        }
        
        for message_summary in messages:
            message_id = message_summary['id']
            
            try:
                result = self.process_email(message_id)
                results['details'].append(result)
                results['processed'] += 1
                
                classification_type = result.get('classification', {}).get('type')
                if classification_type == 'acceptance':
                    results['acceptances'] += 1
                elif classification_type == 'rejection':
                    results['rejections'] += 1
                else:
                    results['unknown'] += 1
            
            except Exception as e:
                self.logger.error(f"Error processing message {message_id}: {e}")
                results['errors'] += 1
                results['details'].append({
                    'message_id': message_id,
                    'error': str(e)
                })
        
        self.logger.info(f"Agent run completed: {results['processed']} processed, "
                        f"{results['acceptances']} acceptances, {results['rejections']} rejections")
        
        return results
    
    def process_email(self, message_id: str) -> Dict[str, Any]:
        """
        Process a single email
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            Processing result
        """
        self.logger.info(f"Processing email: {message_id}")
        
        # Get full message
        message = self.gmail_client.get_message(message_id)
        if not message:
            raise Exception("Failed to retrieve message")
        
        # Parse email
        parsed_email = self.email_parser.parse_message(message)
        
        # Process attachments if enabled
        attachment_text = None
        if self.features.get('analyze_attachments', True):
            attachments = self.gmail_client.get_attachments(message_id)
            if attachments:
                attachment_texts = []
                for attachment in attachments:
                    text = self.attachment_processor.process_attachment(attachment)
                    if text:
                        attachment_texts.append(text)
                
                if attachment_texts:
                    attachment_text = "\n\n".join(attachment_texts)
                    self.logger.info(f"Processed {len(attachment_texts)} attachments")
        
        # Classify email if enabled
        classification = None
        if self.features.get('classify_emails', True):
            classification = self.classifier.classify_email(parsed_email, attachment_text)
        
        # Move to appropriate folder if enabled
        if self.features.get('move_to_folders', True) and classification:
            self._move_email_to_folder(message_id, classification)
        
        # Distribute tasks to team if enabled
        tasks = []
        if self.features.get('team_distribution', True) and classification:
            tasks = self.agent_team.distribute_tasks(parsed_email, classification)
        
        # Record processing
        result = {
            'message_id': message_id,
            'timestamp': datetime.now().isoformat(),
            'email': {
                'subject': parsed_email.get('subject'),
                'from': parsed_email.get('from'),
                'date': parsed_email.get('date')
            },
            'classification': classification,
            'tasks': tasks,
            'attachments_processed': len(attachments) if attachments else 0
        }
        
        self.processing_history.append(result)
        self.logger.info(f"Completed processing email: {parsed_email.get('subject')}")
        
        return result
    
    def _move_email_to_folder(self, message_id: str, classification: Dict[str, Any]):
        """Move email to appropriate folder based on classification"""
        classification_type = classification.get('type')
        
        if classification_type == 'acceptance':
            folder = self.folders.get('acceptances', 'Zusagen')
            self.gmail_client.move_to_label(message_id, folder)
        elif classification_type == 'rejection':
            folder = self.folders.get('rejections', 'Absagen')
            self.gmail_client.move_to_label(message_id, folder)
        else:
            # Move unknown to processed folder
            folder = self.folders.get('processed', 'Verarbeitet')
            self.gmail_client.move_to_label(message_id, folder)
    
    def get_processing_history(self) -> List[Dict[str, Any]]:
        """Get processing history"""
        return self.processing_history
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            'total_processed': len(self.processing_history),
            'team_stats': self.agent_team.get_agent_stats()
        }
    
    def test_connection(self) -> Dict[str, bool]:
        """
        Test connections to external services
        
        Returns:
            Dictionary with connection test results
        """
        self.logger.info("Testing connections...")
        
        results = {
            'gmail': self.gmail_client.service is not None,
            'openai': self.classifier.client is not None
        }
        
        self.logger.info(f"Connection test results: {results}")
        return results
