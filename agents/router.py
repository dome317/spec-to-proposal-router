"""Model routing logic based on complexity classification."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pricing import MODEL_PRICING, calculate_cost

ROUTING_TABLE = {
    "SIMPLE": "gpt-5-nano",
    "MEDIUM": "gpt-5-mini",
    "COMPLEX": "claude-sonnet-4-20250514",
}

DISPLAY_NAMES = {
    "gpt-5-nano": "GPT-5 Nano",
    "gpt-5-mini": "GPT-5 Mini",
    "claude-sonnet-4-20250514": "Claude Sonnet 4",
}

ROUTING_RATIONALE = {
    "SIMPLE": (
        "Standard request with clear parameters detected. "
        "GPT-5 Nano is sufficient for direct catalog lookup \u2014 "
        "fastest and cheapest model."
    ),
    "MEDIUM": (
        "Medium complexity with multiple parameters. "
        "GPT-5 Mini provides enhanced analysis capabilities "
        "at moderate cost."
    ),
    "COMPLEX": (
        "High complexity with system integration / unusual specs. "
        "Claude Sonnet 4 deployed for deep technical analysis and "
        "creative solution development."
    ),
}


def route(classification):
    """Determine which model to use based on classification.

    Args:
        classification: Dict from classifier with at least 'complexity' key.

    Returns:
        Dict with selected_model, selected_model_label, complexity,
        rationale, classifier_cost.
    """
    complexity = classification.get("complexity", "MEDIUM")
    if complexity not in ROUTING_TABLE:
        complexity = "MEDIUM"

    selected_model = ROUTING_TABLE[complexity]
    classifier_cost = calculate_cost(
        "gpt-5-nano",
        classification.get("input_tokens", 0),
        classification.get("output_tokens", 0),
    )

    return {
        "selected_model": selected_model,
        "selected_model_label": DISPLAY_NAMES.get(selected_model, selected_model),
        "complexity": complexity,
        "rationale": ROUTING_RATIONALE[complexity],
        "classifier_cost": classifier_cost,
        "classifier_latency_ms": classification.get("latency_ms", 0),
    }
