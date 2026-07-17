import time
import logging

from groq import Groq, APIStatusError, APIConnectionError

from llm.provider import LLMProvider
from config.settings import Settings

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_BACKOFF = 2


class GroqProvider(LLMProvider):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or Settings.GROQ_API_KEY
        self.model = model or Settings.GROQ_MODEL
        self.client = Groq(api_key=self.api_key)

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = None,
        max_tokens: int = None,
    ) -> str:
        temperature = temperature if temperature is not None else Settings.DEFAULT_TEMPERATURE
        max_tokens = max_tokens or Settings.MAX_TOKENS

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content or ""
            except APIConnectionError as e:
                last_error = e
                logger.warning(f"Groq connection error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_BACKOFF ** attempt)
            except APIStatusError as e:
                if e.status_code == 429:
                    last_error = e
                    logger.warning(f"Groq rate limit hit (attempt {attempt + 1}/{MAX_RETRIES})")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_BACKOFF ** (attempt + 1))
                elif e.status_code in (401, 403):
                    raise RuntimeError(f"Invalid or unauthorized Groq API key. Status: {e.status_code}") from e
                else:
                    last_error = e
                    logger.error(f"Groq API error {e.status_code}: {e.message}")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_BACKOFF ** attempt)
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error calling Groq: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_BACKOFF ** attempt)

        raise RuntimeError(f"Failed to get response from Groq after {MAX_RETRIES} attempts: {last_error}")
