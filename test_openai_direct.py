#!/usr/bin/env python3
"""
Direct test of OpenAI client without Django
"""
import openai

def test_direct_openai():
    """Test OpenAI client directly"""
    print("🔧 Direct OpenAI Client Test")
    print("=" * 30)
    
    # Replace with your actual OpenAI API key
    api_key = "YOUR_OPENAI_API_KEY"
    
    try:
        print(f"OpenAI version: {openai.__version__}")
        
        # Test 1: Basic client creation
        print("🔄 Creating OpenAI client...")
        client = openai.OpenAI(api_key=api_key)
        print("✅ Client created successfully")
        
        # Test 2: Simple API call
        print("🔄 Making API call...")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": "Say 'Hello, this is a test!' and nothing else."}
            ],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ API call successful: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e)}")
        return False

if __name__ == "__main__":
    test_direct_openai()