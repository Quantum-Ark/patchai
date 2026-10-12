"""
Interchangeable LLM Provider Adapter for PatchPilot AI.
Supports real LLM providers (OpenAI, Gemini, Anthropic, Groq, OpenRouter) with strict authentication verification.
Deterministic Mock provider is restricted to isolated unit tests and explicit offline flags.
Never silently falls back to Mock in a live repair run.
"""

import os
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from patchpilot.config import config


class BaseLLMProvider(ABC):
    provider_name: str = "base"
    model_name: str = "unknown"

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate a response from the LLM provider."""
        pass

    def health_check(self) -> Dict[str, Any]:
        """
        Executes a minimal test request to verify genuine connectivity and credentials.
        Returns latency and confirmation without leaking secrets.
        """
        t0 = time.time()
        try:
            resp = self.generate(
                prompt="Respond with exact single word: PONG",
                system_prompt="You are a health check agent."
            )
            elapsed = time.time() - t0
            return {
                "ok": True,
                "provider": self.provider_name,
                "model": self.model_name,
                "latency_seconds": round(elapsed, 3),
                "response_sample": resp.strip()[:60]
            }
        except Exception as e:
            elapsed = time.time() - t0
            return {
                "ok": False,
                "provider": self.provider_name,
                "model": self.model_name,
                "latency_seconds": round(elapsed, 3),
                "error": str(e)
            }


class OpenAIProvider(BaseLLMProvider):
    provider_name: str = "OpenAI"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or config.openai_api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.model_name = model or os.getenv("OPENAI_MODEL") or config.model or "gpt-4o"

        if not self.api_key or self.api_key in ("your_openai_api_key_here", "<your-key>"):
            raise ValueError(
                "OPENAI_API_KEY is not configured or contains placeholder.\n"
                "Please configure OPENAI_API_KEY in your local .env file."
            )

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.2,
        )
        return response.choices[0].message.content or ""


class GeminiProvider(BaseLLMProvider):
    provider_name: str = "Gemini"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = (
            api_key
            or config.gemini_api_key
            or os.getenv("GEMINI_API_KEY", "")
            or os.getenv("GOOGLE_API_KEY", "")
        )
        self.model_name = model or os.getenv("GEMINI_MODEL") or config.model or "gemini-2.0-flash"

        if not self.api_key or self.api_key in ("your_gemini_api_key_here", "<your-key>"):
            raise ValueError(
                "GEMINI_API_KEY is not configured or contains placeholder.\n"
                "Please configure GEMINI_API_KEY in your local .env file."
            )

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        from google import genai

        client = genai.Client(api_key=self.api_key)
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        response = client.models.generate_content(
            model=self.model_name,
            contents=full_prompt,
        )
        return response.text or ""


class AnthropicProvider(BaseLLMProvider):
    provider_name: str = "Anthropic"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = (
            api_key
            or config.anthropic_api_key
            or os.getenv("ANTHROPIC_API_KEY", "")
            or os.getenv("ANTHROPIC_AUTH_TOKEN", "")
        )
        self.base_url = base_url or os.getenv("ANTHROPIC_BASE_URL")
        self.model_name = model or os.getenv("ANTHROPIC_MODEL") or config.model or "claude-3-5-sonnet-20241022"

        if not self.api_key or self.api_key in ("your_anthropic_api_key_here", "<your-key>"):
            raise ValueError(
                "ANTHROPIC_API_KEY is not configured or contains placeholder.\n"
                "Please configure ANTHROPIC_API_KEY in your local .env file."
            )

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        import anthropic

        client = anthropic.Anthropic(api_key=self.api_key, base_url=self.base_url)
        response = client.messages.create(
            model=self.model_name,
            max_tokens=4096,
            system=system_prompt or "You are PatchPilot AI, an autonomous software repair engineer.",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return "".join(b.text for b in response.content if hasattr(b, "text"))


class GroqProvider(BaseLLMProvider):
    provider_name: str = "Groq"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.model_name = model or os.getenv("GROQ_MODEL") or "llama-3.3-70b-versatile"

        if not self.api_key or self.api_key.startswith("gsk_test") or self.api_key.startswith("gsk_live_c8a40020051b700712151833534e629c5c511e76373091876061517810"):
            raise ValueError(
                "GROQ_API_KEY is not configured or invalid. Please configure a valid GROQ_API_KEY from console.groq.com/keys in your local .env file."
            )

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        from openai import OpenAI

        client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.2,
        )
        return response.choices[0].message.content or ""


class OpenRouterProvider(BaseLLMProvider):
    provider_name: str = "OpenRouter"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        self.model_name = model or os.getenv("OPENROUTER_MODEL") or "openai/gpt-4o-mini"

        if not self.api_key or self.api_key in ("your_openrouter_api_key_here", "<your-key>"):
            raise ValueError(
                "OPENROUTER_API_KEY is not configured. Please configure OPENROUTER_API_KEY in your local .env file."
            )

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        from openai import OpenAI

        client = OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.2,
        )
        return response.choices[0].message.content or ""


class MockLLMProvider(BaseLLMProvider):
    """
    Deterministic Mock LLM Provider restricted to isolated unit tests.
    Must never be used as a silent fallback for real repair commands.
    """
    provider_name: str = "Mock (Test Only)"
    model_name: str = "deterministic-mock-v1"

    def __init__(
        self,
        custom_responses: Optional[Dict[str, str]] = None,
        sequential_patches: Optional[List[str]] = None
    ):
        self.custom_responses = custom_responses or {}
        self.sequential_patches = sequential_patches or []
        self._patch_idx = 0
        self.call_history = []

    def register_response(self, prompt_keyword: str, response: str):
        self.custom_responses[prompt_keyword] = response

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        self.call_history.append({"prompt": prompt, "system": system_prompt})

        # Check sequential patches if prompt is asking for code patch
        if ("generate code replacement" in prompt.lower() or "generate_patch" in prompt.lower() or "code patch" in prompt.lower()) and self._patch_idx < len(self.sequential_patches):
            res = self.sequential_patches[self._patch_idx]
            self._patch_idx += 1
            return res

        # Match registered keywords
        for keyword, response in self.custom_responses.items():
            if keyword.lower() in prompt.lower():
                return response

        # Default structured fallback response
        if "investigate" in prompt.lower() or "root cause" in prompt.lower():
            return (
                "HYPOTHESIS: Missing edge-case boundary check.\n"
                "RELEVANT_FILES: src/calculator.py\n"
                "PROPOSED_SOLUTION: Add conditional check for negative zero.\n"
                "TEST_STRATEGY: Execute unit tests with boundary parameters."
            )

        if "patch" in prompt.lower() or "fix" in prompt.lower():
            return (
                "TARGET_FILE: src/calculator.py\n"
                "ORIGINAL_CODE: return x / y\n"
                "PATCHED_CODE: if y == 0: raise ZeroDivisionError('Cannot divide by zero')\nreturn x / y"
            )

        return "Mock response: Analysis and patch completed successfully."


def get_llm_provider(name: Optional[str] = None) -> BaseLLMProvider:
    """
    Returns an authenticated LLM provider.
    Fails explicitly if credentials are missing. NEVER silently falls back to Mock.
    """
    target = (name or os.getenv("PATCHPILOT_PROVIDER", "")).strip().lower()

    if target == "mock":
        return MockLLMProvider()

    if target == "openai":
        return OpenAIProvider()

    if target == "gemini":
        return GeminiProvider()

    if target == "anthropic":
        return AnthropicProvider()

    if target == "groq":
        return GroqProvider()

    if target == "openrouter":
        return OpenRouterProvider()

    # If no provider explicitly specified, auto-detect configured live credentials
    openai_key = os.getenv("OPENAI_API_KEY", "") or config.openai_api_key
    if openai_key and openai_key not in ("your_openai_api_key_here", "<your-key>"):
        return OpenAIProvider()

    gemini_key = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "") or config.gemini_api_key
    if gemini_key and gemini_key not in ("your_gemini_api_key_here", "<your-key>"):
        return GeminiProvider()

    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "") or config.anthropic_api_key
    if anthropic_key and anthropic_key not in ("your_anthropic_api_key_here", "<your-key>"):
        return AnthropicProvider()

    groq_key = os.getenv("GROQ_API_KEY", "")
    if groq_key and groq_key not in ("your_groq_api_key_here", "<your-key>"):
        return GroqProvider()

    openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
    if openrouter_key and openrouter_key not in ("your_openrouter_api_key_here", "<your-key>"):
        return OpenRouterProvider()

    # Fail explicitly with actionable instructions
    raise RuntimeError(
        "No live LLM provider credentials configured.\n"
        "Please configure one of the following in your local .env file:\n"
        "  - OPENAI_API_KEY=<your-api-key>\n"
        "  - GEMINI_API_KEY=<your-api-key>\n"
        "  - ANTHROPIC_API_KEY=<your-api-key>\n"
        "  - GROQ_API_KEY=<your-api-key>\n"
        "  - OPENROUTER_API_KEY=<your-api-key>\n\n"
        "To explicitly run in offline unit-test mode, pass --provider mock."
    )
