"""Token pricing models for all LLMs (February 2026)."""

MODEL_PRICING = {
    "gpt-5-nano": {
        "input_per_1m": 0.05,
        "output_per_1m": 0.40,
        "label": "GPT-5 Nano (Classifier)",
        "color": "#059669",
        "provider": "openai",
    },
    "gpt-5-mini": {
        "input_per_1m": 0.25,
        "output_per_1m": 2.00,
        "label": "GPT-5 Mini (Medium)",
        "color": "#D97706",
        "provider": "openai",
    },
    "claude-sonnet-4": {
        "input_per_1m": 3.00,
        "output_per_1m": 15.00,
        "label": "Claude Sonnet 4 (Complex)",
        "color": "#7C3AED",
        "provider": "anthropic",
    },
    "gpt-5": {
        "input_per_1m": 1.25,
        "output_per_1m": 10.00,
        "label": "GPT-5 (Reference)",
        "color": "#009de2",
        "provider": "openai",
    },
    "gpt-5.2": {
        "input_per_1m": 1.75,
        "output_per_1m": 14.00,
        "label": "GPT-5.2 Thinking (Flagship)",
        "color": "#EF4444",
        "provider": "openai",
    },
}

ROUTING_MODELS = ["gpt-5-nano", "gpt-5-mini", "claude-sonnet-4"]
REFERENCE_MODELS = ["gpt-5", "gpt-5.2"]
ALL_MODELS_ORDERED = ["gpt-5-nano", "gpt-5-mini", "gpt-5", "gpt-5.2", "claude-sonnet-4"]


def calculate_cost(model, input_tokens, output_tokens):
    """Calculate USD cost for a single model call."""
    pricing = MODEL_PRICING.get(model)
    if not pricing:
        return 0.0
    input_cost = (input_tokens / 1_000_000) * pricing["input_per_1m"]
    output_cost = (output_tokens / 1_000_000) * pricing["output_per_1m"]
    return input_cost + output_cost


def calculate_all_models_cost(input_tokens, output_tokens):
    """Calculate cost across all models for the same token count."""
    return {
        model: calculate_cost(model, input_tokens, output_tokens)
        for model in ALL_MODELS_ORDERED
    }


def get_most_expensive_model():
    """Return the model ID with highest combined cost per 1M tokens."""
    return max(
        MODEL_PRICING.keys(),
        key=lambda m: MODEL_PRICING[m]["input_per_1m"] + MODEL_PRICING[m]["output_per_1m"],
    )


def calculate_savings(actual_cost, input_tokens, output_tokens):
    """Calculate savings vs. most expensive model.

    Returns dict with savings_pct, savings_abs, max_cost, max_model.
    """
    max_model = get_most_expensive_model()
    max_cost = calculate_cost(max_model, input_tokens, output_tokens)

    if max_cost == 0:
        return {
            "savings_pct": 0.0,
            "savings_abs": 0.0,
            "max_cost": 0.0,
            "max_model": max_model,
            "max_model_label": MODEL_PRICING[max_model]["label"],
        }

    savings_abs = max_cost - actual_cost
    savings_pct = (savings_abs / max_cost) * 100 if max_cost > 0 else 0.0

    return {
        "savings_pct": round(savings_pct, 1),
        "savings_abs": savings_abs,
        "max_cost": max_cost,
        "max_model": max_model,
        "max_model_label": MODEL_PRICING[max_model]["label"],
    }
