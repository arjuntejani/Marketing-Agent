"""Utilities for fetching and persisting product data from Shopify-like stores."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def _normalize_store_url(store_url: str) -> str:
    """Ensure the provided store URL includes a scheme and no trailing slash."""
    parsed = urlparse(store_url)
    if not parsed.scheme:
        store_url = f"https://{store_url}"
    return store_url.rstrip("/")


def fetch_and_save_products(
    store_url: str,
    output_path: str | Path = "memory/raw_products.json",
    timeout: int = 10,
) -> bool:
    """Fetch ``/products.json`` from a store and save it locally.

    Args:
        store_url: Base storefront URL (e.g., ``store.com`` or ``https://store.com``).
        output_path: Destination path for the raw products JSON.
        timeout: Request timeout in seconds.

    Returns:
        True if products JSON is fetched and saved successfully, otherwise False.
    """
    if not isinstance(store_url, str) or not store_url.strip():
        return False

    base_url = _normalize_store_url(store_url.strip())
    products_url = f"{base_url}/products.json"

    request = Request(
        products_url,
        headers={"User-Agent": "BrandBrainAI-ProductFetcher/1.0"},
        method="GET",
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            raw_body = response.read().decode("utf-8", errors="replace")
    except (URLError, TimeoutError, ValueError):
        return False

    try:
        payload: Any = json.loads(raw_body)
    except json.JSONDecodeError:
        return False

    output = Path(output_path)
    if not output.is_absolute():
        output = Path(__file__).resolve().parents[1] / output

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return True
