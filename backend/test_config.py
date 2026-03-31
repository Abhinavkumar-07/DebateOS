from config import settings
print("=== DEBATE OS CONFIG CHECK ===")
print(f"LLM_PROVIDER: '{settings.LLM_PROVIDER}'")
print(f"OPENAI_API_KEY: '{settings.OPENAI_API_KEY[:5]}...{settings.OPENAI_API_KEY[-5:]}'")
print(f"GEMINI_API_KEY: '{settings.GEMINI_API_KEY[:5]}...{settings.GEMINI_API_KEY[-5:]}'")
print(f"OPENAI_MODEL: '{settings.OPENAI_MODEL}'")
print("==============================")
