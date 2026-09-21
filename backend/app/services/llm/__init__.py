from app.services.llm.client import UnifiedLLMClient, get_llm_client, LLMResult
from app.services.llm.prompts import (
    JOB_CLASSIFICATION_SYSTEM_PROMPT,
    JOB_CLASSIFICATION_USER_TEMPLATE,
)

__all__ = [
    "UnifiedLLMClient",
    "get_llm_client",
    "LLMResult",
    "JOB_CLASSIFICATION_SYSTEM_PROMPT",
    "JOB_CLASSIFICATION_USER_TEMPLATE",
]

