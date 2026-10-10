#!/usr/bin/env python3

"""LLM service names shared by the CLI and the movies command.

Keep ``LLMService`` in sync with ``microeval.llm.LLM_CLIENTS``. This module has
no heavy imports, so the CLI can show the choices without importing microeval
at startup.
"""

from typing import Literal, get_args

LLMService = Literal["openai", "groq", "ollama", "bedrock"]

LLM_SERVICES = get_args(LLMService)
