#!/usr/bin/env python3
"""
Simple scheduler to execute due scheduled calls.
Run this script to automatically execute scheduled calls as they become due.
"""

import os
import sys
import django
import time
from datetime import datetime

# Add the project path
sys.path.append('/Users/apple/Desktop/David2/Agentic-Interviewer/backend')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.management import call_command
from django.utils import timezone

def run_scheduler():
    print("🚀 Starting Agentic Interviewer Call Scheduler...")
    print("⏰ Will check for due calls every 30 seconds")
    print("📞 Press Ctrl+C to stop\n")
    
    try:
        while True:
            current_time = timezone.now()
            print(f"🔍 Checking for due calls at {current_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            
            try:
                # Execute the management command to check and execute due calls
                call_command('execute_scheduled_calls')
                print("✅ Check completed")
                
                # Update call details for recent calls (last 2 hours)
                print("🔄 Updating call details...")
                call_command('update_call_details', '--hours', '2')
                print("✅ Call details updated")
                
            except Exception as e:
                print(f"❌ Error during execution: {e}")
            
            print(f"💤 Sleeping for 30 seconds...\n")
            time.sleep(30)  # Check every 30 seconds
            
    except KeyboardInterrupt:
        print("\n🛑 Scheduler stopped by user")
    except Exception as e:
        print(f"\n💥 Scheduler error: {e}")

if __name__ == "__main__":
    run_scheduler()