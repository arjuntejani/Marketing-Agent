"""Utilities to detect whether a store URL appears to be a Shopify shop."""

from urllib.parse import urlparse

import requests


def _normalize_url(url: str) -> str:
    """Normalize a URL by ensuring it includes a scheme."""
    parsed = urlparse(url)
    if parsed.scheme:
        return url
    return f"https://{url}"


def is_shopify_store(url: str, timeout: int = 8) -> bool:
    """Return True if the provided URL appears to be a Shopify store.

    Detection strategy:
    1. Request the homepage and look for Shopify-specific markers.
    2. Request ``/products.json`` and confirm a successful JSON response
       containing a ``products`` key.

    Args:
        url: Store URL (with or without scheme).
        timeout: Request timeout in seconds.

    Returns:
        bool: True if Shopify signals are detected; otherwise False.
    """
    if not isinstance(url, str) or not url.strip():
        return False

    base_url = _normalize_url(url.strip()).rstrip("/")
    headers = {"User-Agent": "BrandBrainAI-ShopifyDetector/1.0"}

    try:
        home_response = requests.get(base_url, headers=headers, timeout=timeout)
        home_text = home_response.text.lower()
        shopify_markers = (
            "cdn.shopify.com",
            "shopify.theme",
            "x-shopify-stage",
            "shopify",
        )
        has_shopify_marker = any(marker in home_text for marker in shopify_markers)

        products_response = requests.get(
            f"{base_url}/products.json", headers=headers, timeout=timeout
        )

        if products_response.status_code != 200:
            return False

        content_type = products_response.headers.get("Content-Type", "").lower()
        if "json" not in content_type and not products_response.text.strip().startswith("{"):
            return False

        payload = products_response.json()
        has_products_key = isinstance(payload, dict) and "products" in payload

        return has_shopify_marker and has_products_key
    except (requests.RequestException, ValueError, TypeError):
        return False
