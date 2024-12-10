import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN")
OPEN_CAGE_API_KEY = os.getenv("OPEN_CAGE_API_KEY")
OPEN_CAGE_URL = os.getenv("OPEN_CAGE_URL", "https://api.opencagedata.com/geocode/v1/json")
