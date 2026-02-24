"""Proposal generator agent supporting GPT-5 Nano/Mini and Claude Sonnet 4."""

import json
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from products import search_products

PROPOSAL_SYSTEM_PROMPT = """You are a senior application engineer specializing in laser and terahertz solutions.
Based on the customer specification and matched products, create a professional proposal draft.

Respond as JSON with the following structure:
{
    "proposal_text": "Full proposal text in Markdown",
    "product_matches": [
        {"product_id": "...", "product_name": "...", "match_score": 85, "reasoning": "..."}
    ],
    "feasibility_matrix": {
        "Parameter-Name": {"status": "met|partial|not met", "note": "Explanation"}
    },
    "next_steps": ["Step 1", "Step 2"]
}

Tone: Professional, technically precise, solution-oriented.
Language: English."""


def generate_proposal(spec, model, matched_products, demo_mode=True):
    """Generate a technical proposal based on spec and matched products.

    Args:
        spec: Customer specification text.
        model: Model ID to use for generation.
        matched_products: List of product match dicts from search_products().
        demo_mode: If True, return mock data without API call.

    Returns:
        Dict with proposal_text, product_matches, feasibility_matrix,
        model, input_tokens, output_tokens, latency_ms.
    """
    if demo_mode:
        return _mock_proposal(spec, model, matched_products)
    return _live_proposal(spec, model, matched_products)


def _live_proposal(spec, model, matched_products):
    """Call the selected model for real proposal generation."""
    products_context = _build_products_context(matched_products)
    user_prompt = (
        f"Customer specification:\n{spec}\n\n"
        f"Matching products:\n{products_context}\n\n"
        "Create a professional proposal draft as JSON."
    )

    if model.startswith("claude"):
        return _call_anthropic(model, user_prompt)
    return _call_openai(model, user_prompt)


def _call_openai(model, user_prompt):
    """Call OpenAI API (GPT-5 Nano or GPT-5 Mini)."""
    import openai

    client = openai.OpenAI()
    start = time.time()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": PROPOSAL_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        latency_ms = int((time.time() - start) * 1000)
        content = response.choices[0].message.content or "{}"
        result = json.loads(content)
        usage = response.usage

        return {
            **result,
            "model": model,
            "input_tokens": usage.prompt_tokens if usage else 0,
            "output_tokens": usage.completion_tokens if usage else 0,
            "latency_ms": latency_ms,
        }
    except Exception as e:
        latency_ms = int((time.time() - start) * 1000)
        return _error_fallback(model, str(e), latency_ms)


def _call_anthropic(model, user_prompt):
    """Call Anthropic API (Claude Sonnet 4)."""
    import anthropic

    client = anthropic.Anthropic()
    start = time.time()

    try:
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            system=PROPOSAL_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        latency_ms = int((time.time() - start) * 1000)

        content_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                content_text += block.text

        try:
            result = json.loads(content_text)
        except json.JSONDecodeError:
            result = {
                "proposal_text": content_text,
                "product_matches": [],
                "feasibility_matrix": {},
                "next_steps": [],
            }

        return {
            **result,
            "model": model,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "latency_ms": latency_ms,
        }
    except Exception as e:
        latency_ms = int((time.time() - start) * 1000)
        return _error_fallback(model, str(e), latency_ms)


def _error_fallback(model, error_msg, latency_ms):
    """Return error fallback response."""
    return {
        "proposal_text": f"Error during proposal generation: {error_msg}",
        "product_matches": [],
        "feasibility_matrix": {},
        "next_steps": ["Check API configuration", "Retry"],
        "model": model,
        "input_tokens": 0,
        "output_tokens": 0,
        "latency_ms": latency_ms,
        "error": error_msg,
    }


def _build_products_context(matched_products):
    """Build a text summary of matched products for the LLM prompt."""
    if not matched_products:
        return "No direct matches found in catalog."

    lines = []
    for match in matched_products[:5]:
        product = match.get("product", match)
        name = product.get("name", "N/A")
        category = product.get("category", "N/A")
        apps = ", ".join(product.get("applications", [])[:3])
        features = ", ".join(product.get("key_features", [])[:3])
        score = match.get("score", "N/A")
        lines.append(
            f"- {name} ({category}): Match {score}% | "
            f"Applications: {apps} | Features: {features}"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Mock proposals for demo mode
# ---------------------------------------------------------------------------

MOCK_PROPOSALS = {
    "SIMPLE": {
        "proposal_text": """## Proposal: Cobolt 05-01 Series for Fluorescence Microscopy

### Customer Requirement Summary
The customer requires a compact 532 nm laser source with 100 mW output power for use in fluorescence microscopy.

### Recommended Solution
We recommend the **Cobolt 05-01 Series** (Samba model) with the following specifications:
- **Wavelength**: 532 nm (exact match)
- **Output Power**: Up to 1.5 W (100 mW easily achievable)
- **Noise (RMS)**: < 0.1% (excellent for microscopy)
- **Linewidth**: < 1 MHz
- **Technology**: HTCure\u2122 for long-term stability

### Technical Justification
The Cobolt 05-01 series is specifically designed for scientific and industrial applications. The HTCure\u2122 technology ensures a hermetically sealed, monolithic laser cavity with exceptional long-term stability of >20,000 hours.

### Customer Benefits
1. **Plug-and-Play**: No alignment required
2. **Compact Form Factor**: 125 x 70 x 45 mm, ideal for microscope integration
3. **OEM-Ready**: Standardized interfaces for system integration
4. **Spectral Purity**: > 60 dB SMSR

### Alternative
The **Cobolt 04-01 Series** (Samba) offers up to 450 mW at 532 nm in an even more compact package \u2014 ideal if an even smaller footprint is required.

### Next Steps
1. Clarify exact power range and modulation requirements
2. Provide datasheet and quotation
3. Optional: Loan unit for evaluation""",
        "product_matches": [
            {"product_id": "cobolt-05-01", "product_name": "Cobolt 05-01 Series", "match_score": 95, "reasoning": "Exact wavelength 532nm, power in range, ideal application"},
            {"product_id": "cobolt-04-01", "product_name": "Cobolt 04-01 Series", "match_score": 72, "reasoning": "532nm Samba model, more compact alternative, up to 450mW"},
        ],
        "feasibility_matrix": {
            "Wavelength 532 nm": {"status": "met", "note": "Exactly available in Cobolt 05-01 Series (Samba)"},
            "Power 100 mW": {"status": "met", "note": "Range 20-1500 mW, 100 mW easily deliverable"},
            "Fluorescence Microscopy": {"status": "met", "note": "Core application of the Cobolt 05-01 Series"},
        },
        "next_steps": [
            "Prepare datasheet and price quotation",
            "Clarify modulation requirements",
            "Offer evaluation unit",
        ],
        "model": "gpt-5-nano",
        "input_tokens": 1247,
        "output_tokens": 856,
        "latency_ms": 1850,
    },
    "MEDIUM": {
        "proposal_text": """## Proposal: Cobolt 06-01 Series + C-FLEX for Super-Resolution Imaging

### Customer Requirement Summary
The customer requires a multiline laser with 488 nm and 640 nm (each >50 mW), noise <0.5% RMS for super-resolution imaging in a compact form factor.

### Recommended Solution: C-FLEX Laser Combiner
We recommend the **C-FLEX C4 system** with two **Cobolt 06-01** laser modules:

**Configuration:**
| Line | Model | Wavelength | Power | Noise |
|------|-------|-----------|-------|-------|
| 1 | Cobolt 06-MLD | 488 nm | up to 60 mW | < 0.2% RMS |
| 2 | Cobolt 06-MLD | 638 nm | up to 180 mW | < 0.2% RMS |

### Technical Analysis
The **C-FLEX** combines up to 8 laser lines in a compact housing with a single collinear fiber output. The **Cobolt 06-01 Series** offers 25+ available wavelengths with digital modulation up to 150 MHz \u2014 ideal for super-resolution techniques like STED and STORM.

### Benefits of the 06-01 + C-FLEX Combination
1. **Fast Modulation**: DC to 150 MHz with true OFF state
2. **Flexibly Expandable**: C4 upgradable to C6 or C8
3. **32 Wavelengths Available**: Future-proof for new fluorophores
4. **Integrated Clean-up Filters**: No external filtering needed
5. **Plug-and-Play**: USB/RS-232 control

### Alternative: Individual Cobolt 06-01 Modules
If a combiner is not required, laser modules can also be delivered as individual components with separate fiber coupling.

### Next Steps
1. Configuration consultation: C4 with 488/638 nm or extended
2. Detailed quotation with delivery times
3. Application consultation for super-resolution setup""",
        "product_matches": [
            {"product_id": "c-flex", "product_name": "C-FLEX Laser Combiner", "match_score": 92, "reasoning": "Multi-wavelength combiner, compact, up to 8 lines, ideal for super-resolution"},
            {"product_id": "cobolt-06-01", "product_name": "Cobolt 06-01 Series", "match_score": 88, "reasoning": "488nm and 638nm available, fast modulation, <0.2% noise"},
            {"product_id": "cobolt-05-01", "product_name": "Cobolt 05-01 Series", "match_score": 45, "reasoning": "Single-frequency 488nm possible, but no modulation"},
        ],
        "feasibility_matrix": {
            "Wavelength 488 nm": {"status": "met", "note": "Cobolt 06-01 MLD at 488nm, up to 60 mW"},
            "Wavelength 640 nm": {"status": "met", "note": "Cobolt 06-01 MLD at 638nm, up to 180 mW"},
            "Power >50 mW": {"status": "met", "note": "488nm: 60mW, 638nm: 180mW \u2014 both above requirement"},
            "Noise <0.5% RMS": {"status": "met", "note": "06-01 offers <0.2% RMS \u2014 significantly better than required"},
            "Compact Form Factor": {"status": "met", "note": "C-FLEX C4 combines everything in one compact housing"},
            "Super-Resolution": {"status": "met", "note": "06-01 modulation up to 150 MHz ideal for STED/STORM"},
        },
        "next_steps": [
            "Configuration consultation: C4 with 2 or 4 lines",
            "Prepare detailed quotation",
            "Application consultation for super-resolution setup",
        ],
        "model": "gpt-5-mini",
        "input_tokens": 1856,
        "output_tokens": 1243,
        "latency_ms": 3200,
    },
    "COMPLEX": {
        "proposal_text": """## Proposal: Integrated Laser and THz System for AR Holography Production

### Customer Requirement Summary
The customer is planning an AR holography production line with the following requirements:
1. **Primary Source**: 532 nm at 2W for master holograms
2. **Tunable Source**: 450-650 nm for color calibration
3. **Control**: RS-232 integration into existing production line
4. **Quality Control**: THz-based inspection of finished holograms

### Recommended System Solution

#### Component 1: Ampheia Fiber Laser (Master Hologram Laser)
- **Wavelength**: 532 nm
- **Power**: Up to 5 W (meets the 2W requirement with headroom)
- **Characteristics**: Single-frequency, TEM00, ultra-low RIN
- **Rationale**: The Ampheia at 532 nm delivers 5W with outstanding pointing stability, ideal for high-precision holographic recording.

#### Component 2: C-WAVE (Tunable Color Calibration)
- **Wavelength Range**: 450-650 nm (VIS variant, exact match)
- **Tuning**: Continuous, mode-hop-free
- **Linewidth**: < 1 MHz (with AbsoluteLambda: \u00b12 MHz stability)
- **Rationale**: The only source in the portfolio with continuous tunability across the entire visible range. Enables precise RGB color calibration.

#### Component 3: T-SPECTRALYZER (Inline Quality Control)
- **Frequency Range**: 0.1-4 THz
- **Dynamic Range**: > 70 dB at 0.5 THz
- **Measurement Geometry**: Reflection (R) for inline inspection
- **Rationale**: The T-SPECTRALYZER enables non-destructive layer thickness measurement in 2-8 seconds. Fiber-coupled modules (F) allow flexible positioning in the production line.

### System Integration
All components support standardized interfaces (RS-232, USB, LAN). A supervisory control system can synchronize laser parameters, THz measurements, and production processes.

**Architecture Proposal:**
```
Production PLC / Automation Workflow
  \u251c\u2500\u2500 RS-232 \u2192 Ampheia (Master exposure)
  \u251c\u2500\u2500 LAN   \u2192 C-WAVE (Color calibration)
  \u2514\u2500\u2500 LAN   \u2192 T-SPECTRALYZER (QC inspection)
```

### Feasibility Assessment
This system combines three product lines (Laser, Tunable, THz) into an integrated solution. Technical feasibility is confirmed, but requires a custom integration project with the application engineering team.

### Next Steps
1. Kick-off meeting with application engineering
2. Detailed system specification and interface definition
3. Proof-of-concept on individual components
4. System integration quotation with project plan
5. Pilot installation and validation""",
        "product_matches": [
            {"product_id": "ampheia", "product_name": "Ampheia Fiber Laser Systems", "match_score": 90, "reasoning": "532nm at 5W available, meets 2W requirement with headroom"},
            {"product_id": "c-wave", "product_name": "C-WAVE Series", "match_score": 88, "reasoning": "450-650nm tunable, exact match for color calibration"},
            {"product_id": "t-spectralyzer", "product_name": "T-SPECTRALYZER", "match_score": 85, "reasoning": "0.1-4 THz, >70dB dynamic range, inline-capable for QC"},
            {"product_id": "cobolt-08-01", "product_name": "Cobolt 08-01 Series", "match_score": 65, "reasoning": "532nm 08-DPL with >80dB purity, but power below 2W"},
        ],
        "feasibility_matrix": {
            "532 nm / 2W": {"status": "met", "note": "Ampheia Fiber Laser delivers up to 5W at 532nm"},
            "Tunable 450-650 nm": {"status": "met", "note": "C-WAVE VIS covers exactly this range"},
            "RS-232 Control": {"status": "partial", "note": "RS-232/USB/LAN available, system integration required"},
            "THz Quality Control": {"status": "met", "note": "T-SPECTRALYZER with fiber modules for inline QC"},
            "Production Line Integration": {"status": "partial", "note": "Feasible, requires custom engineering project"},
            "Holography Application": {"status": "met", "note": "Ampheia + C-WAVE are optimized for holography"},
        },
        "next_steps": [
            "Kick-off meeting with application engineering",
            "Create detailed system specification",
            "Plan proof-of-concept",
            "Integration quotation with project plan",
        ],
        "model": "claude-sonnet-4-20250514",
        "input_tokens": 2834,
        "output_tokens": 1876,
        "latency_ms": 5400,
    },
}


def _mock_proposal(spec, model, matched_products):
    """Return a pre-written mock proposal based on complexity."""
    spec_lower = spec.lower()

    complex_keywords = [
        "terahertz", "thz", "system", "integration", "production line",
        "manufacturing", "tunable", "rs-232",
    ]
    medium_keywords = [
        "multiline", "multi-line", "multiple", "noise", "rms",
        "super-resolution", "compact", "combiner",
    ]

    if any(kw in spec_lower for kw in complex_keywords):
        mock = MOCK_PROPOSALS["COMPLEX"]
    elif any(kw in spec_lower for kw in medium_keywords):
        mock = MOCK_PROPOSALS["MEDIUM"]
    else:
        mock = MOCK_PROPOSALS["SIMPLE"]

    return {**mock, "model": model}
