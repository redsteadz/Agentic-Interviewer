#!/usr/bin/env python3
"""
Create Test Data for Dashboard Display
This script creates realistic interview calls with AI-processed transcripts
that will appear in your dashboard at http://localhost:5173/dashboard
"""
import os
import sys
import django
from datetime import datetime, timedelta
import json

# Add the backend directory to Python path
sys.path.insert(0, '/Users/apple/Desktop/Davv/Agentic-Interviewer/backend')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import InterviewCall, InterviewAssistant, PhoneNumber
from api.views import CreateAssistantView
from django.contrib.auth.models import User

def create_test_call_1():
    """Healthcare AI Interview - 3 Articles Discussed"""
    print("🏥 Creating Healthcare AI Interview Call...")
    
    transcript = """assistant: Good afternoon! I'm here to conduct an interview about artificial intelligence in healthcare. Let's start with the first article about AI diagnostic tools. Can you share your experience with AI in medical diagnostics?

user: Thank you for the opportunity. I have over 6 years of experience in healthcare AI, primarily focusing on diagnostic imaging. I've been leading a team that developed a deep learning system for detecting early-stage lung cancer in CT scans. Our model achieved 95% accuracy and is now being used in 3 major hospitals.

assistant: That's impressive work! Can you elaborate on the challenges you faced in implementing these diagnostic tools in clinical settings?

user: The biggest challenges were data quality and clinician adoption. We had to ensure our training data represented diverse patient populations and imaging equipment. Getting radiologists to trust the AI recommendations took time, but once they saw the consistent accuracy, they became strong advocates. We also had to implement extensive validation protocols to meet FDA requirements.

assistant: Excellent insights. Now let's move to the second article about personalized medicine. How do you see AI transforming treatment personalization?

user: Personalized medicine is where AI really shines. I've worked on a project that analyzes patient genomics, medical history, and biomarkers to predict drug responses. We developed a system for oncologists that recommends optimal chemotherapy protocols based on individual patient profiles. This approach improved treatment success rates by 28% in our pilot study.

assistant: Very promising results. Finally, let's discuss the third article about AI in drug discovery. What's your perspective on AI accelerating pharmaceutical research?

user: AI is revolutionizing drug discovery timelines. I've collaborated with pharmaceutical companies where we used machine learning to identify potential therapeutic compounds for rare diseases. Traditional drug discovery takes 10-15 years, but our AI models can screen millions of molecular combinations in weeks. We've identified 4 promising compounds that are now in Phase II clinical trials."""

    knowledge = """=== ARTICLE 1 ===
AI Diagnostic Tools: Revolutionizing Medical Imaging

Artificial intelligence is transforming medical diagnostics through advanced computer vision and deep learning algorithms. AI diagnostic tools can analyze medical images with unprecedented accuracy, often matching or exceeding human radiologist performance. These systems are particularly effective in detecting early-stage diseases, analyzing chest X-rays for pneumonia, identifying diabetic retinopathy, and detecting various forms of cancer in CT and MRI scans.

Key benefits include faster diagnosis times, reduced human error, 24/7 availability, consistent analysis quality, and early disease detection capabilities.

=== ARTICLE 2 ===
Personalized Medicine Through AI: Tailoring Treatment to Individual Patients

Personalized medicine leverages artificial intelligence to create individualized treatment plans based on patient-specific data including genomics, medical history, lifestyle factors, and real-time biomarkers. AI algorithms analyze vast amounts of patient data to predict treatment responses, identify optimal drug dosages, and recommend the most effective therapeutic approaches.

Applications include genomic analysis for drug selection, biomarker identification, treatment response prediction, risk stratification, precision dosing, and clinical decision support systems.

=== ARTICLE 3 ===
AI in Drug Discovery: Accelerating Pharmaceutical Innovation

Artificial intelligence is revolutionizing drug discovery by dramatically reducing the time and cost required to develop new medications. AI algorithms can analyze molecular structures, predict drug interactions, identify potential therapeutic targets, and optimize compound designs. Machine learning models can screen millions of chemical compounds virtually, significantly accelerating the early stages of drug development.

Key advantages include faster compound identification, reduced development costs, better success prediction, virtual screening capabilities, optimization of drug properties, and accelerated clinical trial design."""

    return transcript, knowledge, "Healthcare AI Specialist Interview", "+1-555-0101"

def create_test_call_2():
    """Technology Leadership Interview - 2 Articles Discussed"""
    print("💻 Creating Technology Leadership Interview Call...")
    
    transcript = """assistant: Welcome to our technology leadership interview. I'd like to discuss your experience with remote work infrastructure. How have you approached building distributed teams?

user: I've been leading distributed teams for over 8 years across multiple companies. My approach focuses on three core areas: robust communication infrastructure, asynchronous workflows, and strong team culture. We use Slack for daily communication, Zoom for video meetings, and I've implemented a documentation-first policy where all decisions are recorded in Confluence.

assistant: That's a comprehensive approach. Can you tell me more about the specific tools and processes you've implemented?

user: Absolutely. Our tech stack includes GitHub for code collaboration with automated CI/CD pipelines, Jira for project management integrated with our development workflow, and we use timezone-friendly meeting schedules. I've also established 'core collaboration hours' where all team members are available regardless of location - typically 10 AM to 2 PM EST.

assistant: Excellent strategy. Now let's discuss cybersecurity in remote environments. How do you ensure security with distributed teams?

user: Security is absolutely critical with remote teams. I've implemented a zero-trust security model where we assume no inherent trust in any network. Every team member uses company-managed devices with endpoint protection, all access is through VPN with multi-factor authentication, and we conduct quarterly security audits. We also have mandatory monthly security training for all team members.

assistant: That's a very thorough security approach. Any final thoughts on managing remote teams effectively?

user: The key is balancing security with productivity. You need robust processes but they can't be so cumbersome that they slow down the team. I spend about 30% of my time on process optimization and team communication to ensure everything runs smoothly."""

    knowledge = """=== ARTICLE 1 ===
Remote Work Infrastructure: Building Effective Distributed Teams

Building successful remote teams requires intentional infrastructure design encompassing communication platforms, collaboration tools, and cultural frameworks. Effective remote work infrastructure includes reliable communication channels, project management systems, development environments, and performance monitoring tools. The key is creating seamless workflows that enable productivity regardless of physical location.

Essential components include communication platforms like Slack and Microsoft Teams, video conferencing solutions, project management tools, documentation systems, development collaboration tools, and time zone coordination strategies.

=== ARTICLE 2 ===
Cybersecurity in Remote Work Environments: Protecting Distributed Organizations

Remote work environments present unique cybersecurity challenges requiring comprehensive security frameworks. Organizations must implement zero-trust security models, secure all endpoints, monitor network traffic, and ensure data protection across distributed teams. The challenge lies in maintaining security without compromising productivity or user experience.

Key security measures include zero-trust network architecture, multi-factor authentication, VPN access controls, endpoint detection and response, regular security training, incident response protocols, and data encryption standards."""

    return transcript, knowledge, "Senior Technology Leader Interview", "+1-555-0102"

def create_test_call_3():
    """Business Strategy Interview - 2 Articles Discussed"""
    print("📊 Creating Business Strategy Interview Call...")
    
    transcript = """assistant: I'd like to discuss business strategy topics with you today. Let's start with market expansion strategies. What's your experience with entering new markets?

user: I've led market expansion initiatives for the past 10 years, successfully taking our company into 15 new international markets. My approach always starts with comprehensive market research - analyzing local competition, regulatory requirements, customer preferences, and cultural factors. For our expansion into Southeast Asia, we spent 8 months understanding local business practices before making any investments.

assistant: That's a very thorough approach. Can you share some specific strategies that have been most effective?

user: We use a three-phase approach. First, we establish local partnerships to understand market dynamics and reduce risk. Then we pilot with a limited product subset to test demand and refine our approach. Finally, we scale based on performance metrics and market feedback. In Europe, we partnered with local distributors initially, which gave us valuable insights and reduced our operational complexity.

assistant: Excellent strategy. Now let's move to sustainable business practices. How do you integrate sustainability into business operations?

user: Sustainability has become central to our business strategy over the last 5 years. I've implemented a triple bottom line approach - focusing on people, planet, and profit. We've reduced our carbon footprint by 45% through supply chain optimization, implemented circular economy principles in our manufacturing processes, and interestingly, our sustainability initiatives have actually improved our profit margins by 18% through efficiency gains and cost reductions."""

    knowledge = """=== ARTICLE 1 ===
Market Expansion Strategies: Growing Business Across Geographic Boundaries

Market expansion requires strategic planning, comprehensive market research, and phased implementation approaches. Successful market expansion involves understanding local market dynamics, regulatory environments, competitive landscapes, and cultural considerations. Companies must balance standardization with localization to achieve sustainable growth in new markets.

Expansion strategies include thorough market research and analysis, partnership development, pilot program implementation, risk assessment and management, local talent acquisition, regulatory compliance, and brand localization strategies.

=== ARTICLE 2 ===
Sustainable Business Practices: Integrating Environmental Responsibility with Profitability

Sustainable business practices involve integrating environmental and social considerations into core business operations while maintaining profitability. Modern sustainability strategies focus on circular economy principles, supply chain optimization, stakeholder engagement, and long-term value creation rather than short-term profits.

Key sustainability areas include carbon footprint reduction, sustainable supply chain management, circular economy implementation, stakeholder engagement, ESG reporting and compliance, green technology adoption, and social impact measurement."""

    return transcript, knowledge, "Strategic Business Leader Interview", "+1-555-0103"

def create_dashboard_test_data():
    """Create comprehensive test data for dashboard display"""
    print("🎯 Creating Dashboard Test Data")
    print("=" * 50)
    
    try:
        # Get user and existing infrastructure
        user = User.objects.get(username='Mehroz')
        assistant = InterviewAssistant.objects.filter(user=user).first()
        phone_number = PhoneNumber.objects.filter(user=user).first()
        
        if not assistant or not phone_number:
            print("❌ Need assistant and phone number configured first")
            return
        
        print(f"✅ Using assistant: {assistant.name}")
        print(f"✅ Using phone: {phone_number.phone_number}")
        
        assistant_creator = CreateAssistantView()
        test_calls = []
        
        # Create Test Call 1: Healthcare AI
        transcript1, knowledge1, title1, customer1 = create_test_call_1()
        
        call1 = InterviewCall.objects.create(
            user=user,
            vapi_call_id="test-healthcare-ai-001",
            assistant=assistant,
            phone_number=phone_number,
            customer_number=customer1,
            status="ended",
            transcript_text=transcript1,
            duration_seconds=420,  # 7 minutes
            cost=0.35,
            raw_call_data={
                "id": "test-healthcare-ai-001",
                "status": "ended",
                "endedReason": "customer-ended-call",
                "cost": 0.35,
                "duration": 420,
                "transcript": transcript1
            }
        )
        
        # Process transcript with AI
        result1 = assistant_creator.process_transcript_with_articles(transcript1, knowledge1, user=user)
        if result1.get("success"):
            call1.processed_transcript = result1["structured_output"]
            call1.save()
            print("✅ Healthcare AI call created and processed")
        
        test_calls.append(call1)
        
        # Create Test Call 2: Technology Leadership
        transcript2, knowledge2, title2, customer2 = create_test_call_2()
        
        call2 = InterviewCall.objects.create(
            user=user,
            vapi_call_id="test-tech-leadership-002",
            assistant=assistant,
            phone_number=phone_number,
            customer_number=customer2,
            status="ended",
            transcript_text=transcript2,
            duration_seconds=380,  # 6:20 minutes
            cost=0.28,
            raw_call_data={
                "id": "test-tech-leadership-002",
                "status": "ended",
                "endedReason": "customer-ended-call",
                "cost": 0.28,
                "duration": 380,
                "transcript": transcript2
            }
        )
        
        # Process transcript with AI
        result2 = assistant_creator.process_transcript_with_articles(transcript2, knowledge2, user=user)
        if result2.get("success"):
            call2.processed_transcript = result2["structured_output"]
            call2.save()
            print("✅ Technology Leadership call created and processed")
        
        test_calls.append(call2)
        
        # Create Test Call 3: Business Strategy
        transcript3, knowledge3, title3, customer3 = create_test_call_3()
        
        call3 = InterviewCall.objects.create(
            user=user,
            vapi_call_id="test-business-strategy-003",
            assistant=assistant,
            phone_number=phone_number,
            customer_number=customer3,
            status="ended",
            transcript_text=transcript3,
            duration_seconds=340,  # 5:40 minutes
            cost=0.22,
            raw_call_data={
                "id": "test-business-strategy-003",
                "status": "ended",
                "endedReason": "customer-ended-call",
                "cost": 0.22,
                "duration": 340,
                "transcript": transcript3
            }
        )
        
        # Process transcript with AI
        result3 = assistant_creator.process_transcript_with_articles(transcript3, knowledge3, user=user)
        if result3.get("success"):
            call3.processed_transcript = result3["structured_output"]
            call3.save()
            print("✅ Business Strategy call created and processed")
        
        test_calls.append(call3)
        
        print(f"\n🎉 Successfully created {len(test_calls)} test calls!")
        print("\n📊 Dashboard Test Data Summary:")
        print("-" * 40)
        
        for i, call in enumerate(test_calls, 1):
            print(f"Call {i}:")
            print(f"   📞 Customer: {call.customer_number}")
            print(f"   ⏱️  Duration: {call.duration_formatted}")
            print(f"   💰 Cost: ${call.cost}")
            print(f"   🤖 AI Processed: {'Yes' if call.processed_transcript else 'No'}")
            print(f"   📝 Transcript: {len(call.transcript_text)} characters")
            print()
        
        print("🌐 View your test data at: http://localhost:5173/dashboard")
        print("📋 Check both 'Calls' and 'Transcripts' tabs to see the AI formatting")
        
        return test_calls
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    create_dashboard_test_data()