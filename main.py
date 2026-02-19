#!/usr/bin/env python3
"""
Command-line interface for the Bewerbungs-Agent
"""
import argparse
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.bewerbungs_agent.agent import BewerbungsAgent
from src.bewerbungs_agent.config import Config


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Bewerbungs-Agent - AI Agent for Application Management'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--query',
        type=str,
        default='is:unread',
        help='Gmail search query (default: is:unread)'
    )
    
    parser.add_argument(
        '--max-emails',
        type=int,
        default=10,
        help='Maximum number of emails to process (default: 10)'
    )
    
    parser.add_argument(
        '--test-connection',
        action='store_true',
        help='Test connections to Gmail and OpenAI without processing emails'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show agent statistics after processing'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Bewerbungs-Agent - AI Agent for Application Management")
    print("=" * 60)
    print()
    
    try:
        # Initialize agent
        print(f"Loading configuration from: {args.config}")
        agent = BewerbungsAgent(config_path=args.config)
        print("✓ Agent initialized successfully")
        print()
        
        # Test connection if requested
        if args.test_connection:
            print("Testing connections...")
            results = agent.test_connection()
            print(f"  Gmail API: {'✓ Connected' if results['gmail'] else '✗ Not connected'}")
            print(f"  OpenAI API: {'✓ Connected' if results['openai'] else '✗ Not connected'}")
            print()
            
            if not any(results.values()):
                print("⚠ Warning: No external connections available. Running in test mode.")
                print()
        
        # Run agent
        print(f"Processing emails with query: {args.query}")
        print(f"Maximum emails to process: {args.max_emails}")
        print()
        
        results = agent.run(query=args.query, max_emails=args.max_emails)
        
        # Display results
        print("-" * 60)
        print("Processing Results:")
        print("-" * 60)
        print(f"Total processed: {results['processed']}")
        print(f"  Acceptances: {results['acceptances']}")
        print(f"  Rejections: {results['rejections']}")
        print(f"  Unknown: {results['unknown']}")
        print(f"  Errors: {results['errors']}")
        print()
        
        # Show details
        if results['details']:
            print("Processed Emails:")
            print("-" * 60)
            for i, detail in enumerate(results['details'], 1):
                if 'error' in detail:
                    print(f"{i}. ERROR: {detail.get('error')}")
                else:
                    email_info = detail.get('email', {})
                    classification = detail.get('classification', {})
                    print(f"{i}. Subject: {email_info.get('subject', 'N/A')}")
                    print(f"   From: {email_info.get('from', 'N/A')}")
                    print(f"   Type: {classification.get('type', 'N/A')} "
                          f"(confidence: {classification.get('confidence', 0):.2f})")
                    print(f"   Tasks assigned: {len(detail.get('tasks', []))}")
                    print()
        
        # Show stats if requested
        if args.stats:
            print("-" * 60)
            print("Agent Statistics:")
            print("-" * 60)
            stats = agent.get_agent_stats()
            print(f"Total emails processed: {stats['total_processed']}")
            print()
            
            print("Team Task Distribution:")
            for agent_name, agent_stats in stats['team_stats'].items():
                print(f"  {agent_name} ({agent_stats['role']})")
                print(f"    Total tasks: {agent_stats['total_tasks']}")
            print()
        
        print("=" * 60)
        print("Agent run completed successfully!")
        print("=" * 60)
        
        return 0
    
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
