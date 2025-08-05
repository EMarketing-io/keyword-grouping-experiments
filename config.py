import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4.1-2025-04-14"
BATCH_SIZE = 30
TEMPERATURE = 0.0
MAX_RETRIES = 3