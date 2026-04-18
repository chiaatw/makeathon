from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Dict, List, Optional
from uuid import uuid4

from backend.agents.simple_compliance_checker import SimpleComplianceChecker
from devils_advocate_agent import DevilsAdvocateAgentInput, call_devils_advocate_agent

from .models import (
    AnalysisResultDTO,
    AnalysisStatusResponseDTO,
    RecommendationDTO,
    SourcingCaseDTO,
    StreamEventDTO,
    TradeoffItemDTO,
    EvidenceItemDTO,
)


ANALYSIS_STEPS = [
    "Compliance verification",
    "Quality assessment",
    "Price analysis",
    "Lead time evaluation",
    "Risk assessment",
    "Recommendation synthesis",
]


ENUMS = {
    "companies": ["PharmaCorp", "FoodSupplementCo", "Cosmetics Inc"],
    "products": [
        "Immune Support Capsules",
        "Daily Multivitamin Tablets",
        "Liquid Drops",
        "Softgel Complex",
    ],
    "ingredients": ["vitamin-d3", "vitamin-k2", "magnesium-citrate", "zinc-gluconate"],
    "suppliers": ["DSM", "BASF", "Prinova USA", "Ashland", "Taiyo Kagaku"],
    "certifications": ["cGMP", "GMP", "ISO 9001", "ISO 14644", "USP", "FDA-registered"],
    "analysis_steps": ANALYSIS_STEPS,
}


@dataclass
class AnalysisJob:
    analysis_id: str
    request: SourcingCaseDTO
    status: str = "queued"
    current_step: int = 0
    total_steps: int = len(ANALYSIS_STEPS)
    result: Optional[AnalysisResultDTO] = None
    error: Optional[str] = None
    events: List[StreamEventDTO] = field(default_factory=list)
    event_queue: "asyncio.Queue[Optional[StreamEventDTO]]" = field(default_factory=asyncio.Queue)


class AnalysisOrchestrator:
    def __init__(self) -> None:
        self._jobs: Dict[str, AnalysisJob] = {}

    def get_enums(self) -> Dict[str, Any]:
        return ENUMS

    def create_job(self, request: SourcingCaseDTO) -> AnalysisJob:
        analysis_id = str(uuid4())
        job = AnalysisJob(analysis_id=analysis_id, request=request)
        self._jobs[analysis_id] = job
        asyncio.create_task(self._run_job(job))
        return job

    def get_job(self, analysis_id: str) -> Optional[AnalysisJob]:
        return self._jobs.get(analysis_id)

    async def stream_events(self, analysis_id: str) -> AsyncIterator[str]:
        job = self.get_job(analysis_id)
        if not job:
            yield self._format_sse(
                StreamEventDTO(
                    type="error",
                    analysis_id=analysis_id,
                    payload={"message": "Analysis not found"},
                )
            )
            return

        for event in job.events:
            yield self._format_sse(event)

        while True:
            event = await job.event_queue.get()
            if event is None:
                break
            yield self._format_sse(event)

    def to_status_response(self, job: AnalysisJob) -> AnalysisStatusResponseDTO:
        return AnalysisStatusResponseDTO(
            analysis_id=job.analysis_id,
            status=job.status,
            current_step=job.current_step,
            total_steps=job.total_steps,
            result=job.result,
            error=job.error,
        )

    async def _run_job(self, job: AnalysisJob) -> None:
        try:
            job.status = "running"
            for idx, step in enumerate(ANALYSIS_STEPS):
                job.current_step = idx
                await self._emit(
                    job,
                    StreamEventDTO(
                        type="step_started",
                        analysis_id=job.analysis_id,
                        step_index=idx,
                        step_name=step,
                        payload={},
                    ),
                )
                await asyncio.sleep(0.35)
                await self._emit(
                    job,
                    StreamEventDTO(
                        type="step_completed",
                        analysis_id=job.analysis_id,
                        step_index=idx,
                        step_name=step,
                        payload={},
                    ),
                )

            job.result = self._compute_result(job.request)
            job.status = "completed"
            await self._emit(
                job,
                StreamEventDTO(
                    type="final_result",
                    analysis_id=job.analysis_id,
                    payload=job.result.model_dump(),
                ),
            )
        except Exception as exc:
            job.status = "failed"
            job.error = str(exc)
            await self._emit(
                job,
                StreamEventDTO(
                    type="error",
                    analysis_id=job.analysis_id,
                    payload={"message": job.error},
                ),
            )
        finally:
            await job.event_queue.put(None)

    async def _emit(self, job: AnalysisJob, event: StreamEventDTO) -> None:
        job.events.append(event)
        await job.event_queue.put(event)

    @staticmethod
    def _format_sse(event: StreamEventDTO) -> str:
        payload = event.model_dump_json()
        return f"event: {event.type}\ndata: {payload}\n\n"

    def _compute_result(self, request: SourcingCaseDTO) -> AnalysisResultDTO:
        checker = SimpleComplianceChecker()
        compliance = checker.check(request.ingredient, request.supplier, request.company)

        devils = call_devils_advocate_agent(
            DevilsAdvocateAgentInput(
                material=request.ingredient,
                supplier=request.supplier,
                company=request.company,
                material_attributes={"certificates": request.preferences.certifications},
            )
        )

        recommendation_status = self._map_status(compliance.compliance_status, devils.verdict)
        confidence = int(round(((compliance.confidence + devils.confidence) / 2.0) * 100))

        reasons = [x.strip() for x in compliance.reasoning.split("|") if x.strip()]
        reasons.extend([c.claim for c in devils.claims[:3]])

        risks = []
        if compliance.issues:
            if isinstance(compliance.issues, list):
                for issue in compliance.issues:
                    risks.append(str(issue))
        risks.extend([o.issue for o in devils.objections])
        if not risks:
            risks.append("No blocking compliance risks detected in current dataset")

        evidence = [
            EvidenceItemDTO(title="Suppliers CSV", meta="data/suppliers.csv", tag="Internal"),
            EvidenceItemDTO(title="Customer requirements", meta="data/customer_requirements.csv", tag="Internal"),
            EvidenceItemDTO(title="External evidence dataset", meta="data/external_evidence.json", tag="External"),
        ]

        tradeoffs = self._tradeoffs_from_preferences(request)

        recommendation_text = (
            f"{request.supplier} is evaluated for {request.ingredient} at {request.company}. "
            "Recommendation is based on certificate coverage, supplier fit, and available evidence."
        )

        return AnalysisResultDTO(
            recommendation=RecommendationDTO(
                status=recommendation_status,
                confidence=confidence,
                recommendation_text=recommendation_text,
            ),
            reasons=reasons[:6],
            risks=risks[:6],
            evidence=evidence,
            tradeoffs=tradeoffs,
            raw={
                "compliance": {
                    "status": compliance.compliance_status,
                    "confidence": compliance.confidence,
                    "reasoning": compliance.reasoning,
                    "issues": compliance.issues or [],
                    "synergy_potential": compliance.synergy_potential,
                },
                "devils_advocate": devils.dict(),
            },
        )

    @staticmethod
    def _map_status(compliance_status: str, verdict: str) -> str:
        if compliance_status == "COMPLIANT" and verdict in {"RECOMMENDED", "RECOMMENDED_WITH_CAVEAT"}:
            return "Suitable"
        if compliance_status in {"COMPLIANT", "NON_COMPLIANT"}:
            return "Suitable with Risk"
        return "Not Recommended"

    @staticmethod
    def _tradeoffs_from_preferences(request: SourcingCaseDTO) -> List[TradeoffItemDTO]:
        return [
            TradeoffItemDTO(label="Cost", value="Lower" if request.preferences.price == "High" else "Medium", tone="good"),
            TradeoffItemDTO(label="Lead time", value=request.preferences.leadTime, tone="neutral"),
            TradeoffItemDTO(label="Quality", value=request.preferences.quality, tone="good"),
            TradeoffItemDTO(label="Compliance risk", value="Medium" if request.preferences.requireCertifications else "High", tone="warn"),
        ]


orchestrator = AnalysisOrchestrator()
