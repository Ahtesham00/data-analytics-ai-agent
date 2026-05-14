from app.llm.base import LLMClient


def get_llm_client(provider: str) -> LLMClient:
    if provider == "anthropic":
        from app.llm.anthropic_client import AnthropicClient
        return AnthropicClient()
    elif provider == "openai":
        from app.llm.openai_client import OpenAIClient
        return OpenAIClient()
    else:
        raise ValueError(f"Unsupported provider: {provider}")
