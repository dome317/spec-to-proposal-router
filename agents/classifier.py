"""Complexity classifier agent using GPT-5 Nano."""

import json
import time

CLASSIFIER_SYSTEM_PROMPT = """You are a technical classifier for laser and photonics requests.
Analyze the customer specification and classify the complexity:

SIMPLE: Standard wavelengths (405-1064nm), clear power specification, standard application
-> Simple catalog lookup is sufficient

MEDIUM: Multiple parameters simultaneously, specific noise requirements,
combination of multiple wavelengths
-> Extended matching and parameter comparison needed

COMPLEX: Unusual wavelengths, THz range, physical calculations,
custom solutions, system integration, multi-component setup
-> Deep technical analysis and creative proposal needed

Respond ONLY with a JSON object:
{"complexity": "SIMPLE|MEDIUM|COMPLEX", "reasoning": "brief explanation", "key_parameters": ["param1", "param2"]}"""


def classify_spec(spec, demo_mode=True):
    """Classify customer specification complexity.

    Args:
        spec: Customer specification text.
        demo_mode: If True, return mock data without API call.

    Returns:
        Dict with complexity, reasoning, key_parameters, model,
        input_tokens, output_tokens, latency_ms.
    """
    if demo_mode:
        return _mock_classify(spec)
    return _live_classify(spec)


def _live_classify(spec):
    """Call GPT-5 Nano for real classification."""
    import openai

    client = openai.OpenAI()
    start = time.time()

    try:
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
                {"role": "user", "content": f"Customer specification:\n{spec}"},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        latency_ms = int((time.time() - start) * 1000)

        result = json.loads(response.choices[0].message.content)
        return {
            "complexity": result.get("complexity", "MEDIUM"),
            "reasoning": result.get("reasoning", "Classification complete"),
            "key_parameters": result.get("key_parameters", []),
            "model": "gpt-5-nano",
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
            "latency_ms": latency_ms,
        }
    except Exception as e:
        latency_ms = int((time.time() - start) * 1000)
        return {
            "complexity": "MEDIUM",
            "reasoning": f"Fallback classification (API error: {e})",
            "key_parameters": [],
            "model": "gpt-5-nano",
            "input_tokens": 0,
            "output_tokens": 0,
            "latency_ms": latency_ms,
            "error": str(e),
        }


def _mock_classify(spec):
    """Keyword-based mock classification for demo mode."""
    spec_lower = spec.lower()

    # Keywords indicating complex multi-component or system-level requests
    complex_keywords = [
        "terahertz", "thz", "system", "integration", "production line",
        "multi-component", "custom", "rs-232", "manufacturing",
        "quality control", "tunable",
    ]
    # Keywords indicating medium-complexity multi-parameter requests
    medium_keywords = [
        "multiline", "multi-line", "multiple", "combination", "noise",
        "rms", "super-resolution", "compact", "combiner", "tunable",
    ]

    if any(kw in spec_lower for kw in complex_keywords):
        return {
            "complexity": "COMPLEX",
            "reasoning": (
                "Multi-component setup with system integration detected. "
                "Requires deep technical analysis and creative solution development."
            ),
            "key_parameters": _extract_mock_params(spec_lower, "COMPLEX"),
            "model": "gpt-5-nano",
            "input_tokens": 847,
            "output_tokens": 95,
            "latency_ms": 320,
        }

    if any(kw in spec_lower for kw in medium_keywords):
        return {
            "complexity": "MEDIUM",
            "reasoning": (
                "Multiple simultaneous parameters and specific requirements detected. "
                "Extended matching with parameter comparison required."
            ),
            "key_parameters": _extract_mock_params(spec_lower, "MEDIUM"),
            "model": "gpt-5-nano",
            "input_tokens": 623,
            "output_tokens": 82,
            "latency_ms": 280,
        }

    return {
        "complexity": "SIMPLE",
        "reasoning": (
            "Standard wavelength with clear power specification. "
            "Direct catalog lookup sufficient."
        ),
        "key_parameters": _extract_mock_params(spec_lower, "SIMPLE"),
        "model": "gpt-5-nano",
        "input_tokens": 512,
        "output_tokens": 68,
        "latency_ms": 210,
    }


def _extract_mock_params(spec_lower, complexity):
    """Extract plausible key parameters from spec text for mock response."""
    params = []

    import re
    wavelengths = re.findall(r"(\d{3,4})\s*nm", spec_lower)
    for wl in wavelengths:
        params.append(f"{wl} nm")

    power_mw = re.findall(r"(\d+)\s*mw", spec_lower)
    for p in power_mw:
        params.append(f"{p} mW")

    power_w = re.findall(r"(\d+(?:\.\d+)?)\s*w\b", spec_lower)
    for p in power_w:
        params.append(f"{p} W")

    if "noise" in spec_lower or "rms" in spec_lower:
        params.append("Noise/RMS")

    if complexity == "COMPLEX":
        if "thz" in spec_lower or "terahertz" in spec_lower:
            params.append("THz range")
        if "integration" in spec_lower or "rs-232" in spec_lower:
            params.append("System integration")

    return params if params else ["Wavelength", "Power"]
