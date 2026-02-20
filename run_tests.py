#!/usr/bin/env python3
"""
Test runner for the Bewerbungs-Agent
"""
import sys
import subprocess
from pathlib import Path


def main():
    """Run all tests"""
    print("=" * 60)
    print("Bewerbungs-Agent Test Suite")
    print("=" * 60)
    print()
    
    # Change to repository root
    repo_root = Path(__file__).parent
    
    print("Running tests with pytest...")
    print()
    
    # Run pytest
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short'],
        cwd=repo_root
    )
    
    print()
    print("=" * 60)
    
    if result.returncode == 0:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    
    print("=" * 60)
    
    return result.returncode


if __name__ == '__main__':
    sys.exit(main())
