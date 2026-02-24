# Architecture

## Overview

The Spec-to-Proposal Router is an AI-powered pipeline that converts customer specifications into technical proposals. The core innovation is **intelligent model routing** — a cheap classifier analyzes each request and delegates it to the cost-optimal LLM based on complexity.

---

## System Architecture

```
Customer Spec ──> [Classifier: GPT-5 Nano] ──> Complexity?
                                                    |
                ┌───────────────────────────────────┼───────────────────────────────┐
                |                                   |                               |
             SIMPLE                              MEDIUM                          COMPLEX
                |                                   |                               |
        [GPT-5 Nano]                        [GPT-5 Mini]                  [Claude Sonnet 4]
          $0.05/1M                            $0.25/1M                       $3.00/1M
                |                                   |                               |
                └───────────────────────────────────┼───────────────────────────────┘
                                                    |
                                         [Proposal Draft]
```

**Result:** Up to 97% cost savings compared to routing every request through the most expensive model.

---

## Component Details

### Classifier (`agents/classifier.py`)

- **Model:** GPT-5 Nano ($0.05/1M input tokens)
- **Purpose:** Analyze customer spec complexity
- **Output:** `SIMPLE | MEDIUM | COMPLEX` + reasoning + key parameters
- **Demo mode:** Keyword-based heuristic (no API call)

**Classification heuristics (demo mode):**
- **COMPLEX:** THz, system integration, RS-232, production line, tunable
- **MEDIUM:** Multiline, noise/RMS, super-resolution, combiner, compact
- **SIMPLE:** Standard wavelength + clear power specification

### Router (`agents/router.py`)

Maps complexity to the optimal model:

```python
ROUTING_TABLE = {
    "SIMPLE":  "gpt-5-nano",               # $0.05/1M
    "MEDIUM":  "gpt-5-mini",               # $0.25/1M
    "COMPLEX": "claude-sonnet-4-20250514",  # $3.00/1M
}
```

### Proposal Generator (`agents/proposal.py`)

- **Input:** Customer spec + matched products
- **Output:** JSON with proposal text, product matches, feasibility matrix, next steps
- **Live mode:** Calls OpenAI or Anthropic API based on routed model
- **Demo mode:** Returns pre-written proposals for each complexity tier

### Product Search (`products.py`)

Keyword-based scoring engine across 16 photonics products. Matching dimensions:

| Dimension | Score Weight |
|-----------|-------------|
| Product name match | +35 |
| Named model match | +30 |
| THz frequency match | +30 |
| Wavelength exact match | +25 |
| Tunable keyword match | +25 |
| Femtosecond keyword match | +25 |
| Power range match | +20 |
| Wavelength range match | +20 |
| Application match | +20 |
| Category match | +15 |
| Keyword match | +10 |
| Feature word match | +4 |

### Cost Calculator (`utils/cost_calculator.py`)

Computes cost across all 5 models for the same token count, calculates savings vs. the most expensive model.

### PDF Export (`utils/export.py`)

Generates professional PDF proposals using fpdf2 with:
- Cross-platform font support (Windows, Linux, macOS)
- Unicode fallback for systems without TrueType fonts
- Structured sections: spec, routing, products, feasibility, proposal, token analysis

---

## Token Economy

### Pricing Table (February 2026)

| Model | Input/1M | Output/1M | Use Case |
|-------|----------|-----------|----------|
| GPT-5 Nano | $0.05 | $0.40 | Classifier + simple proposals |
| GPT-5 Mini | $0.25 | $2.00 | Medium complexity |
| Claude Sonnet 4 | $3.00 | $15.00 | Complex system proposals |
| GPT-5 | $1.25 | $10.00 | Reference (comparison only) |
| GPT-5.2 Thinking | $1.75 | $14.00 | Flagship (comparison only) |

### Cost Examples

| Scenario | Classifier | Proposal Model | Tokens | Cost | Savings vs. Flagship |
|----------|-----------|---------------|--------|------|---------------------|
| SIMPLE | GPT-5 Nano | GPT-5 Nano | ~2,700 | $0.0005 | **97.6%** |
| MEDIUM | GPT-5 Nano | GPT-5 Mini | ~3,800 | $0.0030 | **89.0%** |
| COMPLEX | GPT-5 Nano | Claude Sonnet 4 | ~5,700 | $0.0191 | **30.2%** |

---

## Product Catalog

### Lasers (11 products)

| Product | Category | Wavelength Range |
|---------|----------|-----------------|
| Cobolt 04-01 Series | Single Frequency CW DPSS | 457-1064 nm |
| Cobolt 05-01 Series | High-Power Single Frequency | 320-1064 nm |
| Cobolt 06-01 Series | Modulated CW Diode | 375-975 nm (25+ lines) |
| Cobolt 08-01 Series | Narrow Linewidth | 405-1064 nm |
| Cobolt Tor Series | Q-Switched Nanosecond | 355-1064 nm |
| C-WAVE Series | Tunable CW OPO | 450-3400 nm |
| Cobolt Qu-T Series | Tunable & Lockable | 530-850 nm |
| Cobolt Odin Series | Mid-IR Tunable | 3000-4600 nm |
| C-FLEX Combiner | Multi-Wavelength | Up to 8 lines |
| VALO Series | Ultrafast Fiber | 1000-1100 nm |
| Ampheia Series | High-Power CW Fiber | 488-1064 nm |

### Terahertz (5 products)

| Product | Category | Range |
|---------|----------|-------|
| T-SPECTRALYZER | THz Spectrometer | 0.1-4 THz |
| T-SPECTRALYZER F | Compact Fiber-Based | 0.1-2.5 THz |
| T-COGNITION | Security Spectrometer | 0.1-4 THz |
| T-SENSE | Mail & Package Imager | 3,000 envelopes/hr |
| T-SENSE FMI | Industrial Imager | QC / NDT |

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | Streamlit 1.40+ | Single-page app with custom CSS |
| Classifier | GPT-5 Nano (OpenAI) | Complexity analysis |
| Medium Routing | GPT-5 Mini (OpenAI) | Mid-tier proposals |
| Complex Routing | Claude Sonnet 4 (Anthropic) | Complex system proposals |
| Charts | Plotly | Token economy visualization |
| PDF Export | fpdf2 | Proposal download |
| PDF Parsing | PyMuPDF (fitz) | Customer PDF upload |
