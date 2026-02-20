"""
Integration tests for the Bewerbungs-Agent
"""
import pytest

from src.bewerbungs_agent.agent import BewerbungsAgent


class TestBewerbungsAgent:
    """Test main agent functionality"""
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        agent = BewerbungsAgent(config_path='nonexistent.yaml')
        
        assert agent is not None
        assert agent.gmail_client is not None
        assert agent.classifier is not None
        assert agent.agent_team is not None
    
    def test_agent_test_connection(self):
        """Test connection testing"""
        agent = BewerbungsAgent(config_path='nonexistent.yaml')
        
        results = agent.test_connection()
        
        assert 'gmail' in results
        assert 'openai' in results
        assert isinstance(results['gmail'], bool)
        assert isinstance(results['openai'], bool)
    
    def test_agent_run_no_messages(self):
        """Test agent run with no messages"""
        agent = BewerbungsAgent(config_path='nonexistent.yaml')
        
        # Run will return empty results if Gmail is not connected
        results = agent.run(query='test', max_emails=5)
        
        assert 'processed' in results
        assert 'acceptances' in results
        assert 'rejections' in results
        assert 'errors' in results
        assert isinstance(results['details'], list)
    
    def test_agent_get_processing_history(self):
        """Test getting processing history"""
        agent = BewerbungsAgent(config_path='nonexistent.yaml')
        
        history = agent.get_processing_history()
        
        assert isinstance(history, list)
    
    def test_agent_get_stats(self):
        """Test getting agent statistics"""
        agent = BewerbungsAgent(config_path='nonexistent.yaml')
        
        stats = agent.get_agent_stats()
        
        assert 'total_processed' in stats
        assert 'team_stats' in stats
    
    def test_agent_features_configuration(self):
        """Test that agent respects feature configuration"""
        agent = BewerbungsAgent(config_path='nonexistent.yaml')
        
        # Check that features are configured
        assert 'classify_emails' in agent.features
        assert 'analyze_attachments' in agent.features
        assert 'move_to_folders' in agent.features
        assert 'team_distribution' in agent.features
