"""
Agent team for task distribution
"""
from typing import List, Dict, Any
from datetime import datetime

from .logger import get_logger


logger = get_logger('agent_team')


class AgentTeam:
    """Manages the agent team and task distribution"""
    
    def __init__(self, team_config: List[Dict[str, str]]):
        """
        Initialize agent team
        
        Args:
            team_config: List of agent configurations
        """
        self.agents = team_config
        self.task_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized agent team with {len(self.agents)} agents")
    
    def distribute_tasks(self, email_data: Dict[str, Any], classification: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Distribute tasks to agent team based on email classification
        
        Args:
            email_data: Parsed email data
            classification: Classification result
            
        Returns:
            List of assigned tasks
        """
        tasks = []
        
        email_type = classification.get('type')
        confidence = classification.get('confidence', 0)
        
        logger.info(f"Distributing tasks for {email_type} email (confidence: {confidence})")
        
        if email_type == 'acceptance':
            tasks.extend(self._create_acceptance_tasks(email_data))
        elif email_type == 'rejection':
            tasks.extend(self._create_rejection_tasks(email_data))
        else:
            tasks.extend(self._create_unknown_tasks(email_data))
        
        # Record tasks in history
        for task in tasks:
            task['timestamp'] = datetime.now().isoformat()
            task['email_id'] = email_data.get('id')
            self.task_history.append(task)
        
        logger.info(f"Created {len(tasks)} tasks for agent team")
        return tasks
    
    def _create_acceptance_tasks(self, email_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create tasks for acceptance emails"""
        tasks = []
        
        # Task for reviewer
        tasks.append({
            'agent': 'Reviewer',
            'action': 'review_acceptance',
            'description': f"Review acceptance email from {email_data.get('from')}",
            'priority': 'high',
            'status': 'assigned'
        })
        
        # Task for scheduler
        tasks.append({
            'agent': 'Scheduler',
            'action': 'schedule_onboarding',
            'description': f"Schedule onboarding for accepted applicant: {email_data.get('subject')}",
            'priority': 'high',
            'status': 'assigned'
        })
        
        return tasks
    
    def _create_rejection_tasks(self, email_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create tasks for rejection emails"""
        tasks = []
        
        # Task for feedback writer
        tasks.append({
            'agent': 'Feedback Writer',
            'action': 'acknowledge_rejection',
            'description': f"Acknowledge rejection email from {email_data.get('from')}",
            'priority': 'medium',
            'status': 'assigned'
        })
        
        return tasks
    
    def _create_unknown_tasks(self, email_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create tasks for unknown email types"""
        tasks = []
        
        # Task for reviewer
        tasks.append({
            'agent': 'Reviewer',
            'action': 'manual_review',
            'description': f"Manually review unclear email from {email_data.get('from')}",
            'priority': 'medium',
            'status': 'assigned'
        })
        
        return tasks
    
    def get_task_history(self) -> List[Dict[str, Any]]:
        """Get task history"""
        return self.task_history
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get statistics about agent task distribution"""
        stats = {}
        
        for agent in self.agents:
            agent_name = agent['name']
            agent_tasks = [t for t in self.task_history if t['agent'] == agent_name]
            
            stats[agent_name] = {
                'total_tasks': len(agent_tasks),
                'role': agent['role'],
                'tasks': agent_tasks
            }
        
        return stats
