import json
from typing import List, Dict, Any
from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.models.job import Job
from app.models.application import Application
from app.models.resume import ResumeVariant, ResumeVersion
from app.schemas.analytics import (
    SourceBreakdown,
    VariantBreakdown,
    LocationBreakdown,
    CompanyBreakdown,
    BreakdownsResponse,
)


class BreakdownEngine:
    """Computes multi-dimensional breakdowns by source, resume variant, location, and company."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_breakdowns(self) -> BreakdownsResponse:
        sources = await self._get_source_breakdown()
        variants = await self._get_variant_breakdown()
        locations = await self._get_location_breakdown()
        companies = await self._get_company_breakdown()

        return BreakdownsResponse(
            sources=sources,
            variants=variants,
            locations=locations,
            companies=companies,
        )

    async def _get_source_breakdown(self) -> List[SourceBreakdown]:
        # Aggregate jobs and applications per source
        jobs_stmt = select(Job.source, func.count(Job.id)).group_by(Job.source)
        jobs_res = await self.db.execute(jobs_stmt)
        job_counts = {row[0]: row[1] for row in jobs_res.all()}

        # Fetch applications joined with jobs
        apps_stmt = (
            select(Job.source, Application.status)
            .join(Job, Application.job_id == Job.id)
        )
        apps_res = await self.db.execute(apps_stmt)
        
        apps_by_source: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for source, status in apps_res.all():
            apps_by_source[source][status] += 1

        all_sources = set(job_counts.keys()).union(set(apps_by_source.keys()))
        if not all_sources:
            # Default sources baseline
            all_sources = {"naukri", "indeed", "greenhouse", "lever", "manual"}

        results: List[SourceBreakdown] = []
        for src in sorted(all_sources):
            j_cnt = job_counts.get(src, 0)
            status_map = apps_by_source.get(src, {})
            
            applied = (
                status_map.get("APPLIED", 0) +
                status_map.get("INTERVIEW", 0) +
                status_map.get("OFFER", 0) +
                status_map.get("REJECTED", 0)
            )
            interviews = status_map.get("INTERVIEW", 0) + status_map.get("OFFER", 0)
            offers = status_map.get("OFFER", 0)
            rejections = status_map.get("REJECTED", 0)

            resp_rate = round(((interviews + rejections) / applied) * 100.0, 1) if applied > 0 else 0.0
            interview_rate = round((interviews / applied) * 100.0, 1) if applied > 0 else 0.0

            results.append(
                SourceBreakdown(
                    source=src,
                    jobs_count=j_cnt,
                    applied_count=applied,
                    interviews_count=interviews,
                    offers_count=offers,
                    response_rate=resp_rate,
                    interview_rate=interview_rate,
                )
            )

        return results

    async def _get_variant_breakdown(self) -> List[VariantBreakdown]:
        # Fetch all resume variants
        var_stmt = select(ResumeVariant)
        var_res = await self.db.execute(var_stmt)
        all_variants = var_res.scalars().all()

        # Fetch applications with their resume version and variant
        app_stmt = (
            select(ResumeVersion.variant_id, Application.status)
            .join(ResumeVersion, Application.resume_version_id == ResumeVersion.id)
        )
        app_res = await self.db.execute(app_stmt)

        stats_by_variant: Dict[int, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for variant_id, status in app_res.all():
            if variant_id is not None:
                stats_by_variant[variant_id][status] += 1

        results: List[VariantBreakdown] = []
        for v in all_variants:
            v_stats = stats_by_variant.get(v.id, {})
            applied = (
                v_stats.get("APPLIED", 0) +
                v_stats.get("INTERVIEW", 0) +
                v_stats.get("OFFER", 0) +
                v_stats.get("REJECTED", 0)
            )
            interviews = v_stats.get("INTERVIEW", 0) + v_stats.get("OFFER", 0)
            offers = v_stats.get("OFFER", 0)
            conv_rate = round((interviews / applied) * 100.0, 1) if applied > 0 else 0.0

            results.append(
                VariantBreakdown(
                    variant_id=v.id,
                    variant_name=v.name,
                    display_name=v.display_name,
                    applications_count=applied,
                    interviews_count=interviews,
                    offers_count=offers,
                    conversion_rate=conv_rate,
                )
            )

        return results

    async def _get_location_breakdown(self) -> List[LocationBreakdown]:
        # Aggregate job counts by canonical location
        jobs_stmt = select(Job.locations, Job.remote)
        jobs_res = await self.db.execute(jobs_stmt)

        counts: Dict[str, int] = defaultdict(int)
        for loc_json, remote in jobs_res.all():
            if remote:
                counts["Remote"] += 1

            if loc_json:
                try:
                    loc_list = json.loads(loc_json) if loc_json.startswith("[") else [loc_json]
                    for loc in loc_list:
                        loc_clean = loc.strip().title()
                        if "Mumbai" in loc_clean:
                            counts["Mumbai"] += 1
                        elif "Bengaluru" in loc_clean or "Bangalore" in loc_clean:
                            counts["Bengaluru"] += 1
                        elif "Pune" in loc_clean:
                            counts["Pune"] += 1
                        elif "Hyderabad" in loc_clean:
                            counts["Hyderabad"] += 1
                        elif not remote:
                            counts[loc_clean] += 1
                except Exception:
                    if "mumbai" in str(loc_json).lower():
                        counts["Mumbai"] += 1
                    elif "bengaluru" in str(loc_json).lower() or "bangalore" in str(loc_json).lower():
                        counts["Bengaluru"] += 1
                    elif "pune" in str(loc_json).lower():
                        counts["Pune"] += 1
                    elif not remote:
                        counts["Other"] += 1
            elif not remote:
                counts["Unspecified"] += 1

        # Applications by location
        app_loc_stmt = (
            select(Job.locations, Job.remote)
            .join(Application, Application.job_id == Job.id)
            .where(Application.status.in_(["APPLIED", "INTERVIEW", "OFFER"]))
        )
        app_loc_res = await self.db.execute(app_loc_stmt)
        app_counts: Dict[str, int] = defaultdict(int)
        for loc_json, remote in app_loc_res.all():
            if remote:
                app_counts["Remote"] += 1
            if loc_json and "mumbai" in str(loc_json).lower():
                app_counts["Mumbai"] += 1
            elif loc_json and ("bengaluru" in str(loc_json).lower() or "bangalore" in str(loc_json).lower()):
                app_counts["Bengaluru"] += 1
            elif loc_json and "pune" in str(loc_json).lower():
                app_counts["Pune"] += 1
            elif not remote:
                app_counts["Other"] += 1

        results: List[LocationBreakdown] = []
        for loc, j_cnt in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            results.append(
                LocationBreakdown(
                    location=loc,
                    jobs_count=j_cnt,
                    applications_count=app_counts.get(loc, 0)
                )
            )

        if not results:
            results = [
                LocationBreakdown(location="Mumbai", jobs_count=0, applications_count=0),
                LocationBreakdown(location="Remote", jobs_count=0, applications_count=0),
                LocationBreakdown(location="Bengaluru", jobs_count=0, applications_count=0),
            ]

        return results

    async def _get_company_breakdown(self) -> List[CompanyBreakdown]:
        # Top companies by job count and application stage
        comp_stmt = (
            select(Job.company, func.count(Job.id))
            .where(Job.company.isnot(None))
            .group_by(Job.company)
            .order_by(desc(func.count(Job.id)))
            .limit(10)
        )
        comp_res = await self.db.execute(comp_stmt)

        results: List[CompanyBreakdown] = []
        stage_rank = {
            "DISCOVERED": 0, "SHORTLISTED": 1, "RESUME_READY": 2,
            "AWAITING_APPROVAL": 3, "APPLIED": 4, "INTERVIEW": 5, "OFFER": 6
        }

        for comp_name, total_j in comp_res.all():
            if not comp_name:
                continue

            app_stmt = (
                select(Application.status)
                .join(Job, Application.job_id == Job.id)
                .where(Job.company == comp_name)
            )
            app_res = await self.db.execute(app_stmt)
            statuses = app_res.scalars().all()

            applied_count = sum(1 for s in statuses if s in ["APPLIED", "INTERVIEW", "OFFER"])
            
            # Find highest stage
            highest = "DISCOVERED"
            highest_score = -1
            for s in statuses:
                score = stage_rank.get(s, 0)
                if score > highest_score:
                    highest_score = score
                    highest = s

            results.append(
                CompanyBreakdown(
                    company=comp_name,
                    total_jobs=total_j,
                    applied_count=applied_count,
                    highest_stage=highest
                )
            )

        return results

