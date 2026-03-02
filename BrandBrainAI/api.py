"""FastAPI interface for running the BrandBrainAI pipeline."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, HttpUrl

from BrandBrainAI.main import run_pipeline

app = FastAPI(title="BrandBrainAI API", version="0.2.0")


class AnalyzeRequest(BaseModel):
    url: HttpUrl


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    """Serve interactive dashboard UI."""
    ui_file = Path(__file__).resolve().parent / "ui" / "index.html"
    return ui_file.read_text(encoding="utf-8")


@app.post("/analyze")
def analyze(payload: AnalyzeRequest) -> dict:
    """Run the end-to-end pipeline for the provided URL and return JSON results."""
    try:
        result = run_pipeline(str(payload.url))
        return {"status": "ok", "result": result}
    except Exception as exc:  # defensive API boundary
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {exc}") from exc
