"""Text analysis utilities for homepage and product description content."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_WORD_RE = re.compile(r"[A-Za-z']+")

_CTA_TERMS = {
    "buy",
    "shop",
    "order",
    "subscribe",
    "sign",
    "join",
    "start",
    "try",
    "learn",
    "discover",
    "book",
    "download",
    "contact",
    "get",
}

_EMOTIONAL_TERMS = {
    "amazing",
    "awesome",
    "beautiful",
    "best",
    "bold",
    "calm",
    "confident",
    "delight",
    "easy",
    "elegant",
    "empower",
    "excited",
    "exclusive",
    "fantastic",
    "feel",
    "fresh",
    "happy",
    "incredible",
    "inspired",
    "joy",
    "love",
    "luxury",
    "perfect",
    "powerful",
    "premium",
    "relax",
    "safe",
    "simple",
    "special",
    "strong",
    "trusted",
    "unique",
}


def _tokenize(text: str) -> list[str]:
    return [w.lower() for w in _WORD_RE.findall(text or "")]


def _load_raw_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _load_product_descriptions(path: Path) -> str:
    try:
        payload: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""

    if not isinstance(payload, dict) or not isinstance(payload.get("products"), list):
        return ""

    descriptions: list[str] = []
    for product in payload["products"]:
        if not isinstance(product, dict):
            continue
        body_html = product.get("body_html")
        if isinstance(body_html, str) and body_html.strip():
            descriptions.append(body_html)
        title = product.get("title")
        if isinstance(title, str) and title.strip():
            descriptions.append(title)

    return "\n".join(descriptions)


def analyze_text(
    raw_text_path: str | Path = "memory/raw_text.txt",
    raw_products_path: str | Path = "memory/raw_products.json",
    output_path: str | Path = "memory/text_metrics.json",
) -> bool:
    """Analyze text and product descriptions; write summary metrics JSON.

    Metrics:
    - word counts (homepage, product_descriptions, total)
    - CTA frequency (count and ratio)
    - emotional word ratio
    """
    base_dir = Path(__file__).resolve().parents[1]

    raw_text_file = Path(raw_text_path)
    if not raw_text_file.is_absolute():
        raw_text_file = base_dir / raw_text_file

    raw_products_file = Path(raw_products_path)
    if not raw_products_file.is_absolute():
        raw_products_file = base_dir / raw_products_file

    out_file = Path(output_path)
    if not out_file.is_absolute():
        out_file = base_dir / out_file

    homepage_text = _load_raw_text(raw_text_file)
    product_text = _load_product_descriptions(raw_products_file)

    homepage_tokens = _tokenize(homepage_text)
    product_tokens = _tokenize(product_text)
    all_tokens = homepage_tokens + product_tokens

    total_words = len(all_tokens)
    cta_count = sum(1 for t in all_tokens if t in _CTA_TERMS)
    emotional_count = sum(1 for t in all_tokens if t in _EMOTIONAL_TERMS)

    result = {
        "word_counts": {
            "homepage": len(homepage_tokens),
            "product_descriptions": len(product_tokens),
            "total": total_words,
        },
        "cta_frequency": {
            "count": cta_count,
            "ratio": round(cta_count / total_words, 4) if total_words else 0.0,
        },
        "emotional_word_ratio": round(emotional_count / total_words, 4) if total_words else 0.0,
    }

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return True
