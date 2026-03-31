"""
DebateOS Base Agent
Abstract base class with LLM abstraction layer supporting Gemini and OpenAI.
Includes retry logic and robust JSON parsing.
"""

import json
import re
import asyncio
import logging
from pathlib import Path
from abc import ABC
from config import settings

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base agent with LLM abstraction, JSON parsing, and retry logic."""

    def __init__(self, prompt_filename: str):
        """Initialize with a prompt file from the prompts/ directory."""
        prompt_path = Path(__file__).parent.parent / "prompts" / prompt_filename
        self.system_prompt = prompt_path.read_text(encoding="utf-8")
        self._model = None
        self._openai_client = None

    def _get_gemini_model(self):
        """Lazy-load Gemini model."""
        if self._model is None:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self._model = genai.GenerativeModel(
                settings.GEMINI_MODEL,
                system_instruction=self.system_prompt,
            )
        return self._model

    def _get_openai_client(self):
        """Lazy-load OpenAI async client."""
        if self._openai_client is None:
            import openai
            self._openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        return self._openai_client

    async def call_llm(self, prompt: str, max_retries: int = 3) -> dict:
        """
        Call the configured LLM provider with retry and JSON parsing.
        Handles Gemini free-tier rate limits with longer backoff.

        Args:
            prompt: The user prompt to send.
            max_retries: Number of retries on failure.

        Returns:
            Parsed JSON dict from the LLM response.
        """
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                if settings.LLM_PROVIDER == "gemini":
                    raw_text = await self._call_gemini(prompt)
                elif settings.LLM_PROVIDER == "openai":
                    raw_text = await self._call_openai(prompt)
                else:
                    raise ValueError(f"Unknown LLM provider: {settings.LLM_PROVIDER}")

                parsed = self._parse_json(raw_text)
                if "parse_error" not in parsed:
                    return parsed

                # If parse failed but we have retries left, retry
                logger.warning(f"JSON parse failed on attempt {attempt + 1}, raw: {raw_text[:200]}")
                if attempt < max_retries:
                    await asyncio.sleep(2)
                    continue
                return parsed

            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                is_rate_limit = any(kw in error_str for kw in [
                    'quota', 'rate', '429', 'resource_exhausted', 'too many', 'retry'
                ])

                if is_rate_limit:
                    # Gemini free tier needs longer waits (up to 35s)
                    wait_time = 15 * (attempt + 1)  # 15s, 30s, 45s
                    logger.warning(f"Rate limited (attempt {attempt + 1}). Waiting {wait_time}s...")
                    if attempt < max_retries:
                        await asyncio.sleep(wait_time)
                        continue
                else:
                    logger.error(f"LLM call failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    if attempt < max_retries:
                        await asyncio.sleep(3 * (attempt + 1))

        # All retries exhausted
        logger.error(f"All LLM retries exhausted. Last error: {last_error}")
        with open('backend_last_llm_error.txt', 'w', encoding='utf-8') as err_file:
            err_file.write(f"PROMPT: {prompt[:100]}...\nERROR: {last_error}")
        return {"error": str(last_error), "parse_error": True}

    async def _call_gemini(self, prompt: str) -> str:
        """Call Google Gemini API (sync API wrapped in thread)."""
        model = self._get_gemini_model()
        response = await asyncio.to_thread(
            model.generate_content,
            prompt,
            generation_config={"temperature": 0.7, "max_output_tokens": 1024},
        )
        return response.text

    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API (native async)."""
        client = self._get_openai_client()
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1024,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content

    @staticmethod
    def _parse_json(text: str) -> dict:
        """
        Robust JSON parsing with multiple fallback strategies.
        Handles raw JSON, markdown-wrapped JSON, and embedded JSON.
        """
        if not text:
            return {"error": "Empty response", "parse_error": True}

        text = text.strip()

        # Strategy 1: Direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Strategy 2: Extract from markdown code block
        code_block = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if code_block:
            try:
                return json.loads(code_block.group(1))
            except json.JSONDecodeError:
                pass

        # Strategy 3: Find the largest JSON object in text
        # Match nested braces up to 3 levels deep
        json_pattern = r'\{[^{}]*(?:\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        if matches:
            # Try the longest match first (most likely to be the full response)
            for match in sorted(matches, key=len, reverse=True):
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue

        # Strategy 4: Return raw text as fallback
        return {"raw_text": text, "parse_error": True}
