"""Token cost calculation and comparison utilities."""

from pricing import (
    MODEL_PRICING,
    ALL_MODELS_ORDERED,
    calculate_cost,
    calculate_savings,
)


def format_cost(cost_usd):
    """Format USD cost for display."""
    if cost_usd < 0.001:
        return f"${cost_usd:.6f}"
    if cost_usd < 0.01:
        return f"${cost_usd:.4f}"
    return f"${cost_usd:.4f}"


def build_comparison_table(total_input_tokens, total_output_tokens):
    """Build cost comparison across all 5 models.

    Returns list of dicts with model info and calculated costs.
    """
    rows = []
    for model_id in ALL_MODELS_ORDERED:
        info = MODEL_PRICING[model_id]
        cost = calculate_cost(model_id, total_input_tokens, total_output_tokens)
        rows.append({
            "model_id": model_id,
            "label": info["label"],
            "color": info["color"],
            "input_cost": (total_input_tokens / 1_000_000) * info["input_per_1m"],
            "output_cost": (total_output_tokens / 1_000_000) * info["output_per_1m"],
            "total_cost": cost,
        })
    return rows


def build_savings_summary(
    classifier_model,
    classifier_input_tokens,
    classifier_output_tokens,
    proposal_model,
    proposal_input_tokens,
    proposal_output_tokens,
):
    """Build comprehensive savings summary for the token economy dashboard.

    Returns dict with all cost breakdowns and savings metrics.
    """
    classifier_cost = calculate_cost(
        classifier_model, classifier_input_tokens, classifier_output_tokens
    )
    proposal_cost = calculate_cost(
        proposal_model, proposal_input_tokens, proposal_output_tokens
    )
    actual_total_cost = classifier_cost + proposal_cost

    total_input = classifier_input_tokens + proposal_input_tokens
    total_output = classifier_output_tokens + proposal_output_tokens

    savings = calculate_savings(actual_total_cost, total_input, total_output)

    return {
        "classifier_cost": classifier_cost,
        "proposal_cost": proposal_cost,
        "actual_total_cost": actual_total_cost,
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "total_tokens": total_input + total_output,
        **savings,
    }
