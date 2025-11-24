import sys
import os
import importlib

def check_import(module_name):
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name} imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import {module_name}: {e}")
        return False

def check_env_file():
    if os.path.exists(".env"):
        print("✅ .env file exists")
    elif os.path.exists(".env.example"):
        print("⚠️ .env file missing, but .env.example exists. Please copy .env.example to .env and fill in your keys.")
    else:
        print("❌ No .env or .env.example found")

# Map of package name to import name
required_modules = {
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "streamlit": "streamlit",
    "supabase": "supabase",
    "sentence-transformers": "sentence_transformers",
    "groq": "groq",
    "resend": "resend",
    "python-dotenv": "dotenv",
    "apscheduler": "apscheduler",
    "trafilatura": "trafilatura",
    "youtube-transcript-api": "youtube_transcript_api",
    "beautifulsoup4": "bs4"
}

print("--- Verifying Setup ---")
print(f"Python Executable: {sys.executable}")

all_good = True
for package, module in required_modules.items():
    if not check_import(module):
        all_good = False

check_env_file()

if all_good:
    print("\n🎉 Setup verification PASSED!")
else:
    print("\n❌ Setup verification FAILED. Please check errors above.")
