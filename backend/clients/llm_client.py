import asyncio
import logging
from abc import ABC, abstractmethod

from backend.config import settings

logger = logging.getLogger(__name__)


class BaseLLMClient(ABC):
    MAX_RETRIES = 3
    RETRY_DELAYS = [2, 4, 8]

    @abstractmethod
    async def _complete_once(self, prompt: str, max_tokens: int) -> str:
        pass

    async def complete(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.1,
    ) -> str:
        last_error = None
        for attempt, delay in enumerate(self.RETRY_DELAYS):
            try:
                result = await self._complete_once(prompt, max_tokens)
                return result
            except Exception as e:
                last_error = e
                logger.warning(f"LLM attempt {attempt + 1} failed: {e}")
                if attempt < len(self.RETRY_DELAYS) - 1:
                    await asyncio.sleep(delay)

        raise RuntimeError(f"LLM failed after {self.MAX_RETRIES} retries: {last_error}")


class GroqClient(BaseLLMClient):
    MODEL = "llama-3.3-70b-versatile"

    def __init__(self):
        from groq import AsyncGroq

        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    async def _complete_once(self, prompt: str, max_tokens: int) -> str:
        response = await self.client.chat.completions.create(
            model=self.MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.1,
            timeout=30.0,
        )
        return response.choices[0].message.content


class ClaudeClient(BaseLLMClient):
    MODEL = "claude-sonnet-4-6"

    def __init__(self):
        import anthropic

        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def _complete_once(self, prompt: str, max_tokens: int) -> str:
        response = await self.client.messages.create(
            model=self.MODEL,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        return response.content[0].text


class MockLLMClient(BaseLLMClient):
    def __init__(self, response: str = '{"queries": ["test query"]}'):
        self._response = response

    async def _complete_once(self, prompt: str, max_tokens: int) -> str:
        return self._response


def get_llm_client() -> BaseLLMClient:
    provider = settings.LLM_PROVIDER.lower()
    if provider == "groq":
        return GroqClient()
    elif provider == "claude":
        return ClaudeClient()
    elif provider == "mock":
        return MockLLMClient()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
