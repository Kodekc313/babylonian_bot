import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the bot token from the environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Check if the bot token is loaded
if BOT_TOKEN is None:
    raise ValueError("BOT_TOKEN not found in the .env file or environment variables!")