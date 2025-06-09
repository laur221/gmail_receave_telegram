#!/usr/bin/env python3
"""
Simple test script for Render deployment
This will run the test_render.py script and then start the main bot
"""

import os
import sys

def main():
    print("🚀 Starting Render deployment test...")
    
    # First run the configuration test
    try:
        print("\n🔍 Running configuration tests...")
        exec(open('test_render.py').read())
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return
    
    print("\n🤖 Starting main Gmail bot...")
    
    # Import and run the main bot
    try:
        import test
        test.main()
    except Exception as e:
        print(f"❌ Bot failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
