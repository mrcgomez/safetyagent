#!/usr/bin/env python3
"""
Setup script for OpenAI API key
"""

import os
import sys

def setup_openai_key():
    """Interactive setup for OpenAI API key"""
    print("🛡️  SafetyAgent AI - OpenAI Setup")
    print("=" * 50)
    
    # Check if key is already set
    existing_key = os.getenv('OPENAI_API_KEY')
    if existing_key:
        print(f"✅ OpenAI API key is already set: {existing_key[:8]}...")
        response = input("Do you want to update it? (y/n): ").lower().strip()
        if response != 'y':
            print("Keeping existing API key.")
            return existing_key
    
    print("\n📝 To get your OpenAI API key:")
    print("1. Go to https://platform.openai.com/api-keys")
    print("2. Sign in to your OpenAI account")
    print("3. Click 'Create new secret key'")
    print("4. Copy the key (it starts with 'sk-')")
    print()
    
    api_key = input("Enter your OpenAI API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided.")
        return None
    
    if not api_key.startswith('sk-'):
        print("⚠️  Warning: OpenAI API keys usually start with 'sk-'")
        response = input("Continue anyway? (y/n): ").lower().strip()
        if response != 'y':
            return None
    
    # Set the environment variable for current session
    os.environ['OPENAI_API_KEY'] = api_key
    
    # Create .env file for future sessions
    env_file = '.env'
    with open(env_file, 'w') as f:
        f.write(f"OPENAI_API_KEY={api_key}\n")
    
    print(f"✅ API key saved to {env_file}")
    print("✅ Environment variable set for current session")
    
    return api_key

def test_openai_connection(api_key):
    """Test the OpenAI connection"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, this is a test."}],
            max_tokens=10
        )
        
        print("✅ OpenAI connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        return False

if __name__ == "__main__":
    api_key = setup_openai_key()
    
    if api_key:
        print("\n🧪 Testing OpenAI connection...")
        if test_openai_connection(api_key):
            print("\n🎉 Setup complete! You can now start the SafetyAgent AI with OpenAI integration.")
            print("\nTo start the server:")
            print("  python simple_server.py")
        else:
            print("\n❌ Setup failed. Please check your API key and try again.")
    else:
        print("\n⚠️  Setup cancelled. The SafetyAgent will work with basic keyword search.")
        print("You can run this script again later to add OpenAI integration.")
