import traceback
from config import settings
import google.generativeai as genai

genai.configure(api_key=settings.GEMINI_API_KEY)
try:
    print("Testing 2.5-flash...")
    response = genai.GenerativeModel('gemini-2.5-flash').generate_content('Say hello.')
    print("SUCCESS: ", response.text)
except Exception as e:
    with open('last_api_error.txt', 'w') as f:
        f.write(traceback.format_exc())
    print("FAILED")
