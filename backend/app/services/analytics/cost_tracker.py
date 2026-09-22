from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.llm import LLMRequest
from app.schemas.analytics import LLMUsageResponse


class LLMCostTracker:
    """Audits LLM usage, token consumption, provider distribution, and cost (PROMPT.md Section 78)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_usage_metrics(self) -> LLMUsageResponse:
        # Total requests, tokens, cost, duration
        totals_stmt = select(
            func.count(LLMRequest.id),
            func.coalesce(func.sum(LLMRequest.input_tokens), 0),
            func.coalesce(func.sum(LLMRequest.output_tokens), 0),
            func.coalesce(func.sum(LLMRequest.estimated_cost), 0.0),
            func.coalesce(func.avg(LLMRequest.duration_ms), 0.0),
        )
        totals_res = await self.db.execute(totals_stmt)
        req_count, in_tok, out_tok, total_cost, avg_dur = totals_res.one()

        # Breakdown by Provider
        provider_stmt = select(
            LLMRequest.provider,
            func.count(LLMRequest.id),
            func.coalesce(func.sum(LLMRequest.input_tokens), 0),
            func.coalesce(func.sum(LLMRequest.output_tokens), 0),
            func.coalesce(func.sum(LLMRequest.estimated_cost), 0.0),
            func.coalesce(func.avg(LLMRequest.duration_ms), 0.0),
        ).group_by(LLMRequest.provider)
        provider_res = await self.db.execute(provider_stmt)

        by_provider: Dict[str, Any] = {}
        for prov, p_cnt, p_in, p_out, p_cost, p_dur in provider_res.all():
            by_provider[prov] = {
                "requests": p_cnt,
                "input_tokens": p_in,
                "output_tokens": p_out,
                "estimated_cost_usd": round(float(p_cost), 4),
                "avg_duration_ms": round(float(p_dur), 1),
            }

        # Breakdown by Operation
        op_stmt = select(
            LLMRequest.operation,
            func.count(LLMRequest.id),
            func.coalesce(func.sum(LLMRequest.input_tokens + func.coalesce(LLMRequest.output_tokens, 0)), 0),
        ).group_by(LLMRequest.operation)
        op_res = await self.db.execute(op_stmt)

        by_operation: Dict[str, Any] = {}
        for op, o_cnt, o_tok in op_res.all():
            by_operation[op] = {
                "requests": o_cnt,
                "total_tokens": o_tok,
            }

        return LLMUsageResponse(
            total_requests=req_count or 0,
            total_input_tokens=in_tok or 0,
            total_output_tokens=out_tok or 0,
            estimated_total_cost_usd=round(float(total_cost or 0.0), 4),
            by_provider=by_provider,
            by_operation=by_operation,
            avg_duration_ms=round(float(avg_dur or 0.0), 1),
        )

