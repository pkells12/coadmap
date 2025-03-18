# config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API settings
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = "claude-3-7-sonnet-20250219"  # Latest Claude model

# App settings
APP_NAME = "Coadmap"
APP_VERSION = "1.0.0"
MAX_TOKENS = 30000  # Increased to ensure we can get 6000-8000 token roadmaps