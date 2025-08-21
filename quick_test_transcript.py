#!/usr/bin/env python3
"""
Quick Test Script for AI Transcript Processing
Use this to quickly test your own transcripts and knowledge bases
"""
import os
import sys
import django

# Add the backend directory to Python path
sys.path.insert(0, '/Users/apple/Desktop/Davv/Agentic-Interviewer/backend')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.views import CreateAssistantView
from django.contrib.auth.models import User

def quick_test():
    """Quick test with your own data"""
    print("🚀 Quick AI Transcript Test")
    print("=" * 40)
    
    # YOUR TEST DATA HERE - Replace with your own content
    test_transcript = """assistant: Let's discuss the first article about artificial intelligence. What are your thoughts on AI?

user: I think AI is fascinating. I've been working with machine learning for 3 years, mainly on natural language processing projects. I've built chatbots and sentiment analysis systems.

A: Great! Now let's talk about the second article on cloud computing. What's your experience there?

user: I've been using AWS for 5 years. I'm certified in Solutions Architecture and have migrated 10+ applications to the cloud, focusing on serverless architectures and microservices."""

    test_knowledge = """=== ARTICLE 1 ===
Artificial Intelligence: The Future of Technology

AI is transforming every industry through machine learning, natural language processing, and computer vision. Modern AI applications include chatbots, recommendation systems, autonomous vehicles, and predictive analytics.

=== ARTICLE 2 ===
Cloud Computing: Scalable Infrastructure Solutions

Cloud computing provides on-demand access to computing resources including servers, storage, databases, and software. Major cloud providers like AWS, Azure, and Google Cloud offer scalable solutions for businesses of all sizes."""

    try:
        user = User.objects.get(username='Mehroz')
        assistant_creator = CreateAssistantView()
        
        print("🔄 Processing your test transcript...")
        result = assistant_creator.process_transcript_with_articles(test_transcript, test_knowledge, user=user)
        
        if result.get("success"):
            print("✅ Processing successful!")
            print("\n📋 AI Output:")
            print("-" * 40)
            print(result.get("structured_output", "No output"))
        else:
            print(f"❌ Processing failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def custom_test(transcript, knowledge):
    """Test with custom transcript and knowledge"""
    try:
        user = User.objects.get(username='Mehroz')
        assistant_creator = CreateAssistantView()
        
        result = assistant_creator.process_transcript_with_articles(transcript, knowledge, user=user)
        
        if result.get("success"):
            print("✅ Custom test successful!")
            print("\n📋 AI Output:")
            print("-" * 40)
            print(result.get("structured_output", "No output"))
        else:
            print(f"❌ Custom test failed: {result.get('error')}")
            
        return result
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    quick_test()
    
    print("\n" + "="*50)
    print("📝 To test your own data:")
    print("1. Edit the 'test_transcript' and 'test_knowledge' variables above")
    print("2. Run: python3 quick_test_transcript.py")
    print("3. Or import this file and use custom_test(transcript, knowledge)")