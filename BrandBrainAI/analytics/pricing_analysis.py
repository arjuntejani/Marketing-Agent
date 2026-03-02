"""Pricing analysis utilities for product feeds."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _to_float(value: Any) -> float | None:
    """Safely convert incoming price-like values to float."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "")
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def analyze_pricing(
    input_path: str | Path = "memory/raw_products.json",
    output_path: str | Path = "memory/pricing_analysis.json",
) -> bool:
    """Analyze product pricing and persist summary statistics.

    Expected input shape is Shopify-like: ``{"products": [...]}``.
    The function scans variants for ``price`` and ``compare_at_price``.

    Outputs:
    - average_price
    - average_discount_percent
    - price_range {min, max}
    - product_count
    - priced_variant_count
    """
    in_path = Path(input_path)
    if not in_path.is_absolute():
        in_path = Path(__file__).resolve().parents[1] / in_path

    out_path = Path(output_path)
    if not out_path.is_absolute():
        out_path = Path(__file__).resolve().parents[1] / out_path

    if not in_path.exists():
        return False

    try:
        payload = json.loads(in_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False

    products = payload.get("products") if isinstance(payload, dict) else None
    if not isinstance(products, list):
        return False

    prices: list[float] = []
    discount_percents: list[float] = []

    for product in products:
        if not isinstance(product, dict):
            continue
        variants = product.get("variants", [])
        if not isinstance(variants, list):
            continue

        for variant in variants:
            if not isinstance(variant, dict):
                continue

            price = _to_float(variant.get("price"))
            if price is None:
                continue

            prices.append(price)

            compare_at = _to_float(variant.get("compare_at_price"))
            if compare_at is not None and compare_at > 0 and compare_at > price:
                discount_pct = ((compare_at - price) / compare_at) * 100.0
                discount_percents.append(discount_pct)

    if prices:
        average_price = round(sum(prices) / len(prices), 2)
        min_price = round(min(prices), 2)
        max_price = round(max(prices), 2)
    else:
        average_price = None
        min_price = None
        max_price = None

    average_discount = round(sum(discount_percents) / len(discount_percents), 2) if discount_percents else 0.0

    result = {
        "average_price": average_price,
        "average_discount_percent": average_discount,
        "price_range": {"min": min_price, "max": max_price},
        "product_count": len(products),
        "priced_variant_count": len(prices),
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return True
