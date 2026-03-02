"""Simple webpage text scraper for homepage content extraction."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


def _normalize_url(url: str) -> str:
    """Ensure URL has a scheme and no trailing whitespace."""
    cleaned = url.strip()
    parsed = urlparse(cleaned)
    if parsed.scheme:
        return cleaned
    return f"https://{cleaned}"


def scrape_homepage_text(
    url: str,
    output_path: str | Path = "memory/raw_text.txt",
    timeout: int = 10,
) -> bool:
    """Download homepage, extract key text blocks, and save to disk.

    Extracted sections:
    - Meta description
    - Hero text (first heading + first prominent paragraph)
    - About section text (if an about-like section exists)
    """
    if not isinstance(url, str) or not url.strip():
        return False

    target_url = _normalize_url(url)
    headers = {"User-Agent": "BrandBrainAI-Scraper/1.0"}

    try:
        response = requests.get(target_url, headers=headers, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException:
        return False

    soup = BeautifulSoup(response.text, "html.parser")

    # Meta description
    meta_description = ""
    meta_tag = soup.find("meta", attrs={"name": "description"})
    if meta_tag and meta_tag.get("content"):
        meta_description = meta_tag.get("content", "").strip()

    # Hero text candidates: first h1/h2 and first paragraph
    hero_heading = ""
    heading_tag = soup.find(["h1", "h2"])
    if heading_tag:
        hero_heading = heading_tag.get_text(" ", strip=True)

    hero_paragraph = ""
    paragraph_tag = soup.find("p")
    if paragraph_tag:
        hero_paragraph = paragraph_tag.get_text(" ", strip=True)

    # About section extraction
    about_text = ""
    about_container = soup.find(
        lambda tag: tag.name in {"section", "div", "article"}
        and (
            (tag.get("id") and "about" in str(tag.get("id")).lower())
            or any("about" in cls.lower() for cls in (tag.get("class") or []))
        )
    )
    if about_container:
        about_text = about_container.get_text(" ", strip=True)

    parts = [
        "META DESCRIPTION:\n" + (meta_description or "N/A"),
        "\nHERO TEXT:\n" + "\n".join([t for t in [hero_heading, hero_paragraph] if t])
        if (hero_heading or hero_paragraph)
        else "\nHERO TEXT:\nN/A",
        "\nABOUT:\n" + (about_text or "N/A"),
    ]

    output = Path(output_path)
    if not output.is_absolute():
        output = Path(__file__).resolve().parents[1] / output

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n\n".join(parts).strip() + "\n", encoding="utf-8")
    return True
