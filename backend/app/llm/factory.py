import os
from app.llm.base import LLMProvider
from app.llm.providers.local import LocalProvider


def get_llm_provider() -> LLMProvider:
    provider_name = os.getenv("LLM_PROVIDER", "local").lower()

    if provider_name == "local":
        return LocalProvider()

    if provider_name == "groq":
        from app.llm.providers.groq import GroqProvider
        return GroqProvider()

    if provider_name == "huggingface":
        from app.llm.providers.huggingface import HuggingFaceProvider
        return HuggingFaceProvider()

    if provider_name == "openrouter":
        from app.llm.providers.openrouter import OpenRouterProvider
        return OpenRouterProvider()

    raise ValueError(
        f"Unknown LLM_PROVIDER '{provider_name}'. "
        "Valid values: local, groq, huggingface, openrouter"
    )