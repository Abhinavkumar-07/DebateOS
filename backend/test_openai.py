"""Quick test of OpenAI API connectivity."""
import warnings
import asyncio
warnings.filterwarnings("ignore")

from config import settings

async def main():
    print(f"Provider: {settings.LLM_PROVIDER}")
    if settings.LLM_PROVIDER != 'openai':
        print("Not configured for OpenAI!")
        return
        
    print(f"Model: {settings.OPENAI_MODEL}")
    import openai
    client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    print("\nCalling OpenAI API...")
    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": "Say hello in exactly 3 words."}],
            temperature=0.7,
            max_tokens=10
        )
        print(f"SUCCESS: {response.choices[0].message.content}")
    except Exception as e:
        err_msg = f"ERROR: {type(e).__name__}: {e}"
        print(err_msg)
        with open('debug_openai.txt', 'w', encoding='utf-8') as f:
            f.write(err_msg)

if __name__ == "__main__":
    asyncio.run(main())
