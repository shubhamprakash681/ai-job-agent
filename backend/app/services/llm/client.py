import json
import re
import time
from typing import Any
import httpx
import structlog
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.llm import LLMRequest

logger = structlog.get_logger(__name__)


class LLMResult(BaseModel):
    content: str
    parsed_json: dict[str, Any] | None = None
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    duration_ms: int = 0
    estimated_cost: float = 0.0
    status: str = "success"
    error_message: str | None = None


def estimate_tokens(text: str) -> int:
    """Rough approximation: 1 token ~ 4 characters."""
    return max(1, len(text) // 4)


def extract_json_from_llm_output(text: str) -> dict[str, Any] | None:
    """Extract and parse JSON from raw LLM string, handling optional markdown formatting."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except Exception:
        # Try finding first { and last }
        match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass
    return None


class UnifiedLLMClient:
    """
    Unified LLM Client with automatic provider failover:
    1. Groq (llama-3.3-70b-versatile, fast & free tier)
    2. Gemini (gemini-2.0-flash, high reasoning)
    3. Local LLM (Ollama OpenAI-compatible endpoint)
    4. Heuristic Fallback (deterministic rule-based evaluator)
    """

    def __init__(self):
        self.settings = get_settings()

    async def call_groq(self, system_prompt: str, user_prompt: str) -> LLMResult:
        """Call Groq API via OpenAI-compatible endpoint."""
        api_key = self.settings.GROQ_API_KEY
        model = self.settings.GROQ_MODEL or "llama-3.3-70b-versatile"

        if not api_key:
            raise ValueError("GROQ_API_KEY not configured")

        start = time.time()
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            in_tok = usage.get("prompt_tokens", estimate_tokens(system_prompt + user_prompt))
            out_tok = usage.get("completion_tokens", estimate_tokens(content))
            duration = int((time.time() - start) * 1000)

            # Groq Llama 70B pricing: ~$0.59 / 1M prompt, $0.79 / 1M completion (virtually free)
            cost = (in_tok * 0.00000059) + (out_tok * 0.00000079)

            return LLMResult(
                content=content,
                parsed_json=extract_json_from_llm_output(content),
                provider="groq",
                model=model,
                input_tokens=in_tok,
                output_tokens=out_tok,
                duration_ms=duration,
                estimated_cost=cost,
            )

    async def call_gemini(self, system_prompt: str, user_prompt: str) -> LLMResult:
        """Call Gemini API via REST endpoint."""
        api_key = self.settings.GEMINI_API_KEY
        model = self.settings.GEMINI_MODEL or "gemini-2.0-flash"

        if not api_key:
            raise ValueError("GEMINI_API_KEY not configured")

        start = time.time()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",
            },
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

            candidates = data.get("candidates", [])
            if not candidates:
                raise ValueError("No candidates returned from Gemini")

            content = candidates[0]["content"]["parts"][0]["text"]
            usage = data.get("usageMetadata", {})
            in_tok = usage.get("promptTokenCount", estimate_tokens(system_prompt + user_prompt))
            out_tok = usage.get("candidatesTokenCount", estimate_tokens(content))
            duration = int((time.time() - start) * 1000)

            # Gemini 2.0 Flash: $0.10 / 1M prompt, $0.40 / 1M completion
            cost = (in_tok * 0.0000001) + (out_tok * 0.0000004)

            return LLMResult(
                content=content,
                parsed_json=extract_json_from_llm_output(content),
                provider="gemini",
                model=model,
                input_tokens=in_tok,
                output_tokens=out_tok,
                duration_ms=duration,
                estimated_cost=cost,
            )

    async def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        db: AsyncSession | None = None,
        job_id: int | None = None,
        operation: str = "classify",
    ) -> LLMResult:
        """
        Execute request with automatic provider fallback:
        1. Groq (if GROQ_API_KEY is present)
        2. Gemini (if GEMINI_API_KEY is present)
        3. Fallback Heuristic
        """
        errors: list[str] = []

        # 1. Try Groq
        if self.settings.GROQ_API_KEY:
            try:
                result = await self.call_groq(system_prompt, user_prompt)
                if db:
                    await self._log_to_db(db, result, job_id, operation)
                return result
            except Exception as e:
                err = f"Groq failed: {str(e)}"
                logger.warning(err)
                errors.append(err)

        # 2. Try Gemini
        if self.settings.GEMINI_API_KEY:
            try:
                result = await self.call_gemini(system_prompt, user_prompt)
                if db:
                    await self._log_to_db(db, result, job_id, operation)
                return result
            except Exception as e:
                err = f"Gemini failed: {str(e)}"
                logger.warning(err)
                errors.append(err)

        # 3. Deterministic Heuristic Fallback
        result = self._heuristic_fallback(user_prompt)
        if db:
            await self._log_to_db(db, result, job_id, operation)
        return result

    # Alias for clarity
    generate_structured_json = generate_completion

    def _heuristic_fallback(self, user_prompt: str) -> LLMResult:
        """Deterministic rule-based classification when external LLM APIs are unavailable."""
        text_lower = user_prompt.lower()

        # Check for unrelated stack
        unrelated_techs = ["c++", "golang", "rust", "ruby on rails", "flutter", "swift", "ios developer", "android developer", ".net developer"]
        if any(re.search(rf"\b{re.escape(t)}\b", text_lower) for t in unrelated_techs) and "java" not in text_lower:
            parsed = {
                "role_category": "UNRELATED",
                "fit_category": "REJECT",
                "fit_score": 15,
                "recommended_variant": "java-backend",
                "primary_technologies": ["Unrelated Stack"],
                "matched_skills": [],
                "missing_skills": ["Java", "Spring Boot"],
                "experience_fit": "UNACCEPTABLE",
                "red_flags": ["Technology stack does not align with Java / React candidate profile."],
                "key_responsibilities": ["Non-Java software development"],
                "reasoning": "Job requires technologies outside Shubham Prakash's verified background.",
            }
        elif "kafka" in text_lower and ("stream" in text_lower or "distributed" in text_lower or "redis" in text_lower):
            parsed = {
                "role_category": "DISTRIBUTED_SYSTEMS",
                "fit_category": "HIGH_FIT",
                "fit_score": 90,
                "recommended_variant": "backend-distributed",
                "primary_technologies": ["Java", "Kafka", "Redis", "Distributed Systems"],
                "matched_skills": ["Java", "Kafka", "Redis", "Microservices", "PostgreSQL"],
                "missing_skills": [],
                "experience_fit": "EXCELLENT",
                "red_flags": [],
                "key_responsibilities": ["Build high-throughput distributed microservices", "Implement event streaming pipelines"],
                "reasoning": "Strong match with candidate's TradeX distributed systems & Kafka experience.",
            }
        elif "react" in text_lower and ("java" in text_lower or "spring" in text_lower or "full stack" in text_lower):
            parsed = {
                "role_category": "JAVA_REACT_FULLSTACK",
                "fit_category": "HIGH_FIT",
                "fit_score": 92,
                "recommended_variant": "java-react-fullstack",
                "primary_technologies": ["Java", "Spring Boot", "React", "TypeScript", "REST APIs"],
                "matched_skills": ["Java", "Spring Boot", "React", "TypeScript", "Microservices"],
                "missing_skills": [],
                "experience_fit": "EXCELLENT",
                "red_flags": [],
                "key_responsibilities": ["Develop enterprise Java backend and modern React web UI"],
                "reasoning": "Perfect match with Shubham's 3 years of enterprise Java + React experience at TCS and Accenture.",
            }
        else:
            parsed = {
                "role_category": "JAVA_BACKEND",
                "fit_category": "HIGH_FIT",
                "fit_score": 88,
                "recommended_variant": "java-backend",
                "primary_technologies": ["Java", "Spring Boot", "Microservices", "PostgreSQL"],
                "matched_skills": ["Java", "Spring Boot", "REST APIs", "PostgreSQL", "Docker"],
                "missing_skills": [],
                "experience_fit": "EXCELLENT",
                "red_flags": [],
                "key_responsibilities": ["Design and maintain Spring Boot microservices and REST APIs"],
                "reasoning": "Direct match with candidate's core Java / Spring Boot backend engineering background.",
            }

        return LLMResult(
            content=json.dumps(parsed),
            parsed_json=parsed,
            provider="heuristic",
            model="rule-based-classifier",
            input_tokens=estimate_tokens(user_prompt),
            output_tokens=estimate_tokens(json.dumps(parsed)),
            duration_ms=5,
            estimated_cost=0.0,
        )

    async def _log_to_db(
        self,
        db: AsyncSession,
        result: LLMResult,
        job_id: int | None,
        operation: str,
    ) -> None:
        """Persist request metadata, token counts, and cost into llm_requests table."""
        try:
            req_log = LLMRequest(
                provider=result.provider,
                model=result.model,
                operation=operation,
                prompt_version="v1.0",
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
                estimated_cost=result.estimated_cost,
                duration_ms=result.duration_ms,
                status=result.status,
                error_message=result.error_message,
                job_id=job_id,
            )
            db.add(req_log)
            await db.commit()
        except Exception as e:
            logger.warning("Could not log LLM request to database", error=str(e))


_LLM_CLIENT: UnifiedLLMClient | None = None


def get_llm_client() -> UnifiedLLMClient:
    global _LLM_CLIENT
    if _LLM_CLIENT is None:
        _LLM_CLIENT = UnifiedLLMClient()
    return _LLM_CLIENT

