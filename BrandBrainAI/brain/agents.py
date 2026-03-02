"""Agent utilities for generating strategic and creative outputs from brand artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from BrandBrainAI.brain.model_interface import generate_response


def _resolve_path(path: str | Path) -> Path:
    p = Path(path)
    if p.is_absolute():
        return p
    return Path(__file__).resolve().parents[1] / p


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def strategy_agent(
    brand_dna_path: str | Path = "memory/brand_dna.json",
    output_path: str | Path = "memory/strategy.json",
) -> dict[str, Any]:
    """Generate a strategy JSON from Brand DNA.

    Output keys:
    - campaign_objective
    - emotional_trigger
    - psychological_lever
    """
    dna_path = _resolve_path(brand_dna_path)
    out_path = _resolve_path(output_path)

    brand_dna = _load_json(dna_path)

    summary = str(brand_dna.get("brand_summary", "")).lower()
    voice = brand_dna.get("voice_tone", {}) if isinstance(brand_dna.get("voice_tone"), dict) else {}
    emotional_ratio = float(voice.get("emotional_ratio", 0.0) or 0.0)
    pricing = (
        brand_dna.get("pricing_positioning", {})
        if isinstance(brand_dna.get("pricing_positioning"), dict)
        else {}
    )
    avg_discount = float(pricing.get("average_discount_percent", 0.0) or 0.0)

    if any(k in summary for k in ["premium", "luxury", "exclusive"]):
        campaign_objective = "Increase perceived brand value and premium conversion"
    elif avg_discount >= 20:
        campaign_objective = "Drive promotional conversion and short-term sales lift"
    else:
        campaign_objective = "Grow consideration and improve conversion intent"

    if emotional_ratio >= 0.2:
        emotional_trigger = "Aspirational identity and confidence"
    elif any(k in summary for k in ["safe", "trusted", "reliable"]):
        emotional_trigger = "Trust and security reassurance"
    else:
        emotional_trigger = "Curiosity and discovery"

    if avg_discount >= 20:
        psychological_lever = "Loss aversion (limited-time savings)"
    elif "premium" in summary or "luxury" in summary:
        psychological_lever = "Status signaling and social proof"
    else:
        psychological_lever = "Clarity and cognitive ease"

    strategy = {
        "campaign_objective": campaign_objective,
        "emotional_trigger": emotional_trigger,
        "psychological_lever": psychological_lever,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(strategy, indent=2, ensure_ascii=False), encoding="utf-8")
    return strategy


def _creative_prompt(brand_dna: dict[str, Any], strategy: dict[str, Any]) -> str:
    return (
        "You are a performance creative strategist.\n"
        "Generate campaign assets as strict JSON only (no markdown).\n"
        "Schema:\n"
        "{\n"
        '  "social_posts": ["string", "string", "string"],\n'
        '  "email_drafts": [{"subject": "string", "body": "string"}, {"subject": "string", "body": "string"}],\n'
        '  "ad_copy": [{"headline": "string", "primary_text": "string", "cta": "string"}, {"headline": "string", "primary_text": "string", "cta": "string"}]\n'
        "}\n\n"
        f"BRAND_DNA:\n{json.dumps(brand_dna, ensure_ascii=False)}\n\n"
        f"STRATEGY:\n{json.dumps(strategy, ensure_ascii=False)}"
    )


def _default_campaign(brand_dna: dict[str, Any], strategy: dict[str, Any]) -> dict[str, Any]:
    summary = str(brand_dna.get("brand_summary", "Your brand")).strip()[:120]
    trigger = str(strategy.get("emotional_trigger", "confidence"))
    objective = str(strategy.get("campaign_objective", "drive conversions"))

    return {
        "social_posts": [
            f"{summary} — built to inspire {trigger.lower()}.",
            f"New from our brand: crafted for people who value {trigger.lower()}.",
            f"Ready to elevate your routine? Discover what makes us different.",
        ],
        "email_drafts": [
            {
                "subject": "A smarter way to experience our brand",
                "body": f"We’re focused on one goal: {objective.lower()}. Discover our latest collection today.",
            },
            {
                "subject": "Your next favorite product is here",
                "body": "Explore handpicked favorites designed for everyday impact. Shop now and see the difference.",
            },
        ],
        "ad_copy": [
            {
                "headline": "Elevate Your Everyday",
                "primary_text": f"Designed to spark {trigger.lower()} and help you act with confidence.",
                "cta": "Shop Now",
            },
            {
                "headline": "Make the Switch Today",
                "primary_text": "Discover products made for quality, clarity, and results.",
                "cta": "Learn More",
            },
        ],
    }


def creative_agent(
    brand_dna_path: str | Path = "memory/brand_dna.json",
    strategy_path: str | Path = "memory/strategy.json",
    output_path: str | Path = "memory/campaign_creatives.json",
    temperature: float = 0.7,
    max_tokens: int = 900,
) -> dict[str, Any]:
    """Generate campaign creatives from brand DNA + strategy and save JSON."""
    dna = _load_json(_resolve_path(brand_dna_path))
    strategy = _load_json(_resolve_path(strategy_path))
    out_path = _resolve_path(output_path)

    prompt = _creative_prompt(dna, strategy)
    llm_text = generate_response(prompt=prompt, temperature=temperature, max_tokens=max_tokens)

    campaign = _default_campaign(dna, strategy)
    if isinstance(llm_text, str) and llm_text.strip():
        try:
            parsed = json.loads(llm_text)
            if isinstance(parsed, dict):
                campaign = {
                    "social_posts": parsed.get("social_posts", campaign["social_posts"]),
                    "email_drafts": parsed.get("email_drafts", campaign["email_drafts"]),
                    "ad_copy": parsed.get("ad_copy", campaign["ad_copy"]),
                }
        except json.JSONDecodeError:
            pass

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(campaign, indent=2, ensure_ascii=False), encoding="utf-8")
    return campaign


def _rule_refine_headline(text: str) -> str:
    s = (text or '').strip()
    if not s:
        return 'Upgrade Your Routine Today'
    if len(s) > 70:
        s = s[:67].rstrip() + '...'
    if not any(ch.isdigit() for ch in s) and len(s.split()) > 3:
        s = f"{s} — See Results Fast"
    return s


def _rule_refine_cta(cta: str) -> str:
    c = (cta or '').strip().lower()
    mapping = {
        'learn more': 'Get Started',
        'shop now': 'Shop Now',
        'buy now': 'Buy Now',
        'subscribe': 'Start Free Trial',
        'sign up': 'Get Started',
    }
    if c in mapping:
        return mapping[c]
    if not c:
        return 'Get Started'
    return c.title()


def _rule_refine_hook(text: str) -> str:
    s = (text or '').strip()
    if not s:
        return 'Discover the easiest way to get better results today.'
    if len(s) < 40:
        s = s + ' Built to convert interest into action.'
    # Add urgency cue if absent.
    urgency_words = ('today', 'now', 'limited', 'fast')
    if not any(w in s.lower() for w in urgency_words):
        s = s.rstrip('.') + ' — Act today.'
    return s


def _performance_prompt(campaign: dict[str, Any]) -> str:
    return (
        'You are a conversion copywriter. Refine headlines, CTAs, and hooks for higher conversion.\n'
        'Return strict JSON only (no markdown) with schema:\n'
        '{\n'
        '  "ad_copy": [{"headline": "string", "primary_text": "string", "cta": "string"}],\n'
        '  "social_posts": ["string"]\n'
        '}\n\n'
        f'INPUT_CAMPAIGN:\n{json.dumps(campaign, ensure_ascii=False)}'
    )


def performance_agent(
    campaign_path: str | Path = 'memory/campaign_creatives.json',
    output_path: str | Path = 'memory/campaign_performance.json',
    use_llm: bool = True,
    temperature: float = 0.4,
    max_tokens: int = 700,
) -> dict[str, Any]:
    """Refine hooks/headlines/CTAs for conversion using rules + optional local LLM."""
    campaign = _load_json(_resolve_path(campaign_path))

    refined = {
        'social_posts': [],
        'email_drafts': campaign.get('email_drafts', []),
        'ad_copy': [],
    }

    social_posts = campaign.get('social_posts', []) if isinstance(campaign.get('social_posts'), list) else []
    for post in social_posts:
        if isinstance(post, str):
            refined['social_posts'].append(_rule_refine_hook(post))

    ad_copy = campaign.get('ad_copy', []) if isinstance(campaign.get('ad_copy'), list) else []
    for ad in ad_copy:
        if not isinstance(ad, dict):
            continue
        refined['ad_copy'].append(
            {
                'headline': _rule_refine_headline(str(ad.get('headline', ''))),
                'primary_text': _rule_refine_hook(str(ad.get('primary_text', ''))),
                'cta': _rule_refine_cta(str(ad.get('cta', ''))),
            }
        )

    if use_llm:
        prompt = _performance_prompt(refined)
        llm_text = generate_response(prompt=prompt, temperature=temperature, max_tokens=max_tokens)
        if isinstance(llm_text, str) and llm_text.strip():
            try:
                parsed = json.loads(llm_text)
                if isinstance(parsed, dict):
                    refined = {
                        'social_posts': parsed.get('social_posts', refined['social_posts']),
                        'email_drafts': refined.get('email_drafts', []),
                        'ad_copy': parsed.get('ad_copy', refined['ad_copy']),
                    }
            except json.JSONDecodeError:
                pass

    out = _resolve_path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(refined, indent=2, ensure_ascii=False), encoding='utf-8')
    return refined


def _avg(values: list[float]) -> float:
    return round(sum(values) / len(values), 2) if values else 0.0


def _score_brand_consistency(campaign: dict[str, Any], brand_dna: dict[str, Any]) -> float:
    brand_terms = set(str(brand_dna.get('brand_summary', '')).lower().split())
    brand_terms = {w.strip('.,!?') for w in brand_terms if len(w) > 4}

    corpus = []
    for post in campaign.get('social_posts', []) if isinstance(campaign.get('social_posts'), list) else []:
        if isinstance(post, str):
            corpus.append(post.lower())
    for ad in campaign.get('ad_copy', []) if isinstance(campaign.get('ad_copy'), list) else []:
        if isinstance(ad, dict):
            corpus.append(str(ad.get('headline', '')).lower())
            corpus.append(str(ad.get('primary_text', '')).lower())

    if not corpus or not brand_terms:
        return 60.0

    matches = 0
    total = 0
    joined = ' '.join(corpus)
    for term in list(brand_terms)[:40]:
        total += 1
        if term in joined:
            matches += 1
    return round((matches / total) * 100, 2) if total else 60.0


def _score_emotional_resonance(campaign: dict[str, Any], brand_dna: dict[str, Any]) -> float:
    trigger = str((brand_dna.get('voice_tone', {}) if isinstance(brand_dna.get('voice_tone'), dict) else {}).get('style', '')).lower()
    emotional_words = {
        'love','joy','confidence','inspire','inspired','excited','premium','bold','happy','trust','safe','exclusive','amazing'
    }
    if trigger:
        emotional_words.update(trigger.split())

    texts = []
    texts.extend([x for x in campaign.get('social_posts', []) if isinstance(x, str)] if isinstance(campaign.get('social_posts'), list) else [])
    for ad in campaign.get('ad_copy', []) if isinstance(campaign.get('ad_copy'), list) else []:
        if isinstance(ad, dict):
            texts.append(str(ad.get('primary_text', '')))

    tokens = ' '.join(texts).lower().split()
    if not tokens:
        return 50.0
    hits = sum(1 for t in tokens if t.strip('.,!?') in emotional_words)
    ratio = hits / len(tokens)
    return round(min(100.0, ratio * 600), 2)


def _score_conversion_potential(campaign: dict[str, Any]) -> float:
    strong_ctas = {'shop now','buy now','get started','start free trial','claim offer','learn more'}
    hooks = 0
    ctas = 0
    ad_count = 0

    for post in campaign.get('social_posts', []) if isinstance(campaign.get('social_posts'), list) else []:
        if isinstance(post, str) and any(k in post.lower() for k in ['today', 'now', 'limited', 'discover']):
            hooks += 1

    for ad in campaign.get('ad_copy', []) if isinstance(campaign.get('ad_copy'), list) else []:
        if not isinstance(ad, dict):
            continue
        ad_count += 1
        cta = str(ad.get('cta', '')).strip().lower()
        if cta in strong_ctas:
            ctas += 1
        pt = str(ad.get('primary_text', '')).lower()
        if any(k in pt for k in ['today', 'now', 'limited', 'save', 'results']):
            hooks += 1

    if ad_count == 0:
        return 50.0
    cta_score = (ctas / ad_count) * 60
    hook_score = min(40.0, hooks * 10.0)
    return round(min(100.0, cta_score + hook_score), 2)


def _rewrite_weak_parts(campaign: dict[str, Any], weak_dimensions: list[str]) -> dict[str, Any]:
    improved = {
        'social_posts': list(campaign.get('social_posts', [])) if isinstance(campaign.get('social_posts'), list) else [],
        'email_drafts': list(campaign.get('email_drafts', [])) if isinstance(campaign.get('email_drafts'), list) else [],
        'ad_copy': list(campaign.get('ad_copy', [])) if isinstance(campaign.get('ad_copy'), list) else [],
    }

    if 'conversion_potential' in weak_dimensions:
        # Apply conversion-focused rule refinement.
        for i, ad in enumerate(improved['ad_copy']):
            if isinstance(ad, dict):
                improved['ad_copy'][i] = {
                    'headline': _rule_refine_headline(str(ad.get('headline', ''))),
                    'primary_text': _rule_refine_hook(str(ad.get('primary_text', ''))),
                    'cta': _rule_refine_cta(str(ad.get('cta', ''))),
                }

    if 'emotional_resonance' in weak_dimensions:
        improved['social_posts'] = [
            _rule_refine_hook(str(p)) + ' Feel the difference.' for p in improved['social_posts']
        ]

    if 'brand_consistency' in weak_dimensions and improved['social_posts']:
        improved['social_posts'][0] = 'From our brand promise: ' + improved['social_posts'][0]

    return improved


def evaluation_agent(
    campaign_path: str | Path = 'memory/campaign_performance.json',
    brand_dna_path: str | Path = 'memory/brand_dna.json',
    output_path: str | Path = 'memory/campaign_evaluation.json',
    threshold: float = 70.0,
) -> dict[str, Any]:
    """Score campaign quality and rewrite weak parts if any score is below threshold."""
    campaign = _load_json(_resolve_path(campaign_path))
    brand_dna = _load_json(_resolve_path(brand_dna_path))

    scores = {
        'brand_consistency': _score_brand_consistency(campaign, brand_dna),
        'emotional_resonance': _score_emotional_resonance(campaign, brand_dna),
        'conversion_potential': _score_conversion_potential(campaign),
    }
    overall_score = _avg(list(scores.values()))
    weak = [k for k, v in scores.items() if v < threshold]

    improved_campaign = campaign
    rewritten = False
    if weak:
        improved_campaign = _rewrite_weak_parts(campaign, weak)
        rewritten = True

    result = {
        'scores': scores,
        'overall_score': overall_score,
        'threshold': threshold,
        'weak_dimensions': weak,
        'rewritten': rewritten,
        'campaign': improved_campaign,
    }

    out = _resolve_path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    return result
