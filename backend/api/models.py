from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


PriorityLevel = Literal["Low", "Medium", "High"]
AnalysisStatus = Literal["queued", "running", "completed", "failed"]
RecommendationStatus = Literal["Suitable", "Suitable with Risk", "Not Recommended"]
TradeoffLevel = Literal["Low", "Lower", "Medium", "High"]


class PreferencesDTO(BaseModel):
    price: PriorityLevel
    leadTime: PriorityLevel
    quality: PriorityLevel
    requireCertifications: bool
    maxLeadTimeDays: int = Field(ge=1, le=365)
    certifications: List[str] = Field(default_factory=list)


class SourcingCaseDTO(BaseModel):
    id: Optional[str] = None
    company: str
    product: str
    ingredient: str
    supplier: str
    preferences: PreferencesDTO


class EnumsResponseDTO(BaseModel):
    companies: List[str]
    products: List[str]
    ingredients: List[str]
    suppliers: List[str]
    certifications: List[str]
    analysis_steps: List[str]


class EvaluateResponseDTO(BaseModel):
    analysis_id: str
    status: AnalysisStatus


class RecommendationDTO(BaseModel):
    status: RecommendationStatus
    confidence: int = Field(ge=0, le=100)
    recommendation_text: str


class TradeoffItemDTO(BaseModel):
    label: str
    value: TradeoffLevel
    tone: Literal["good", "neutral", "warn"]


class EvidenceItemDTO(BaseModel):
    title: str
    meta: str
    tag: Literal["External", "Internal", "Regulatory", "Document"]


class AnalysisResultDTO(BaseModel):
    recommendation: RecommendationDTO
    reasons: List[str]
    risks: List[str]
    evidence: List[EvidenceItemDTO]
    tradeoffs: List[TradeoffItemDTO]
    raw: Dict[str, Any] = Field(default_factory=dict)


class AnalysisStatusResponseDTO(BaseModel):
    analysis_id: str
    status: AnalysisStatus
    current_step: int
    total_steps: int
    result: Optional[AnalysisResultDTO] = None
    error: Optional[str] = None


class StreamEventDTO(BaseModel):
    type: Literal["step_started", "step_completed", "final_result", "error"]
    analysis_id: str
    step_index: Optional[int] = None
    step_name: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
