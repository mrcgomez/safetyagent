# 🚀 Safety Agent - Deployment Guide

## Render Deployment Instructions

### 1. GitHub Setup
1. Create a new GitHub repository
2. Push this code to the repository
3. Connect the repository to Render

### 2. Render Configuration
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Use these settings:
   - **Name:** safety-agent
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python simple_server.py`
   - **Plan:** Free

### 3. Environment Variables
Add these environment variables in Render:
- `OPENAI_API_KEY` - Your OpenAI API key (starts with sk-)
- `PORT` - Will be set automatically by Render

### 4. Files Included
- ✅ `simple_server.py` - Main application
- ✅ `requirements.txt` - Python dependencies
- ✅ `safety_manual.json` - Safety manual data
- ✅ `Procfile` - Process configuration
- ✅ `render.yaml` - Render configuration
- ✅ `.env` - Local environment variables (not deployed)

### 5. Deployment
1. Click "Create Web Service"
2. Wait for build to complete
3. Your Safety Agent will be available at the provided URL

### 6. Testing
Once deployed, test these endpoints:
- Main app: `https://your-app-name.onrender.com`
- Health check: `https://your-app-name.onrender.com/health`
- API stats: `https://your-app-name.onrender.com/api/stats`

## Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export OPENAI_API_KEY="your-api-key-here"

# Run locally
python simple_server.py
```

## Features
- ✅ AI-powered safety Q&A
- ✅ SoCalGas branding
- ✅ Mobile responsive
- ✅ Real-time chat interface
- ✅ Safety manual knowledge base
