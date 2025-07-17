import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Admin Telegram IDs (comma separated list)
ADMIN_IDS = [
    int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x
]

# Database
DATABASE_PATH = "bot_database.db"

# File paths
MEMORY_PAGES_DIR = "memory_pages"
TEMPLATES_DIR = "templates"

# Create directories if they don't exist
os.makedirs(MEMORY_PAGES_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True) 
