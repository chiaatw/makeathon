from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .models import AnalysisStatusResponseDTO, EnumsResponseDTO, EvaluateResponseDTO, SourcingCaseDTO
from .services import orchestrator


app = FastAPI(title="Makeathon API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/enums", response_model=EnumsResponseDTO)
def get_enums() -> EnumsResponseDTO:
    return EnumsResponseDTO(**orchestrator.get_enums())


@app.post("/api/v1/analysis/evaluate", response_model=EvaluateResponseDTO)
def evaluate_case(payload: SourcingCaseDTO) -> EvaluateResponseDTO:
    job = orchestrator.create_job(payload)
    return EvaluateResponseDTO(analysis_id=job.analysis_id, status=job.status)


@app.get("/api/v1/analysis/{analysis_id}", response_model=AnalysisStatusResponseDTO)
def get_analysis_status(analysis_id: str) -> AnalysisStatusResponseDTO:
    job = orchestrator.get_job(analysis_id)
    if not job:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return orchestrator.to_status_response(job)


@app.get("/api/v1/analysis/{analysis_id}/events")
async def stream_analysis_events(analysis_id: str) -> StreamingResponse:
    job = orchestrator.get_job(analysis_id)
    if not job:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return StreamingResponse(
        orchestrator.stream_events(analysis_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
