"""
Interchangeable LLM Provider Adapter.
Supports real LLM providers (OpenAI, Anthropic, Gemini) with strict authentication verification.
Deterministic Mock provider is restricted to isolated unit tests and explicit offline flags.
"""

import os
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


class OpenAIProvider(BaseLLMProvider):
    provider_name: str = "OpenAI"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or config.openai_api_key
        self.model_name = model or config.model or "gpt-4o"

        if not self.api_key or self.api_key == "your_openai_api_key_here":
            raise ValueError(
                "OPENAI_API_KEY is not configured. Please set OPENAI_API_KEY in your .env file."
            )

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
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


class AnthropicProvider(BaseLLMProvider):
    provider_name: str = "Anthropic"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or config.anthropic_api_key
        self.model_name = model or config.model or "claude-3-5-sonnet-20241022"

        if not self.api_key or self.api_key == "your_anthropic_api_key_here":
            raise ValueError(
                "ANTHROPIC_API_KEY is not configured. Please set ANTHROPIC_API_KEY in your .env file."
            )

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        import anthropic

        client = anthropic.Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model=self.model_name,
            max_tokens=4096,
            system=system_prompt or "You are PatchPilot AI, an autonomous software repair engineer.",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        # Concatenate text blocks
        return "".join(b.text for b in response.content if hasattr(b, "text"))


class GeminiProvider(BaseLLMProvider):
    provider_name: str = "Gemini"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or config.gemini_api_key
        self.model_name = model or config.model or "gemini-2.0-flash"

        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            raise ValueError(
                "GEMINI_API_KEY is not configured. Please set GEMINI_API_KEY in your .env file."
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

    if target == "anthropic":
        return AnthropicProvider()

    if target == "gemini":
        return GeminiProvider()

    # If no provider explicitly specified, auto-detect configured live credentials
    if config.openai_api_key and config.openai_api_key != "your_openai_api_key_here":
        return OpenAIProvider()

    if config.anthropic_api_key and config.anthropic_api_key != "your_anthropic_api_key_here":
        return AnthropicProvider()

    if config.gemini_api_key and config.gemini_api_key != "your_gemini_api_key_here":
        return GeminiProvider()

    # Fail explicitly with actionable instructions
    raise RuntimeError(
        "No live LLM provider credentials configured.\n"
        "Please set one of the following in your local .env file:\n"
        "  - OPENAI_API_KEY=<your-key>\n"
        "  - ANTHROPIC_API_KEY=<your-key>\n"
        "  - GEMINI_API_KEY=<your-key>\n"
        "To explicitly run in offline unit-test mode, pass --provider mock."
    )
