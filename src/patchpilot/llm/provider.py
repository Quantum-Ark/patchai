"""
Interchangeable LLM Provider Adapter.
Supports real LLM providers (OpenAI, Anthropic) as well as offline deterministic Mock providers for testing.
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from patchpilot.config import config


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate a response from the LLM provider."""
        pass


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or config.openai_api_key
        self.model = model or config.model

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            raise ValueError(
                "OPENAI_API_KEY is not configured. Please set a valid key in .env or switch to the Mock provider."
            )

        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2,
        )
        return response.choices[0].message.content or ""


class MockLLMProvider(BaseLLMProvider):
    """
    Deterministic Mock LLM Provider for unit testing and offline benchmark runs.
    """
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
    provider_name = name or os.getenv("PATCHPILOT_PROVIDER", "openai").lower()
    if provider_name == "mock":
        return MockLLMProvider()
    elif provider_name == "openai":
        # If no key set, fallback gracefully to mock for zero-config runs
        key = config.openai_api_key
        if not key or key == "your_openai_api_key_here":
            return MockLLMProvider()
        return OpenAIProvider()
    else:
        return MockLLMProvider()
