"""CSS parsing helpers for extracting primary colors and fonts from HTML/CSS."""

from __future__ import annotations

import re
from typing import List, Tuple

from bs4 import BeautifulSoup

_COLOR_PATTERN = re.compile(
    r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b"
    r"|rgba?\([^\)]+\)"
    r"|hsla?\([^\)]+\)"
)

_NAMED_COLORS = {
    "black",
    "white",
    "red",
    "green",
    "blue",
    "yellow",
    "orange",
    "purple",
    "pink",
    "gray",
    "grey",
    "brown",
    "teal",
    "navy",
    "maroon",
    "olive",
    "lime",
    "aqua",
    "silver",
    "gold",
    "beige",
    "coral",
    "crimson",
    "indigo",
    "ivory",
    "khaki",
    "lavender",
    "magenta",
    "plum",
    "salmon",
    "tan",
    "tomato",
    "turquoise",
    "violet",
}


def _extract_style_blocks(html: str) -> str:
    """Return all inline <style> content from HTML."""
    soup = BeautifulSoup(html or "", "html.parser")
    return "\n".join(style.get_text(" ", strip=True) for style in soup.find_all("style"))


def _normalize_font_name(value: str) -> str:
    """Normalize a font token by removing wrapping quotes and extra spaces."""
    return value.strip().strip("\"'")


def parse_css_theme(html: str, css: str) -> Tuple[List[str], List[str]]:
    """Extract primary colors and fonts from HTML + CSS input.

    Args:
        html: Raw HTML content (used to read inline <style> blocks).
        css: Raw CSS text.

    Returns:
        tuple[list[str], list[str]]: (colors, fonts)
    """
    combined_css = "\n".join(filter(None, [css or "", _extract_style_blocks(html)]))

    colors: List[str] = []
    fonts: List[str] = []

    # Hex/RGB/HSL colors
    for match in _COLOR_PATTERN.findall(combined_css):
        color = match.strip().lower()
        if color not in colors:
            colors.append(color)

    # Named colors in common color properties
    for match in re.findall(
        r"(?:color|background(?:-color)?|border-color)\s*:\s*([a-zA-Z]+)",
        combined_css,
        flags=re.IGNORECASE,
    ):
        color_name = match.strip().lower()
        if color_name in _NAMED_COLORS and color_name not in colors:
            colors.append(color_name)

    # Font extraction from font-family declarations
    for family_block in re.findall(r"font-family\s*:\s*([^;}{]+)", combined_css, flags=re.IGNORECASE):
        for candidate in family_block.split(","):
            font = _normalize_font_name(candidate)
            if not font:
                continue
            # skip generic family keywords only
            if font.lower() in {"serif", "sans-serif", "monospace", "cursive", "fantasy", "system-ui"}:
                continue
            if font not in fonts:
                fonts.append(font)

    return colors, fonts
