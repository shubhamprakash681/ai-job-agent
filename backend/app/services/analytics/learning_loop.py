from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.analytics import LearningInsight, LearningLoopResponse
from app.services.analytics.breakdown_engine import BreakdownEngine
from app.services.analytics.funnel_engine import FunnelEngine


class LearningLoopAdvisor:
    """Implements the Outcome-Driven Strategy Advisor (PROMPT.md Section 75).

    Analyzes conversion metrics across resume variants, sources, and role types
    to recommend ranking adjustments, source prioritization, and search queries.

    SAFETY RULE: Candidate factual information is NEVER automatically modified.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_insights(self) -> LearningLoopResponse:
        breakdown_engine = BreakdownEngine(self.db)
        breakdowns = await breakdown_engine.get_breakdowns()

        funnel_engine = FunnelEngine(self.db)
        funnel = await funnel_engine.get_funnel_metrics()

        insights: List[LearningInsight] = []
        top_variant: Optional[str] = None
        top_source: Optional[str] = None

        # 1. Analyze Resume Variants
        active_variants = [v for v in breakdowns.variants if v.applications_count > 0]
        if active_variants:
            # Sort by conversion rate, then interview count
            best_v = max(active_variants, key=lambda v: (v.conversion_rate, v.interviews_count))
            top_variant = best_v.variant_name

            insights.append(
                LearningInsight(
                    type="variant_preference",
                    title=f"Prioritize {best_v.display_name} Variant",
                    recommendation=(
                        f"Set '{best_v.display_name}' as the preferred variant for upcoming applications. "
                        f"It currently demonstrates a {best_v.conversion_rate}% interview conversion rate."
                    ),
                    rationale=(
                        f"Variant '{best_v.display_name}' has produced {best_v.interviews_count} interview(s) "
                        f"across {best_v.applications_count} submitted application(s)."
                    ),
                    impact="High — Increases recruiter response probability based on verified historical conversion.",
                )
            )
        else:
            insights.append(
                LearningInsight(
                    type="variant_preference",
                    title="Baseline Variant Strategy: Java + React Full Stack",
                    recommendation="Continue utilizing 'Java + React Full Stack' as the primary master resume variant.",
                    rationale="Aligned with core background (~3.2 years software development across TCS Digital and Accenture).",
                    impact="Medium — Established high relevance across Indian tech hubs (Mumbai, Bengaluru, Pune).",
                )
            )

        # 2. Analyze Job Sources
        active_sources = [s for s in breakdowns.sources if s.applied_count > 0]
        if active_sources:
            best_s = max(active_sources, key=lambda s: (s.interview_rate, s.response_rate))
            top_source = best_s.source

            insights.append(
                LearningInsight(
                    type="source_priority",
                    title=f"Scale Discovery on '{best_s.source.capitalize()}'",
                    recommendation=(
                        f"Increase crawler frequency and scoring weight for jobs sourced from '{best_s.source.capitalize()}'. "
                        f"Recorded interview conversion rate: {best_s.interview_rate}%."
                    ),
                    rationale=(
                        f"Applications via {best_s.source.capitalize()} generated {best_s.interviews_count} interview(s) "
                        f"with a {best_s.response_rate}% overall recruiter response rate."
                    ),
                    impact="High — Concentrates effort on high-responsiveness channels.",
                )
            )

            # Check for low-performing sources
            underperforming = [s for s in active_sources if s.applied_count >= 5 and s.interviews_count == 0]
            for low_s in underperforming:
                insights.append(
                    LearningInsight(
                        type="source_priority",
                        title=f"Deprioritize High-Friction Channel: {low_s.source.capitalize()}",
                        recommendation=f"Lower scoring threshold priority for '{low_s.source.capitalize()}' in favor of direct company ATS listings.",
                        rationale=f"0 interviews yielded across {low_s.applied_count} applications.",
                        impact="Medium — Reduces application fatigue on stale job postings.",
                    )
                )
        else:
            insights.append(
                LearningInsight(
                    type="source_priority",
                    title="Direct ATS Prioritization (Greenhouse / Lever)",
                    recommendation="Prioritize direct career page postings (Lever, Greenhouse) over third-party aggregators.",
                    rationale="Direct ATS postings avoid intermediary screening filters and provide higher initial response rates.",
                    impact="High — Direct submissions convert ~2.5x faster to recruiter screenings.",
                )
            )

        # 3. Role & Skill Alignment Strategy
        insights.append(
            LearningInsight(
                type="role_focus",
                title="Optimize for Concurrency & Microservices Titles",
                recommendation="Target Senior Software Engineer / SDE-2 roles emphasizing Java 17+, Spring Boot, Kafka, and React.",
                rationale="Candidate experience sweet spot is ~3.2 years (TCS Digital, Accenture), meeting mid-to-senior backend/fullstack benchmarks.",
                impact="High — Maximizes match score above the 70+ threshold.",
            )
        )

        return LearningLoopResponse(
            insights=insights,
            top_variant=top_variant,
            top_source=top_source,
            candidate_facts_preserved=True,
        )

