"""FastAPI interface for running the BrandBrainAI pipeline."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

from BrandBrainAI.main import run_pipeline

app = FastAPI(title="BrandBrainAI API", version="0.1.0")


class AnalyzeRequest(BaseModel):
    url: HttpUrl


@app.post("/analyze")
def analyze(payload: AnalyzeRequest) -> dict:
    """Run the end-to-end pipeline for the provided URL and return JSON results."""
    try:
        result = run_pipeline(str(payload.url))
        return {"status": "ok", "result": result}
    except Exception as exc:  # defensive API boundary
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {exc}") from exc
