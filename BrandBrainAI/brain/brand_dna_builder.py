"""Build a structured Brand DNA profile from extracted and analyzed artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from BrandBrainAI.brain.model_interface import generate_response


def _resolve_path(path: str | Path) -> Path:
    """Resolve relative paths from the BrandBrainAI project root."""
    p = Path(path)
    if p.is_absolute():
        return p
    return Path(__file__).resolve().parents[1] / p


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _default_brand_dna(raw_text: str, pricing: dict[str, Any], text_metrics: dict[str, Any]) -> dict[str, Any]:
    """Fallback structure if model output is unavailable or unparsable."""
    preview = " ".join(raw_text.split())[:400]
    return {
        "brand_summary": preview or "No source text available.",
        "voice_tone": {
            "emotional_ratio": text_metrics.get("emotional_word_ratio", 0.0),
            "cta_ratio": text_metrics.get("cta_frequency", {}).get("ratio", 0.0),
        },
        "pricing_positioning": {
            "average_price": pricing.get("average_price"),
            "price_range": pricing.get("price_range", {}),
            "average_discount_percent": pricing.get("average_discount_percent", 0.0),
        },
        "recommended_audience": [],
        "value_propositions": [],
        "evidence": {
            "word_counts": text_metrics.get("word_counts", {}),
        },
    }


def _build_prompt(raw_text: str, pricing: dict[str, Any], text_metrics: dict[str, Any]) -> str:
    """Create prompt asking the model for strict JSON Brand DNA output."""
    return (
        "You are a brand strategist. Build a concise, structured Brand DNA JSON object.\n"
        "Return ONLY valid JSON (no markdown).\n"
        "Use this schema exactly:\n"
        "{\n"
        '  "brand_summary": "string",\n'
        '  "voice_tone": {"style": ["string"], "emotional_ratio": number, "cta_ratio": number},\n'
        '  "pricing_positioning": {"average_price": number|null, "price_range": {"min": number|null, "max": number|null}, "average_discount_percent": number},\n'
        '  "recommended_audience": ["string"],\n'
        '  "value_propositions": ["string"],\n'
        '  "evidence": {"word_counts": {"homepage": number, "product_descriptions": number, "total": number}}\n'
        "}\n\n"
        f"RAW_TEXT:\n{raw_text[:6000]}\n\n"
        f"PRICING_ANALYSIS:\n{json.dumps(pricing, ensure_ascii=False)}\n\n"
        f"TEXT_METRICS:\n{json.dumps(text_metrics, ensure_ascii=False)}"
    )


def build_brand_dna(
    raw_text_path: str | Path = "memory/raw_text.txt",
    pricing_analysis_path: str | Path = "memory/pricing_analysis.json",
    text_metrics_path: str | Path = "memory/text_metrics.json",
    output_path: str | Path = "memory/brand_dna.json",
    temperature: float = 0.3,
    max_tokens: int = 700,
) -> bool:
    """Build a Brand DNA dict from text + analytics and save to JSON."""
    raw_text_file = _resolve_path(raw_text_path)
    pricing_file = _resolve_path(pricing_analysis_path)
    text_metrics_file = _resolve_path(text_metrics_path)
    out_file = _resolve_path(output_path)

    raw_text = _read_text(raw_text_file)
    pricing = _read_json(pricing_file)
    text_metrics = _read_json(text_metrics_file)

    prompt = _build_prompt(raw_text=raw_text, pricing=pricing, text_metrics=text_metrics)
    llm_output = generate_response(prompt=prompt, temperature=temperature, max_tokens=max_tokens)

    default_dna = _default_brand_dna(raw_text=raw_text, pricing=pricing, text_metrics=text_metrics)
    brand_dna: dict[str, Any] = default_dna

    if isinstance(llm_output, str) and llm_output.strip():
        try:
            parsed = json.loads(llm_output)
            if isinstance(parsed, dict):
                # Merge minimally to guarantee required keys exist.
                brand_dna = {**default_dna, **parsed}
        except json.JSONDecodeError:
            brand_dna = default_dna

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(brand_dna, indent=2, ensure_ascii=False), encoding="utf-8")
    return True
