import os
from dotenv import load_dotenv

load_dotenv(override=True)

print(f"OS ENV: {os.environ.get('OPENAI_API_KEY')}")

from config import settings
print(f"SETTINGS: {settings.OPENAI_API_KEY}")

import openai
print(f"OPENAI CLIENT KEY: {openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY).api_key}")
