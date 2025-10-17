#!/usr/bin/env python3
"""
SafetyAgent AI - Startup Script
Quick start script for development and testing
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    try:
        import fastapi
        import langchain
        import chromadb
        import openai
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def check_openai_key():
    """Check if OpenAI API key is set"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your_api_key_here'")
        return False
    else:
        print("✅ OpenAI API key is configured")
        return True

def create_directories():
    """Create necessary directories"""
    directories = ["data", "data/chroma_db", "data/uploads"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    print("✅ Data directories created")

def main():
    """Main startup function"""
    print("🛡️  SafetyAgent AI - Starting up...")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check OpenAI key
    if not check_openai_key():
        print("\nYou can still start the server, but AI features won't work without an API key.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Check for safety manual
    safety_manual = Path("EmployeeSafetyManual.docx")
    if safety_manual.exists():
        print(f"✅ Found safety manual: {safety_manual}")
    else:
        print("⚠️  No safety manual found. You can upload documents via the web interface.")
    
    print("\n🚀 Starting SafetyAgent AI server...")
    print("📱 Open your browser to: http://localhost:8000")
    print("💬 Click the chat icon in the bottom-left corner to start chatting!")
    print("📚 Upload your safety documents using the upload button")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the server
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "backend.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 SafetyAgent AI stopped. Goodbye!")

if __name__ == "__main__":
    main()
