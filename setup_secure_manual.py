#!/usr/bin/env python3
"""
Script to convert safety manual JSON to environment variable format
This helps keep sensitive safety information secure in deployment
"""

import json
import os
import sys

def convert_json_to_env_var():
    """Convert safety_manual.json to environment variable format"""
    
    json_file = "safety_manual.json"
    
    if not os.path.exists(json_file):
        print(f"❌ Error: {json_file} not found!")
        print("Make sure you're running this from the safetyagent directory")
        return False
    
    try:
        # Read the JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            safety_data = json.load(f)
        
        # Convert to JSON string
        safety_json_string = json.dumps(safety_data)
        
        print("✅ Safety manual JSON loaded successfully!")
        print(f"📊 Content size: {len(safety_json_string):,} characters")
        print(f"📊 Chunks: {safety_data['metadata']['total_chunks']}")
        print()
        
        # Create .env file
        env_content = f"""# Safety Agent Environment Variables
# Keep this file secure and never commit it to version control

# OpenAI API Key (required for AI features)
OPENAI_API_KEY=your-openai-api-key-here

# Safety Manual Content (secure storage)
SAFETY_MANUAL_JSON='{safety_json_string}'
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("🔒 Security Setup Complete!")
        print()
        print("📁 Files created:")
        print("   - .env (contains your API key and safety manual)")
        print()
        print("🚀 Next steps:")
        print("1. Edit .env file and add your OpenAI API key")
        print("2. Add .env to .gitignore (already done)")
        print("3. For Render deployment:")
        print("   - Add OPENAI_API_KEY as environment variable")
        print("   - Add SAFETY_MANUAL_JSON as environment variable")
        print()
        print("⚠️  IMPORTANT: Never commit .env to version control!")
        print("   The safety manual is now stored securely as an environment variable.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_render_instructions():
    """Show instructions for setting up environment variables on Render"""
    
    print("\n" + "="*60)
    print("🔒 RENDER DEPLOYMENT - SECURE SETUP")
    print("="*60)
    print()
    print("To deploy securely on Render:")
    print()
    print("1. 📝 In Render Dashboard:")
    print("   - Go to your service settings")
    print("   - Navigate to 'Environment' tab")
    print("   - Add these environment variables:")
    print()
    print("   OPENAI_API_KEY = your-actual-openai-api-key")
    print("   SAFETY_MANUAL_JSON = [the long JSON string from .env file]")
    print()
    print("2. 🔐 Security Benefits:")
    print("   ✅ Safety manual not stored in GitHub repository")
    print("   ✅ API keys not exposed in code")
    print("   ✅ Environment variables encrypted on Render")
    print("   ✅ Can be updated without code changes")
    print()
    print("3. 📋 Copy the SAFETY_MANUAL_JSON value:")
    print("   - Open the .env file")
    print("   - Copy the entire value after SAFETY_MANUAL_JSON=")
    print("   - Paste it into Render's environment variable field")
    print()

if __name__ == "__main__":
    print("🛡️  Safety Agent - Secure Setup")
    print("="*40)
    print()
    
    if convert_json_to_env_var():
        show_render_instructions()
        
        # Ask if user wants to remove the JSON file
        print("\n" + "="*60)
        response = input("🗑️  Remove safety_manual.json file for extra security? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            try:
                os.remove("safety_manual.json")
                print("✅ safety_manual.json removed for security")
                print("   The safety manual is now only stored in the .env file")
            except Exception as e:
                print(f"❌ Error removing file: {e}")
        else:
            print("ℹ️  safety_manual.json kept (you can remove it manually later)")
        
        print("\n🎉 Setup complete! Your safety manual is now secure.")
    else:
        print("❌ Setup failed. Please check the error messages above.")
        sys.exit(1)
