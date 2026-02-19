"""
Tests for email classifier
"""
import pytest

from src.bewerbungs_agent.classifier import EmailClassifier


class TestEmailClassifier:
    """Test email classification"""
    
    def test_fallback_classify_rejection(self):
        """Test fallback classification for rejection emails"""
        classifier = EmailClassifier(api_key='', model='gpt-4')
        
        email_data = {
            'subject': 'Absage für Ihre Bewerbung',
            'from': 'hr@company.com',
            'body': 'Leider müssen wir Ihnen mitteilen, dass wir Sie nicht berücksichtigen können.'
        }
        
        result = classifier.classify_email(email_data)
        
        assert result['type'] == 'rejection'
        assert 0 < result['confidence'] <= 1
        assert 'reason' in result
    
    def test_fallback_classify_acceptance(self):
        """Test fallback classification for acceptance emails"""
        classifier = EmailClassifier(api_key='', model='gpt-4')
        
        email_data = {
            'subject': 'Zusage für Ihre Bewerbung',
            'from': 'hr@company.com',
            'body': 'Wir freuen uns, Ihnen ein Angebot zu unterbreiten. Willkommen im Team!'
        }
        
        result = classifier.classify_email(email_data)
        
        assert result['type'] == 'acceptance'
        assert 0 < result['confidence'] <= 1
        assert 'reason' in result
    
    def test_fallback_classify_unknown(self):
        """Test fallback classification for unclear emails"""
        classifier = EmailClassifier(api_key='', model='gpt-4')
        
        email_data = {
            'subject': 'Nachfrage zu Ihrer Bewerbung',
            'from': 'hr@company.com',
            'body': 'Vielen Dank für Ihre Bewerbung. Wir melden uns bald.'
        }
        
        result = classifier.classify_email(email_data)
        
        assert result['type'] in ['acceptance', 'rejection', 'unknown']
        assert 0 <= result['confidence'] <= 1
    
    def test_classifier_with_attachment_text(self):
        """Test classification with attachment text"""
        classifier = EmailClassifier(api_key='', model='gpt-4')
        
        email_data = {
            'subject': 'Bewerbung Update',
            'body': 'Siehe Anhang'
        }
        
        attachment_text = 'Leider müssen wir absagen.'
        
        result = classifier.classify_email(email_data, attachment_text)
        
        # Should classify based on attachment
        assert result['type'] == 'rejection'
    
    def test_classifier_english_rejection(self):
        """Test classification of English rejection emails"""
        classifier = EmailClassifier(api_key='', model='gpt-4')
        
        email_data = {
            'subject': 'Application Status',
            'body': 'Unfortunately, we regret to inform you that we cannot move forward with your application.'
        }
        
        result = classifier.classify_email(email_data)
        
        assert result['type'] == 'rejection'
    
    def test_classifier_english_acceptance(self):
        """Test classification of English acceptance emails"""
        classifier = EmailClassifier(api_key='', model='gpt-4')
        
        email_data = {
            'subject': 'Job Offer',
            'body': 'Congratulations! We are pleased to offer you a position. Welcome to our team!'
        }
        
        result = classifier.classify_email(email_data)
        
        assert result['type'] == 'acceptance'
