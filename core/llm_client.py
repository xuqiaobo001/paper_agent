"""
LLM Client Module
Responsible for interacting with various LLM APIs
"""
import os
import json
import time
from typing import Optional, List, Dict, Any, Generator
from abc import ABC, abstractmethod

from .config import Config, get_config, LLMConfig


class LLMClient(ABC):
    """LLM Client Base Class"""

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat request"""
        pass

    @abstractmethod
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        """Streaming chat request"""
        pass


class OpenAICompatibleClient(LLMClient):
    """OpenAI-compatible client (supports OpenAI, DeepSeek, Zhipu, etc.)"""

    def __init__(self, config: LLMConfig, api_base: str = ""):
        self.config = config
        self.api_base = api_base or config.api_base or "https://api.openai.com/v1"
        self.api_key = config.api_key

        # Lazy load openai library
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError:
                raise ImportError("Please install openai: pip install openai")

            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_base,
                timeout=self.config.timeout,
            )
        return self._client

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat request"""
        retries = 0
        last_error = None

        while retries < self.config.max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=kwargs.get("model", self.config.model),
                    messages=messages,
                    temperature=kwargs.get("temperature", self.config.temperature),
                    max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                )
                return response.choices[0].message.content or ""

            except Exception as e:
                last_error = e
                retries += 1
                if retries < self.config.max_retries:
                    time.sleep(self.config.retry_delay)

        raise RuntimeError(f"LLM request failed after {self.config.max_retries} retries: {last_error}")

    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        """Streaming chat request"""
        try:
            response = self.client.chat.completions.create(
                model=kwargs.get("model", self.config.model),
                messages=messages,
                temperature=kwargs.get("temperature", self.config.temperature),
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                stream=True,
            )

            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise RuntimeError(f"LLM streaming request failed: {e}")


class AnthropicClient(LLMClient):
    """Anthropic Claude Client"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.api_key = config.api_key
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                from anthropic import Anthropic
            except ImportError:
                raise ImportError("Please install anthropic: pip install anthropic")

            self._client = Anthropic(
                api_key=self.api_key,
            )
        return self._client

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat request"""
        retries = 0
        last_error = None

        # Convert message format (Anthropic uses different format)
        system_message = ""
        chat_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                chat_messages.append(msg)

        while retries < self.config.max_retries:
            try:
                response = self.client.messages.create(
                    model=kwargs.get("model", self.config.model),
                    max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                    system=system_message if system_message else None,
                    messages=chat_messages,
                )
                return response.content[0].text

            except Exception as e:
                last_error = e
                retries += 1
                if retries < self.config.max_retries:
                    time.sleep(self.config.retry_delay)

        raise RuntimeError(f"Anthropic request failed after {self.config.max_retries} retries: {last_error}")

    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        """Streaming chat request"""
        system_message = ""
        chat_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                chat_messages.append(msg)

        try:
            with self.client.messages.stream(
                model=kwargs.get("model", self.config.model),
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                system=system_message if system_message else None,
                messages=chat_messages,
            ) as stream:
                for text in stream.text_stream:
                    yield text

        except Exception as e:
            raise RuntimeError(f"Anthropic streaming request failed: {e}")


class OllamaClient(LLMClient):
    """Ollama Local Model Client"""

    def __init__(self, config: LLMConfig, api_base: str = ""):
        self.config = config
        self.api_base = api_base or config.api_base or "http://localhost:11434/v1"
        # Ollama is compatible with OpenAI API, use OpenAI client
        self._openai_client = OpenAICompatibleClient(config, self.api_base)
        # Ollama doesn't need API key, set placeholder
        self._openai_client.api_key = "ollama"

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        return self._openai_client.chat(messages, **kwargs)

    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        return self._openai_client.chat_stream(messages, **kwargs)


class LLMClientFactory:
    """LLM Client Factory"""

    @staticmethod
    def create(config: Optional[Config] = None) -> LLMClient:
        """Create LLM client based on configuration"""
        config = config or get_config()
        llm_config = config.llm
        provider = llm_config.provider.lower()

        # Get provider-specific api_base
        api_base = config.get_llm_api_base()

        if provider == "openai":
            return OpenAICompatibleClient(llm_config, api_base)

        elif provider == "anthropic":
            return AnthropicClient(llm_config)

        elif provider == "deepseek":
            return OpenAICompatibleClient(llm_config, api_base or "https://api.deepseek.com")

        elif provider == "zhipu":
            return OpenAICompatibleClient(llm_config, api_base or "https://open.bigmodel.cn/api/paas/v4")

        elif provider == "ollama":
            return OllamaClient(llm_config, api_base)

        else:
            # Default to OpenAI-compatible client
            return OpenAICompatibleClient(llm_config, api_base)


class LLMHelper:
    """LLM Helper Utility Class"""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or get_config()
        self.client = LLMClientFactory.create(self.config)

    def ask(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Simple Q&A"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        return self.client.chat(messages, **kwargs)

    def analyze(self, content: str, instruction: str, **kwargs) -> str:
        """Analyze content"""
        prompt = f"{instruction}\n\nContent to analyze:\n\n{content}"
        return self.ask(prompt, **kwargs)

    def extract_json(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Extract JSON format response"""
        system_prompt = "You are a professional information extraction assistant. Please return results in JSON format only, without any other content."

        response = self.ask(prompt, system_prompt=system_prompt, **kwargs)

        # Try to extract JSON
        try:
            # Try direct parsing
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
            if json_match:
                return json.loads(json_match.group(1))

            # Try to extract content within braces
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group(0))

            raise ValueError(f"Cannot extract JSON from response: {response[:200]}")

    def summarize(self, content: str, max_length: int = 500, **kwargs) -> str:
        """Summarize content"""
        prompt = f"Please summarize the key points of the following content in no more than {max_length} characters:\n\n{content}"
        return self.ask(prompt, **kwargs)


# Convenience functions
def create_llm_client(config: Optional[Config] = None) -> LLMClient:
    """Create LLM client"""
    return LLMClientFactory.create(config)


def get_llm_helper(config: Optional[Config] = None) -> LLMHelper:
    """Get LLM helper utility"""
    return LLMHelper(config)
