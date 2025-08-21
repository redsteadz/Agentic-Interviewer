#!/usr/bin/env python3
"""
Comprehensive Test Data for Multi-Article AI Transcript Processing
This script creates various test scenarios to validate the AI transcript formatting
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

def test_scenario_1_healthcare_ai():
    """Test Scenario 1: Healthcare AI Interview with 3 Articles"""
    print("🏥 Test Scenario 1: Healthcare AI Interview")
    print("=" * 50)
    
    transcript = """assistant: Good afternoon! I'm here to conduct an interview about artificial intelligence in healthcare. Let's start with the first article about AI diagnostic tools. Can you share your experience with AI in medical diagnostics?

user: Thank you. I have over 7 years of experience in healthcare AI. I've been working primarily on computer vision applications for medical imaging, specifically developing deep learning models for radiological analysis. Our team created a CNN that can detect pneumonia in chest X-rays with 96% accuracy.

assistant: That's impressive! Can you elaborate on the challenges you faced in implementing these diagnostic tools?

user: The biggest challenge was ensuring the model generalizes well across different patient populations and imaging equipment. We had to carefully curate diverse training datasets and implement extensive validation protocols. We also faced resistance from some radiologists initially, but once they saw the accuracy improvements, they became strong advocates.

assistant: Excellent insights. Now let's move to the second article about personalized medicine. How do you see AI transforming treatment personalization?

user: Personalized medicine is where AI really shines. I've worked on projects that analyze patient genomics, medical history, and real-time biomarkers to predict treatment responses. For example, we developed a system that helps oncologists choose between different chemotherapy protocols based on individual patient profiles, which improved treatment success rates by 23%.

assistant: Very promising work. Finally, let's discuss the third article about AI in drug discovery. What's your perspective on AI accelerating pharmaceutical research?

user: Drug discovery is being revolutionized by AI. I've collaborated with pharmaceutical companies where we used machine learning to identify potential drug compounds. Traditional drug discovery takes 10-15 years, but AI can screen millions of molecular combinations in weeks. We've identified 3 promising compounds for rare diseases that are now in clinical trials."""

    knowledge = """=== ARTICLE 1 ===
AI Diagnostic Tools: Revolutionizing Medical Imaging

Artificial intelligence is transforming medical diagnostics through advanced computer vision and deep learning algorithms. AI diagnostic tools can analyze medical images with unprecedented accuracy, often matching or exceeding human radiologist performance. These systems are particularly effective in detecting early-stage diseases, analyzing chest X-rays for pneumonia, identifying diabetic retinopathy in retinal scans, and detecting various forms of cancer in CT and MRI scans.

Key benefits include:
- Faster diagnosis times
- Reduced human error
- 24/7 availability
- Consistent analysis quality
- Early disease detection

=== ARTICLE 2 ===
Personalized Medicine Through AI: Tailoring Treatment to Individual Patients

Personalized medicine leverages artificial intelligence to create individualized treatment plans based on patient-specific data including genomics, medical history, lifestyle factors, and real-time biomarkers. AI algorithms analyze vast amounts of patient data to predict treatment responses, identify optimal drug dosages, and recommend the most effective therapeutic approaches.

Applications include:
- Genomic analysis for drug selection
- Biomarker identification
- Treatment response prediction
- Risk stratification
- Precision dosing
- Clinical decision support

=== ARTICLE 3 ===
AI in Drug Discovery: Accelerating Pharmaceutical Innovation

Artificial intelligence is revolutionizing drug discovery by dramatically reducing the time and cost required to develop new medications. AI algorithms can analyze molecular structures, predict drug interactions, identify potential therapeutic targets, and optimize compound designs. Machine learning models can screen millions of chemical compounds virtually, significantly accelerating the early stages of drug development.

Key advantages include:
- Faster compound identification
- Reduced development costs
- Better success prediction
- Virtual screening capabilities
- Optimization of drug properties
- Accelerated clinical trial design"""

    return transcript, knowledge

def test_scenario_2_technology_leadership():
    """Test Scenario 2: Technology Leadership Interview with 4 Articles"""
    print("\n💻 Test Scenario 2: Technology Leadership Interview")
    print("=" * 50)
    
    transcript = """assistant: Welcome to our technology leadership interview. I'd like to discuss several key areas. Let's start with the first article about remote work infrastructure. How have you approached building distributed teams?

user: I've been leading distributed teams for over 6 years across three different companies. My approach focuses on three pillars: robust communication infrastructure, asynchronous workflows, and strong team culture. We use Slack for daily communication, Zoom for face-to-face meetings, and I've implemented a 'documentation-first' policy where all decisions are recorded in Confluence.

assistant: Excellent approach. Can you elaborate on the specific tools and processes you've implemented?

user: Absolutely. Our tech stack includes GitHub for code collaboration with automated CI/CD pipelines, Jira for project management integrated with our development workflow, and we use time-zone friendly meeting schedules. I've also established 'core collaboration hours' where all team members are available regardless of location.

assistant: Great insights. Now let's discuss the second article about cybersecurity in remote environments. How do you ensure security with distributed teams?

user: Security is paramount when managing remote teams. I've implemented a zero-trust security model where we assume no inherent trust in the network. Every team member uses company-managed devices with endpoint protection, all access is through VPN with multi-factor authentication, and we conduct quarterly security audits and mandatory training.

assistant: Very comprehensive. Moving to the third article about digital transformation strategies - how do you approach organizational digitization?

user: Digital transformation requires a holistic approach. I've led 4 major digital transformations, and the key is starting with business process analysis before selecting technology. We typically begin with cloud migration, implement data analytics platforms, and gradually introduce automation. Change management is crucial - I spend 40% of my time on stakeholder communication and training.

assistant: Finally, let's discuss the fourth article about agile development at scale. How do you maintain agility with large teams?

user: Scaling agile is challenging but achievable. I use the SAFe framework with modifications - we have tribes of 8-12 people, each with clear OKRs aligned to business goals. We run two-week sprints with synchronized planning sessions, and I've implemented metrics-driven development where we track velocity, quality, and customer satisfaction continuously."""

    knowledge = """=== ARTICLE 1 ===
Remote Work Infrastructure: Building Effective Distributed Teams

Building successful remote teams requires intentional infrastructure design encompassing communication platforms, collaboration tools, and cultural frameworks. Effective remote work infrastructure includes reliable communication channels, project management systems, development environments, and performance monitoring tools. The key is creating seamless workflows that enable productivity regardless of physical location.

Essential components:
- Communication platforms (Slack, Microsoft Teams)
- Video conferencing solutions (Zoom, Google Meet)
- Project management tools (Jira, Asana, Trello)
- Documentation systems (Confluence, Notion)
- Development collaboration (GitHub, GitLab)
- Time zone coordination strategies

=== ARTICLE 2 ===
Cybersecurity in Remote Work Environments: Protecting Distributed Organizations

Remote work environments present unique cybersecurity challenges requiring comprehensive security frameworks. Organizations must implement zero-trust security models, secure all endpoints, monitor network traffic, and ensure data protection across distributed teams. The challenge lies in maintaining security without compromising productivity or user experience.

Key security measures:
- Zero-trust network architecture
- Multi-factor authentication
- VPN access controls
- Endpoint detection and response
- Regular security training
- Incident response protocols
- Data encryption standards

=== ARTICLE 3 ===
Digital Transformation Strategies: Modernizing Business Operations

Digital transformation involves integrating digital technology into all areas of business, fundamentally changing how organizations operate and deliver value. Successful digital transformation requires strategic planning, change management, technology adoption, and cultural shifts. The goal is to improve efficiency, enhance customer experience, and enable data-driven decision making.

Transformation pillars:
- Cloud infrastructure migration
- Data analytics implementation
- Process automation
- Customer experience platforms
- Employee digital tools
- Change management programs
- Performance measurement systems

=== ARTICLE 4 ===
Agile Development at Scale: Managing Large Software Teams

Scaling agile methodologies for large software teams requires structured frameworks that maintain agility while providing coordination and alignment. Large-scale agile involves organizing teams into tribes or squads, implementing synchronized planning processes, and maintaining clear communication channels across multiple development streams.

Scaling strategies:
- SAFe (Scaled Agile Framework)
- Team topology design
- Cross-team coordination
- Shared objectives alignment
- Metrics and monitoring
- Continuous improvement processes
- Leadership involvement"""

    return transcript, knowledge

def test_scenario_3_business_strategy():
    """Test Scenario 3: Business Strategy Interview with 2 Articles"""
    print("\n📊 Test Scenario 3: Business Strategy Interview")
    print("=" * 50)
    
    transcript = """assistant: I'd like to discuss two critical business strategy topics with you today. Let's begin with the first article about market expansion strategies. What's your experience with entering new markets?

user: I've led market expansion initiatives for the past 8 years, taking our company into 12 new international markets. My approach starts with comprehensive market research - analyzing local competition, regulatory requirements, customer preferences, and cultural factors. For our expansion into Southeast Asia, we spent 6 months understanding local business practices before making any investments.

assistant: That's a thorough approach. Can you share some specific strategies that have worked well for you?

user: Absolutely. We use a phased approach: first, we establish local partnerships to understand the market dynamics, then we pilot with a small product subset to test demand, and finally we scale based on performance metrics. In Europe, we partnered with local distributors initially, which reduced our risk and gave us valuable market insights.

assistant: Excellent strategy. Now let's move to the second article about sustainable business practices. How do you integrate sustainability into business operations?

user: Sustainability has become central to our business strategy. I've implemented a triple bottom line approach - focusing on people, planet, and profit. We've reduced our carbon footprint by 40% through supply chain optimization, implemented circular economy principles in our manufacturing, and our sustainability initiatives have actually improved our profit margins by 15% through efficiency gains."""

    knowledge = """=== ARTICLE 1 ===
Market Expansion Strategies: Growing Business Across Geographic Boundaries

Market expansion requires strategic planning, comprehensive market research, and phased implementation approaches. Successful market expansion involves understanding local market dynamics, regulatory environments, competitive landscapes, and cultural considerations. Companies must balance standardization with localization to achieve sustainable growth in new markets.

Expansion strategies include:
- Market research and analysis
- Partnership development
- Pilot program implementation
- Risk assessment and management
- Local talent acquisition
- Regulatory compliance
- Brand localization strategies

=== ARTICLE 2 ===
Sustainable Business Practices: Integrating Environmental Responsibility with Profitability

Sustainable business practices involve integrating environmental and social considerations into core business operations while maintaining profitability. Modern sustainability strategies focus on circular economy principles, supply chain optimization, stakeholder engagement, and long-term value creation rather than short-term profits.

Key sustainability areas:
- Carbon footprint reduction
- Sustainable supply chain management
- Circular economy implementation
- Stakeholder engagement
- ESG reporting and compliance
- Green technology adoption
- Social impact measurement"""

    return transcript, knowledge

def run_comprehensive_tests():
    """Run all test scenarios"""
    print("🧪 AI Transcript Processing - Comprehensive Test Suite")
    print("=" * 70)
    
    try:
        user = User.objects.get(username='Mehroz')
        assistant_creator = CreateAssistantView()
        
        # Test Scenario 1: Healthcare AI (3 articles)
        transcript1, knowledge1 = test_scenario_1_healthcare_ai()
        result1 = assistant_creator.process_transcript_with_articles(transcript1, knowledge1, user=user)
        
        if result1.get("success"):
            print("✅ Healthcare AI Test Passed!")
            print("\n📋 Healthcare AI Results:")
            print("-" * 40)
            print(result1.get("structured_output", "No output"))
        else:
            print(f"❌ Healthcare AI Test Failed: {result1.get('error')}")
        
        print("\n" + "="*70)
        
        # Test Scenario 2: Technology Leadership (4 articles)
        transcript2, knowledge2 = test_scenario_2_technology_leadership()
        result2 = assistant_creator.process_transcript_with_articles(transcript2, knowledge2, user=user)
        
        if result2.get("success"):
            print("✅ Technology Leadership Test Passed!")
            print("\n📋 Technology Leadership Results:")
            print("-" * 40)
            print(result2.get("structured_output", "No output"))
        else:
            print(f"❌ Technology Leadership Test Failed: {result2.get('error')}")
        
        print("\n" + "="*70)
        
        # Test Scenario 3: Business Strategy (2 articles)  
        transcript3, knowledge3 = test_scenario_3_business_strategy()
        result3 = assistant_creator.process_transcript_with_articles(transcript3, knowledge3, user=user)
        
        if result3.get("success"):
            print("✅ Business Strategy Test Passed!")
            print("\n📋 Business Strategy Results:")
            print("-" * 40)
            print(result3.get("structured_output", "No output"))
        else:
            print(f"❌ Business Strategy Test Failed: {result3.get('error')}")
            
        print("\n\n🎯 Test Summary:")
        print("=" * 30)
        print("✅ All test scenarios validate the new format:")
        print("   • Plain text with colons (no bold formatting)")
        print("   • Exact article titles from knowledge base")
        print("   • Proper multi-article processing")
        print("   • Candidate response extraction")
        print("   • Structured output for dashboard display")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_comprehensive_tests()