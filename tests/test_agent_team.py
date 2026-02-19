"""
Tests for agent team
"""
import pytest

from src.bewerbungs_agent.agent_team import AgentTeam


class TestAgentTeam:
    """Test agent team functionality"""
    
    def test_agent_team_initialization(self):
        """Test agent team initialization"""
        team_config = [
            {'name': 'Reviewer', 'role': 'Reviews documents'},
            {'name': 'Scheduler', 'role': 'Schedules interviews'}
        ]
        
        team = AgentTeam(team_config)
        
        assert len(team.agents) == 2
        assert team.agents[0]['name'] == 'Reviewer'
        assert team.agents[1]['name'] == 'Scheduler'
    
    def test_distribute_acceptance_tasks(self):
        """Test task distribution for acceptance emails"""
        team_config = [
            {'name': 'Reviewer', 'role': 'Reviews documents'},
            {'name': 'Scheduler', 'role': 'Schedules interviews'},
            {'name': 'Feedback Writer', 'role': 'Writes feedback'}
        ]
        
        team = AgentTeam(team_config)
        
        email_data = {
            'id': 'msg123',
            'subject': 'Job Offer',
            'from': 'company@example.com'
        }
        
        classification = {
            'type': 'acceptance',
            'confidence': 0.9
        }
        
        tasks = team.distribute_tasks(email_data, classification)
        
        assert len(tasks) > 0
        assert any(task['agent'] == 'Reviewer' for task in tasks)
        assert any(task['agent'] == 'Scheduler' for task in tasks)
    
    def test_distribute_rejection_tasks(self):
        """Test task distribution for rejection emails"""
        team_config = [
            {'name': 'Reviewer', 'role': 'Reviews documents'},
            {'name': 'Feedback Writer', 'role': 'Writes feedback'}
        ]
        
        team = AgentTeam(team_config)
        
        email_data = {
            'id': 'msg456',
            'subject': 'Application Status',
            'from': 'company@example.com'
        }
        
        classification = {
            'type': 'rejection',
            'confidence': 0.85
        }
        
        tasks = team.distribute_tasks(email_data, classification)
        
        assert len(tasks) > 0
        assert any(task['agent'] == 'Feedback Writer' for task in tasks)
    
    def test_distribute_unknown_tasks(self):
        """Test task distribution for unknown email types"""
        team_config = [
            {'name': 'Reviewer', 'role': 'Reviews documents'}
        ]
        
        team = AgentTeam(team_config)
        
        email_data = {
            'id': 'msg789',
            'subject': 'Question',
            'from': 'company@example.com'
        }
        
        classification = {
            'type': 'unknown',
            'confidence': 0.4
        }
        
        tasks = team.distribute_tasks(email_data, classification)
        
        assert len(tasks) > 0
        assert any(task['action'] == 'manual_review' for task in tasks)
    
    def test_task_history(self):
        """Test task history tracking"""
        team_config = [
            {'name': 'Reviewer', 'role': 'Reviews documents'}
        ]
        
        team = AgentTeam(team_config)
        
        email_data = {'id': 'msg1', 'from': 'test@example.com'}
        classification = {'type': 'acceptance', 'confidence': 0.9}
        
        team.distribute_tasks(email_data, classification)
        
        history = team.get_task_history()
        assert len(history) > 0
        assert 'timestamp' in history[0]
        assert 'email_id' in history[0]
    
    def test_agent_stats(self):
        """Test agent statistics"""
        team_config = [
            {'name': 'Reviewer', 'role': 'Reviews documents'},
            {'name': 'Scheduler', 'role': 'Schedules interviews'}
        ]
        
        team = AgentTeam(team_config)
        
        # Distribute some tasks
        email_data1 = {'id': 'msg1', 'from': 'test1@example.com'}
        classification1 = {'type': 'acceptance', 'confidence': 0.9}
        team.distribute_tasks(email_data1, classification1)
        
        email_data2 = {'id': 'msg2', 'from': 'test2@example.com'}
        classification2 = {'type': 'rejection', 'confidence': 0.8}
        team.distribute_tasks(email_data2, classification2)
        
        stats = team.get_agent_stats()
        
        assert 'Reviewer' in stats
        assert 'Scheduler' in stats
        assert stats['Reviewer']['total_tasks'] > 0
        assert 'role' in stats['Reviewer']
