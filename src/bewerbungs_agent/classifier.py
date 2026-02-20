"""
OpenAI-based email classification
"""
from typing import Dict, Any, Optional
import json

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from .logger import get_logger


logger = get_logger('classifier')


class EmailClassifier:
    """Classifier for email types using OpenAI"""
    
    def __init__(self, api_key: str, model: str = "gpt-4", temperature: float = 0.3):
        """
        Initialize classifier
        
        Args:
            api_key: OpenAI API key
            model: Model to use
            temperature: Temperature for responses
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.client = None
        
        if OpenAI and api_key:
            self.client = OpenAI(api_key=api_key)
            logger.info(f"Initialized OpenAI classifier with model: {model}")
        else:
            logger.warning("OpenAI not initialized (missing API key or library)")
    
    def classify_email(self, email_data: Dict[str, Any], attachment_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Classify email as acceptance or rejection
        
        Args:
            email_data: Parsed email data
            attachment_text: Optional text from attachments
            
        Returns:
            Classification result with type and confidence
        """
        if not self.client:
            logger.warning("OpenAI client not initialized, using fallback classification")
            return self._fallback_classify(email_data, attachment_text)
        
        try:
            # Prepare prompt
            prompt = self._create_classification_prompt(email_data, attachment_text)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at classifying job application emails. Classify emails as 'acceptance' (Zusage) or 'rejection' (Absage) based on their content."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            logger.info(f"Classified email as: {result.get('type')} (confidence: {result.get('confidence')})")
            return result
        
        except Exception as e:
            logger.error(f"Error classifying email: {e}")
            return self._fallback_classify(email_data, attachment_text)
    
    def _create_classification_prompt(self, email_data: Dict[str, Any], attachment_text: Optional[str]) -> str:
        """Create prompt for classification"""
        prompt_parts = [
            "Classify this job application email as either 'acceptance' or 'rejection'.",
            "",
            f"Subject: {email_data.get('subject', 'N/A')}",
            f"From: {email_data.get('from', 'N/A')}",
            "",
            "Email body:",
            email_data.get('body', email_data.get('snippet', '')),
        ]
        
        if attachment_text:
            prompt_parts.extend([
                "",
                "Attachment content:",
                attachment_text[:1000]  # Limit attachment text
            ])
        
        prompt_parts.extend([
            "",
            "Return a JSON object with:",
            '- "type": either "acceptance" or "rejection"',
            '- "confidence": a number between 0 and 1',
            '- "reason": brief explanation for the classification'
        ])
        
        return "\n".join(prompt_parts)
    
    def _fallback_classify(self, email_data: Dict[str, Any], attachment_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Fallback classification using keyword matching
        
        Args:
            email_data: Parsed email data
            attachment_text: Optional text from attachments
            
        Returns:
            Classification result
        """
        subject = (email_data.get('subject') or '').lower()
        body = (email_data.get('body') or email_data.get('snippet', '')).lower()
        attachment_content = (attachment_text or '').lower()
        content = f"{subject} {body} {attachment_content}"
        
        # Keywords for rejection
        rejection_keywords = [
            'absage', 'ablehnung', 'leider', 'nicht berücksichtigen',
            'rejection', 'unfortunately', 'regret', 'not selected',
            'andere kandidaten', 'andere bewerber'
        ]
        
        # Keywords for acceptance
        acceptance_keywords = [
            'zusage', 'angebot', 'vertrag', 'einstellung', 'willkommen',
            'acceptance', 'offer', 'contract', 'hired', 'welcome',
            'glückwunsch', 'congratulations', 'vorstellungsgespräch', 'interview'
        ]
        
        rejection_count = sum(1 for kw in rejection_keywords if kw in content)
        acceptance_count = sum(1 for kw in acceptance_keywords if kw in content)
        
        if rejection_count > acceptance_count:
            classification_type = 'rejection'
            confidence = min(0.9, 0.5 + (rejection_count * 0.1))
        elif acceptance_count > rejection_count:
            classification_type = 'acceptance'
            confidence = min(0.9, 0.5 + (acceptance_count * 0.1))
        else:
            classification_type = 'unknown'
            confidence = 0.3
        
        logger.info(f"Fallback classification: {classification_type} (confidence: {confidence})")
        
        return {
            'type': classification_type,
            'confidence': confidence,
            'reason': 'Fallback keyword-based classification'
        }
