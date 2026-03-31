"""Quick test of Gemini API connectivity."""
import warnings
warnings.filterwarnings("ignore")

from config import settings
import google.generativeai as genai

print(f"Provider: {settings.LLM_PROVIDER}")
print(f"Model: {settings.GEMINI_MODEL}")
print(f"API Key: {settings.GEMINI_API_KEY[:10]}...{settings.GEMINI_API_KEY[-4:]}")

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel(settings.GEMINI_MODEL)

print("\nCalling Gemini API...")
try:
    response = model.generate_content("Say hello in exactly 3 words.")
    print(f"SUCCESS: {response.text}")
except Exception as e:
    err_msg = f"ERROR: {type(e).__name__}: {e}"
    print(err_msg)
    with open('debug_api.txt', 'w', encoding='utf-8') as f:
        f.write(err_msg)
