"""BrandBrainAI pipeline entrypoint.

Flow:
1) Accept URL input
2) Run extractors
3) Run analytics
4) Build Brand DNA
5) Run agents in sequence
6) Output final campaign JSON
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from BrandBrainAI.analytics.pricing_analysis import analyze_pricing
from BrandBrainAI.analytics.text_analysis import analyze_text
from BrandBrainAI.brain.agents import creative_agent, evaluation_agent, performance_agent, strategy_agent
from BrandBrainAI.brain.brand_dna_builder import build_brand_dna
from BrandBrainAI.extractor.product_fetcher import fetch_and_save_products
from BrandBrainAI.extractor.scraper import scrape_homepage_text
from BrandBrainAI.extractor.shopify_detector import is_shopify_store


def run_pipeline(url: str, final_output: str | Path = "memory/final_campaign.json") -> dict:
    """Run full BrandBrainAI pipeline and return final campaign payload."""
    base_dir = Path(__file__).resolve().parent
    output_path = Path(final_output)
    if not output_path.is_absolute():
        output_path = base_dir / output_path

    # 1) Extractor stage
    scrape_homepage_text(url)

    # Product extraction is attempted regardless; Shopify check informs logs/metadata only.
    shopify_detected = is_shopify_store(url)
    fetch_and_save_products(url)

    # 2) Analytics stage
    analyze_pricing()
    analyze_text()

    # 3) Brand DNA stage
    build_brand_dna()

    # 4) Agents stage (strategy -> creative -> performance -> evaluation)
    strategy = strategy_agent()
    creatives = creative_agent()
    performance = performance_agent()
    evaluation = evaluation_agent()

    final_campaign = {
        "input_url": url,
        "shopify_detected": bool(shopify_detected),
        "strategy": strategy,
        "creatives": creatives,
        "performance": performance,
        "evaluation": evaluation,
        "final_campaign": evaluation.get("campaign", performance),
        "final_output_path": str(output_path),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(final_campaign, indent=2, ensure_ascii=False), encoding="utf-8")
    return final_campaign


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the BrandBrainAI end-to-end pipeline.")
    parser.add_argument("url", help="Target store URL (e.g. https://store.com)")
    parser.add_argument(
        "--output",
        default="memory/final_campaign.json",
        help="Path for final campaign JSON output (default: memory/final_campaign.json)",
    )
    return parser


def _print_summary(result: dict) -> None:
    """Print a concise human-readable summary after pipeline execution."""
    evaluation = result.get("evaluation", {}) if isinstance(result.get("evaluation"), dict) else {}
    scores = evaluation.get("scores", {}) if isinstance(evaluation.get("scores"), dict) else {}

    print("\n=== BrandBrainAI Pipeline Summary ===")
    print(f"URL: {result.get('input_url', 'N/A')}")
    print(f"Shopify detected: {result.get('shopify_detected', False)}")
    print(f"Final campaign file: {result.get('final_output_path', 'N/A')}")
    print(f"Overall score: {evaluation.get('overall_score', 'N/A')}")

    if scores:
        print("Scores:")
        print(f"  - Brand consistency: {scores.get('brand_consistency', 'N/A')}")
        print(f"  - Emotional resonance: {scores.get('emotional_resonance', 'N/A')}")
        print(f"  - Conversion potential: {scores.get('conversion_potential', 'N/A')}")


def main() -> None:
    args = _build_parser().parse_args()
    result = run_pipeline(url=args.url, final_output=args.output)
    _print_summary(result)


if __name__ == "__main__":
    main()
