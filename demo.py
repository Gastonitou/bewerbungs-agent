#!/usr/bin/env python3
"""
Demo script for testing the Bewerbungs-Agent
This demonstrates the agent functionality without requiring real Gmail/OpenAI credentials
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.bewerbungs_agent.config import Config
from src.bewerbungs_agent.classifier import EmailClassifier
from src.bewerbungs_agent.agent_team import AgentTeam
from src.bewerbungs_agent.email_parser import EmailParser


def demo_classification():
    """Demo email classification"""
    print("=" * 60)
    print("DEMO 1: Email Classification")
    print("=" * 60)
    print()
    
    classifier = EmailClassifier(api_key='', model='gpt-4')
    
    # Test cases
    test_emails = [
        {
            'name': 'German Rejection',
            'subject': 'Absage für Ihre Bewerbung',
            'body': 'Sehr geehrte/r Bewerber/in, leider müssen wir Ihnen mitteilen, dass wir uns für andere Kandidaten entschieden haben.'
        },
        {
            'name': 'German Acceptance',
            'subject': 'Zusage - Willkommen im Team!',
            'body': 'Wir freuen uns sehr, Ihnen ein Angebot für die Position zu unterbreiten. Herzlich willkommen in unserem Team!'
        },
        {
            'name': 'English Rejection',
            'subject': 'Application Status Update',
            'body': 'Unfortunately, we regret to inform you that we will not be moving forward with your application at this time.'
        },
        {
            'name': 'English Acceptance',
            'subject': 'Job Offer - Software Engineer',
            'body': 'Congratulations! We are pleased to offer you the position of Software Engineer. Welcome to our company!'
        }
    ]
    
    for email in test_emails:
        print(f"Testing: {email['name']}")
        print(f"Subject: {email['subject']}")
        
        result = classifier.classify_email(email)
        
        print(f"Result: {result['type'].upper()}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Reason: {result['reason']}")
        print()


def demo_agent_team():
    """Demo agent team task distribution"""
    print("=" * 60)
    print("DEMO 2: Agent Team Task Distribution")
    print("=" * 60)
    print()
    
    team_config = [
        {'name': 'Reviewer', 'role': 'Reviews application documents'},
        {'name': 'Feedback Writer', 'role': 'Writes feedback for applicants'},
        {'name': 'Scheduler', 'role': 'Schedules interviews'}
    ]
    
    team = AgentTeam(team_config)
    
    # Test scenarios
    scenarios = [
        {
            'email': {
                'id': 'msg001',
                'subject': 'Job Offer Accepted',
                'from': 'candidate@example.com'
            },
            'classification': {
                'type': 'acceptance',
                'confidence': 0.95
            }
        },
        {
            'email': {
                'id': 'msg002',
                'subject': 'Application Rejection',
                'from': 'company@example.com'
            },
            'classification': {
                'type': 'rejection',
                'confidence': 0.88
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"Scenario {i}: {scenario['classification']['type'].upper()}")
        print(f"Email: {scenario['email']['subject']}")
        print()
        
        tasks = team.distribute_tasks(scenario['email'], scenario['classification'])
        
        print(f"Tasks assigned ({len(tasks)} total):")
        for task in tasks:
            print(f"  → {task['agent']}: {task['description']}")
            print(f"    Action: {task['action']}")
            print(f"    Priority: {task['priority']}")
        print()
    
    # Show statistics
    print("-" * 60)
    print("Agent Statistics:")
    print("-" * 60)
    stats = team.get_agent_stats()
    for agent_name, agent_stats in stats.items():
        print(f"{agent_name} ({agent_stats['role']})")
        print(f"  Total tasks assigned: {agent_stats['total_tasks']}")
    print()


def demo_email_parsing():
    """Demo email parsing"""
    print("=" * 60)
    print("DEMO 3: Email Parsing")
    print("=" * 60)
    print()
    
    # Sample Gmail message format
    sample_message = {
        'id': 'msg12345',
        'threadId': 'thread67890',
        'snippet': 'Thank you for your application...',
        'payload': {
            'headers': [
                {'name': 'Subject', 'value': 'Re: Software Engineer Position'},
                {'name': 'From', 'value': 'HR Department <hr@company.com>'},
                {'name': 'To', 'value': 'candidate@example.com'},
                {'name': 'Date', 'value': 'Wed, 19 Feb 2026 10:30:00 +0000'}
            ],
            'body': {
                'data': 'VGhhbmsgZm9yIHlvdXIgYXBwbGljYXRpb24uIFdlIHdvdWxkIGxpa2UgdG8gbW92ZSBmb3J3YXJkIHdpdGggeW91ciBjYW5kaWRhY3ku'
            }
        }
    }
    
    parsed = EmailParser.parse_message(sample_message)
    
    print("Parsed Email:")
    print(f"  ID: {parsed['id']}")
    print(f"  Subject: {parsed['subject']}")
    print(f"  From: {parsed['from']}")
    print(f"  To: {parsed['to']}")
    print(f"  Date: {parsed['date']}")
    print(f"  Snippet: {parsed['snippet']}")
    print()
    
    # Extract sender email
    sender_email = EmailParser.extract_sender_email(parsed['from'])
    print(f"Extracted sender email: {sender_email}")
    print()


def demo_config():
    """Demo configuration"""
    print("=" * 60)
    print("DEMO 4: Configuration Management")
    print("=" * 60)
    print()
    
    config = Config('nonexistent.yaml')
    
    print("Configuration loaded (using defaults):")
    print()
    
    print("Gmail Configuration:")
    gmail_config = config.get_gmail_config()
    print(f"  Email: {gmail_config.get('email')}")
    print(f"  Folders:")
    for folder_type, folder_name in gmail_config.get('folders', {}).items():
        print(f"    {folder_type}: {folder_name}")
    print()
    
    print("OpenAI Configuration:")
    openai_config = config.get_openai_config()
    print(f"  Model: {openai_config.get('model')}")
    print(f"  Temperature: {openai_config.get('temperature')}")
    print()
    
    print("Agent Features:")
    agent_config = config.get_agent_config()
    for feature, enabled in agent_config.get('features', {}).items():
        status = "✓ Enabled" if enabled else "✗ Disabled"
        print(f"  {feature}: {status}")
    print()


def main():
    """Run all demos"""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  Bewerbungs-Agent - Interactive Demo".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    demos = [
        ("Configuration Management", demo_config),
        ("Email Parsing", demo_email_parsing),
        ("Email Classification", demo_classification),
        ("Agent Team Task Distribution", demo_agent_team),
    ]
    
    for i, (name, demo_func) in enumerate(demos):
        if i > 0:
            input("\nPress Enter to continue to next demo...")
            print()
        
        demo_func()
    
    print("=" * 60)
    print("Demo completed!")
    print()
    print("To test with real data:")
    print("  1. Set up Gmail API credentials (credentials.json)")
    print("  2. Add OpenAI API key to config.yaml")
    print("  3. Run: python main.py")
    print("=" * 60)


if __name__ == '__main__':
    main()
