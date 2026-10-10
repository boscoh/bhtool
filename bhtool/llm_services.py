#!/usr/bin/env python3

"""Provider defaults for the movies LLM command.

One cheap model per provider, picked for the short name-normalization prompt.
Prices change, so check them before you add a provider. This module has no
heavy imports, so the CLI can show the list without loading pydantic-ai.
"""

import os
from typing import Literal, get_args

LLMService = Literal[
    "groq",
    "google",
    "openai",
    "anthropic",
    "mistral",
    "deepseek",
    "xai",
    "bedrock",
    "ollama",
]

PROVIDERS = get_args(LLMService)

# pydantic-ai model id is "<provider>:<model>".
# The value is the cheapest model that can follow the normalize instructions.
PROVIDER_MODELS = {
    "groq": "openai/gpt-oss-20b",         # $0.075 / $0.30 per 1M
    "google": "gemini-2.5-flash-lite",    # $0.10 / $0.40
    "openai": "gpt-6-luna",               # $0.10 / $0.50
    "anthropic": "claude-haiku-5-5",      # $0.10 / $0.50
    "mistral": "ministral-3-8b-25-12",    # $0.15 / $0.15
    "deepseek": "deepseek-flash",         # $0.15 / $0.60 off-peak
    "xai": "grok-4.3",                    # $1.25 / $2.50
    "bedrock": "amazon.nova-lite-v1:0",   # region-dependent
    "ollama": "llama3.2",                 # free, local
}

# Environment variable that enables a provider. Auto-detect reads these in order.
PROVIDER_ENV_VARS = {
    "groq": ("GROQ_API_KEY",),
    "google": ("GOOGLE_API_KEY", "GEMINI_API_KEY"),
    "openai": ("OPENAI_API_KEY",),
    "anthropic": ("ANTHROPIC_API_KEY",),
    "mistral": ("MISTRAL_API_KEY",),
    "deepseek": ("DEEPSEEK_API_KEY",),
    "xai": ("XAI_API_KEY",),
    "bedrock": ("AWS_ACCESS_KEY_ID", "AWS_PROFILE", "AWS_BEARER_TOKEN_BEDROCK"),
    "ollama": ("OLLAMA_BASE_URL",),
}

# pydantic-ai needs this value for the Ollama provider.
OLLAMA_BASE_URL = "http://localhost:11434"


def model_for(service: str) -> str:
    """Return the pydantic-ai model id for a provider, for example 'openai:gpt-6-luna'."""
    try:
        model = PROVIDER_MODELS[service]
    except KeyError:
        raise ValueError(
            f"Unknown service {service!r}; choose one of {', '.join(PROVIDERS)}"
        ) from None
    return f"{service}:{model}"


def detect_service() -> str:
    """Pick a provider from LLM_SERVICE, else from the environment, else ollama."""
    env_service = os.environ.get("LLM_SERVICE")
    if env_service:
        return env_service.lower()
    for provider in PROVIDERS:
        if any(os.environ.get(var) for var in PROVIDER_ENV_VARS[provider]):
            return provider
    return "ollama"
