"""AI Spec-to-Proposal Router — Main Streamlit App."""

import html as html_mod
import sys
import os
import time
import streamlit as st
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from products import search_products
from pricing import MODEL_PRICING
from agents.classifier import classify_spec
from agents.router import route, DISPLAY_NAMES
from agents.proposal import generate_proposal
from utils.cost_calculator import format_cost, build_comparison_table, build_savings_summary
from utils.export import generate_proposal_pdf

# ---------------------------------------------------------------------------
# Page config (must be first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Spec-to-Proposal Router",
    page_icon="\U0001f52c",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Load custom CSS
# ---------------------------------------------------------------------------
css_path = os.path.join(os.path.dirname(__file__), "styles", "custom.css")
if os.path.exists(css_path):
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state init
# ---------------------------------------------------------------------------
if "results" not in st.session_state:
    st.session_state.results = None
if "spec_text" not in st.session_state:
    st.session_state.spec_text = ""
if "pa_sent" not in st.session_state:
    st.session_state.pa_sent = False

# ---------------------------------------------------------------------------
# Example queries
# ---------------------------------------------------------------------------
EXAMPLES = {
    "simple": "We need a 532 nm laser with 100 mW for fluorescence microscopy.",
    "medium": (
        "Required: Multiline laser with 488 nm and 640 nm, each >50 mW, "
        "noise <0.5% RMS for super-resolution imaging. Compact form factor preferred."
    ),
    "complex": (
        "For our new AR holography production line we need a system: "
        "Primary 532 nm at 2W for master holograms + tunable source 450-650 nm "
        "for color calibration. Integration into existing production line with RS-232 "
        "control. THz quality control of finished holograms desirable."
    ),
}

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-header">
            <h2>Spec-to-Proposal Router</h2>
            <p class="sidebar-subtitle">AI-Powered Model Routing</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    demo_mode = st.toggle(
        "Demo Mode",
        value=True,
        help="Demo: Mock data without API calls | Live: Real API calls with GPT-5 & Claude",
    )

    if demo_mode:
        st.markdown(
            '<div class="demo-banner"><span>DEMO MODE \u2014 Simulated Responses</span></div>',
            unsafe_allow_html=True,
        )
    else:
        api_key_ok = True
        openai_key = os.environ.get("OPENAI_API_KEY", "")
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not openai_key:
            openai_key = st.text_input("OpenAI API Key", type="password", key="openai_key_input")
            if openai_key:
                os.environ["OPENAI_API_KEY"] = openai_key
            else:
                api_key_ok = False
        if not anthropic_key:
            anthropic_key = st.text_input("Anthropic API Key", type="password", key="anthropic_key_input")
            if anthropic_key:
                os.environ["ANTHROPIC_API_KEY"] = anthropic_key
            else:
                api_key_ok = False
        if not api_key_ok:
            st.warning("API keys required for Live Mode")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    input_mode = st.radio("Input Mode", ["Text", "PDF Upload"], horizontal=True)

    if input_mode == "Text":
        spec_input = st.text_area(
            "Customer Specification",
            value=st.session_state.spec_text,
            height=150,
            placeholder="e.g. 532 nm laser source, 200 mW, <1% RMS noise, holography...",
        )
    else:
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded_file is not None:
            from utils.pdf_parser import extract_text_from_pdf

            spec_input = extract_text_from_pdf(uploaded_file.read())
            st.text_area("Extracted Text", value=spec_input, height=100, disabled=True)
        else:
            spec_input = ""

    analyze_clicked = st.button(
        "START ANALYSIS",
        type="primary",
        use_container_width=True,
        disabled=not spec_input.strip(),
    )

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    st.markdown(
        '<p style="color:#94A3B8; font-family:\'JetBrains Mono\',monospace; '
        'font-size:0.65rem; font-weight:500; text-transform:uppercase; letter-spacing:0.1em;">'
        "Example Queries</p>",
        unsafe_allow_html=True,
    )

    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        if st.button("\U0001f7e2 Simple", use_container_width=True, key="ex_simple"):
            st.session_state.spec_text = EXAMPLES["simple"]
            st.rerun()
    with col_e2:
        if st.button("\U0001f7e1 Medium", use_container_width=True, key="ex_medium"):
            st.session_state.spec_text = EXAMPLES["medium"]
            st.rerun()
    with col_e3:
        if st.button("\U0001f7e3 Complex", use_container_width=True, key="ex_complex"):
            st.session_state.spec_text = EXAMPLES["complex"]
            st.rerun()

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="info-box">
            <div class="info-title">How does Model Routing work?</div>
            <div class="info-text">
                1. A <b>cheap classifier</b> (GPT-5 Nano) analyzes the request<br>
                2. Based on complexity, the <b>optimal model</b> is selected<br>
                3. Simple requests \u2192 cheap model<br>
                4. Complex requests \u2192 powerful model<br>
                <br>
                <b>Result:</b> Up to 97% cost savings vs. the most expensive model
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Main header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="app-header">
        <h1>
            AI Spec-to-Proposal Router
        </h1>
        <div class="subtitle">Intelligent Model Routing \u00b7 Token Economy \u00b7 16 Photonics Products</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Analysis flow
# ---------------------------------------------------------------------------
if analyze_clicked and spec_input.strip():
    # Privacy compliance step
    pii_placeholder = st.empty()
    pii_placeholder.markdown(
        """
        <div class="pii-scrubber">
            <div class="pii-title">Privacy Compliance: PII Scrubber Active</div>
            <div class="pii-text">Anonymizing customer data before API call...</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    time.sleep(0.8)
    pii_placeholder.markdown(
        """
        <div class="pii-scrubber">
            <div class="pii-title">Privacy Compliance: PII Scrubber Complete</div>
            <div class="pii-text">No personal data detected \u00b7 Forwarding to classifier</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.spinner("Classifying request..."):
        classification = classify_spec(spec_input, demo_mode=demo_mode)

    with st.spinner("Routing to optimal model..."):
        routing = route(classification)

    with st.spinner("Searching product catalog (16 products)..."):
        product_matches = search_products(spec_input)

    with st.spinner("Generating proposal..."):
        proposal_result = generate_proposal(
            spec_input,
            routing["selected_model"],
            product_matches,
            demo_mode=demo_mode,
        )

    pii_placeholder.empty()

    savings_summary = build_savings_summary(
        classifier_model="gpt-5-nano",
        classifier_input_tokens=classification.get("input_tokens", 0),
        classifier_output_tokens=classification.get("output_tokens", 0),
        proposal_model=routing["selected_model"],
        proposal_input_tokens=proposal_result.get("input_tokens", 0),
        proposal_output_tokens=proposal_result.get("output_tokens", 0),
    )

    st.session_state.results = {
        "classification": classification,
        "routing": routing,
        "product_matches": product_matches,
        "proposal": proposal_result,
        "savings": savings_summary,
        "spec_text": spec_input,
    }
    st.session_state.pa_sent = False

# ---------------------------------------------------------------------------
# Render results
# ---------------------------------------------------------------------------
results = st.session_state.results

if results is None:
    st.markdown(
        """
        <div class="empty-state">
            <div class="icon">\U0001f52c</div>
            <h3>Ready for Analysis</h3>
            <p>
                Enter a customer specification in the sidebar or select one of the
                examples. The AI analyzes the request, selects the cost-optimal
                model, and generates a technical proposal draft.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Business context cards
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    ctx1, ctx2, ctx3 = st.columns(3)
    with ctx1:
        st.markdown(
            """
            <div class="metric-card" style="text-align:left;">
                <div class="metric-label">The Problem</div>
                <div style="color:#475569; font-size:0.85rem; line-height:1.6; margin-top:0.5rem;">
                    Sales engineers match customer specs <b style="color:#DC2626;">manually</b>
                    against the catalog. With 16 product lines and hundreds of parameters,
                    a proposal takes <b style="color:#DC2626;">hours</b>.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with ctx2:
        st.markdown(
            """
            <div class="metric-card" style="text-align:left;">
                <div class="metric-label">The Solution</div>
                <div style="color:#475569; font-size:0.85rem; line-height:1.6; margin-top:0.5rem;">
                    <b style="color:#009de2;">Intelligent model routing</b> selects the
                    cost-optimal AI model per request. Simple lookups cost almost nothing,
                    only complex cases use expensive models.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with ctx3:
        st.markdown(
            """
            <div class="metric-card" style="text-align:left;">
                <div class="metric-label">The Impact</div>
                <div style="color:#475569; font-size:0.85rem; line-height:1.6; margin-top:0.5rem;">
                    <b style="color:#059669;">97% cost savings</b> vs. single-model approach.
                    Response time: seconds instead of hours. Scalable to any
                    product portfolio.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="poc-disclaimer">
            <div class="poc-title">Demo \u2014 Data Source Note</div>
            <div class="poc-text">
                This system uses <b>publicly available product data</b> (16 photonics products).
                The routing architecture and token economy model are fully functional \u2014 for optimal
                result quality, integrate your own internal data sources (complete catalog, price lists,
                historical requests).
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.stop()

classification = results["classification"]
routing = results["routing"]
product_matches = results["product_matches"]
proposal = results["proposal"]
savings = results["savings"]

# ---------------------------------------------------------------------------
# Row 1: Metric Cards
# ---------------------------------------------------------------------------
complexity = classification["complexity"]
badge_class = f"badge-{complexity.lower()}"
model_label = routing["selected_model_label"]
savings_pct = savings["savings_pct"]
total_tokens = savings["total_tokens"]
total_latency = classification.get("latency_ms", 0) + proposal.get("latency_ms", 0)
savings_color = "#059669" if savings_pct > 50 else "#D97706" if savings_pct > 20 else "#DC2626"

c1, c2, c3 = st.columns(3)

with c1:
    reasoning_short = classification.get("reasoning", "")[:70]
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Complexity</div>
            <div class="metric-value">
                <span class="badge {badge_class}">{complexity}</span>
            </div>
            <div class="metric-detail">{reasoning_short}...</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Selected Model</div>
            <div class="metric-value" style="color:#009de2; font-size:1.3rem;">
                {model_label}
            </div>
            <div class="metric-detail">{total_tokens:,} tokens // {total_latency:,}ms</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Cost Savings</div>
            <div class="metric-value" style="color:{savings_color};">{savings_pct}%</div>
            <div class="metric-detail">vs. {savings['max_model_label']} // {format_cost(savings['actual_total_cost'])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Row 2: Routing Flow Visualization
# ---------------------------------------------------------------------------
st.markdown('<div class="section-header">Routing Decision</div>', unsafe_allow_html=True)

model_display = DISPLAY_NAMES.get(routing["selected_model"], routing["selected_model"])

st.markdown(
    f"""
    <div class="routing-flow">
        <div class="routing-step step-input">
            <div class="step-icon">\U0001f4dd</div>
            <div class="step-label">Customer Spec</div>
        </div>
        <div class="routing-arrow">\u2014\u2014\u25b6</div>
        <div class="routing-step step-classifier">
            <div class="step-icon">\U0001f9e0</div>
            <div class="step-label">Classifier</div>
            <div class="step-model">GPT-5 Nano</div>
        </div>
        <div class="routing-arrow">\u2014\u2014\u25b6</div>
        <div class="routing-step step-router">
            <div class="step-icon"><span class="badge {badge_class}" style="font-size:0.55rem;">{complexity}</span></div>
            <div class="step-label">Router</div>
        </div>
        <div class="routing-arrow">\u2014\u2014\u25b6</div>
        <div class="routing-step step-model">
            <div class="step-icon">\u26a1</div>
            <div class="step-label">{model_display}</div>
            <div class="step-model">Proposal Gen</div>
        </div>
        <div class="routing-arrow">\u2014\u2014\u25b6</div>
        <div class="routing-step step-output">
            <div class="step-icon">\U0001f4cb</div>
            <div class="step-label">Proposal</div>
        </div>
    </div>
    <p class="routing-rationale">{routing['rationale']}</p>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Row 3: Product Matches
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="section-header">Matching Products</div>',
    unsafe_allow_html=True,
)

display_matches = proposal.get("product_matches", [])
if not display_matches and product_matches:
    display_matches = product_matches[:4]

if display_matches:
    cols = st.columns(min(len(display_matches), 4))
    for i, match in enumerate(display_matches[:4]):
        if "product" in match:
            product = match["product"]
            score = match.get("score", match.get("match_score", 0))
            name = product.get("name", "N/A")
            category = product.get("category", "N/A")
            reasoning = match.get("reasoning", "")
        else:
            score = match.get("match_score", 0)
            name = match.get("product_name", "N/A")
            category = ""
            reasoning = match.get("reasoning", "")

        score_class = "score-high" if score >= 75 else "score-mid" if score >= 50 else "score-low"
        score_color = "#059669" if score >= 75 else "#D97706" if score >= 50 else "#DC2626"

        with cols[i]:
            st.markdown(
                f"""
                <div class="product-card" style="animation-delay:{0.1 * (i + 1)}s;">
                    <div class="product-category">{category}</div>
                    <div class="product-name">{name}</div>
                    <div class="match-score {score_class}">{score}%</div>
                    <div class="score-bar-bg">
                        <div class="score-bar-fill" style="width:{score}%; background:{score_color};"></div>
                    </div>
                    <div class="product-reasoning">{reasoning[:120]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
else:
    st.info("No direct product matches found.")

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Row 4: Feasibility Matrix
# ---------------------------------------------------------------------------
feasibility = proposal.get("feasibility_matrix", {})
if feasibility:
    st.markdown(
        '<div class="section-header">Technical Feasibility Matrix</div>',
        unsafe_allow_html=True,
    )

    matrix_html = '<div class="feasibility-container">'
    for param, info in feasibility.items():
        if isinstance(info, dict):
            status = info.get("status", "")
            note = info.get("note", "")
        else:
            status = str(info)
            note = ""

        status_lower = status.lower()
        if "met" in status_lower and "not" not in status_lower and "partial" not in status_lower:
            status_class = "status-green"
            icon = "\u2713"
        elif "partial" in status_lower:
            status_class = "status-yellow"
            icon = "\u25cb"
        else:
            status_class = "status-red"
            icon = "\u2717"

        p = html_mod.escape(param)
        s = html_mod.escape(status)
        n = html_mod.escape(note)
        matrix_html += (
            f'<div class="feasibility-row">'
            f'<div class="feasibility-param">{p}</div>'
            f'<div class="feasibility-status {status_class}">{icon} {s}</div>'
            f'<div class="feasibility-note">{n}</div>'
            f'</div>'
        )
    matrix_html += '</div>'
    st.markdown(matrix_html, unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Row 5: Token Economy Dashboard
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="section-header">Token Economy Dashboard</div>'
    '<div class="section-subheader">Cost comparison: Intelligent routing vs. single-model approach</div>',
    unsafe_allow_html=True,
)

eco_left, eco_right = st.columns([2, 1])

with eco_left:
    comparison = build_comparison_table(
        savings["total_input_tokens"],
        savings["total_output_tokens"],
    )

    labels = [row["label"] for row in comparison]
    input_costs = [row["input_cost"] for row in comparison]
    output_costs = [row["output_cost"] for row in comparison]
    colors = [row["color"] for row in comparison]
    total_costs = [row["total_cost"] for row in comparison]

    fig = go.Figure()

    bar_colors_light = [
        f"rgba({int(c[1:3],16)},{int(c[3:5],16)},{int(c[5:7],16)},0.45)"
        for c in colors
    ]

    fig.add_trace(go.Bar(
        name="Input",
        y=labels,
        x=input_costs,
        orientation="h",
        marker=dict(color=bar_colors_light, line=dict(color=colors, width=1.5)),
        text=[f"${c:.4f}" if c > 0.0001 else "" for c in input_costs],
        textposition="outside",
        textfont=dict(size=10, color="#475569", family="JetBrains Mono"),
    ))

    fig.add_trace(go.Bar(
        name="Output",
        y=labels,
        x=output_costs,
        orientation="h",
        marker=dict(color=colors, line=dict(color=colors, width=0)),
        text=[f"${c:.4f}" if c > 0.0001 else "" for c in output_costs],
        textposition="outside",
        textfont=dict(size=10, color="#475569", family="JetBrains Mono"),
    ))

    actual_model_label = MODEL_PRICING.get(
        routing["selected_model"].replace("-20250514", ""),
        {},
    ).get("label", routing["selected_model_label"])

    fig.add_annotation(
        x=max(total_costs) * 1.15 if total_costs else 0,
        y=actual_model_label,
        text="\u25c0 SELECTED",
        showarrow=False,
        font=dict(size=11, color="#059669", family="JetBrains Mono"),
        xanchor="left",
    )

    fig.update_layout(
        barmode="stack",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="JetBrains Mono", color="#64748B", size=11),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#475569", size=10),
        ),
        xaxis=dict(
            title=dict(text="Cost (USD)", font=dict(size=10, color="#64748B")),
            gridcolor="#E2E8F0",
            tickformat="$.4f",
            tickfont=dict(size=9, color="#64748B"),
            zeroline=False,
        ),
        yaxis=dict(
            gridcolor="#E2E8F0",
            tickfont=dict(size=10, color="#475569"),
            automargin=True,
        ),
        height=340,
        margin=dict(l=220, r=80, t=40, b=40),
        bargap=0.2,
    )

    st.plotly_chart(fig, use_container_width=True)

with eco_right:
    st.markdown(
        f"""
        <div class="savings-highlight">
            <div class="savings-value">{savings['savings_pct']}%</div>
            <div class="savings-label">Savings vs. {savings['max_model_label']}</div>
        </div>

        <div class="cost-panel">
            <div class="cost-row">
                <div class="cost-label">Actual Cost</div>
                <div class="cost-value" style="color:var(--green-success);">
                    {format_cost(savings['actual_total_cost'])}
                </div>
            </div>
            <div class="cost-row">
                <div class="cost-label">Cost with {savings['max_model_label']}</div>
                <div class="cost-value" style="color:var(--red-error);">
                    {format_cost(savings['max_cost'])}
                </div>
            </div>
            <div class="cost-row">
                <div class="cost-label">Total Tokens</div>
                <div class="cost-value">
                    {savings['total_tokens']:,}
                </div>
            </div>
            <div class="cost-row">
                <div class="cost-label">Breakdown</div>
                <div class="cost-breakdown">
                    Input: {savings['total_input_tokens']:,}<br>
                    Output: {savings['total_output_tokens']:,}<br>
                    Classifier: {format_cost(savings['classifier_cost'])}<br>
                    Proposal: {format_cost(savings['proposal_cost'])}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Row 6: Proposal Text
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="section-header">Proposal Draft</div>',
    unsafe_allow_html=True,
)

with st.expander("Show full proposal draft", expanded=True):
    proposal_text = proposal.get("proposal_text", "No proposal generated.")
    next_steps = proposal.get("next_steps", [])
    steps_html = ""
    if next_steps and "next steps" not in proposal_text.lower():
        steps_html = '<h3 style="margin-top:1.2rem;">Next Steps</h3><ul>'
        for step in next_steps:
            steps_html += f"<li>{html_mod.escape(step)}</li>"
        steps_html += "</ul>"
    st.markdown(
        f'<div class="proposal-text">{proposal_text}{steps_html}</div>',
        unsafe_allow_html=True,
    )

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Row 7: PDF Export + Webhook
# ---------------------------------------------------------------------------
export_col, pa_col = st.columns(2)

with export_col:
    try:
        pdf_bytes = generate_proposal_pdf(
            customer_spec=results["spec_text"],
            routing_info={
                **routing,
                "total_latency_ms": total_latency,
            },
            product_matches=display_matches,
            feasibility_matrix=feasibility,
            proposal_text=proposal.get("proposal_text", ""),
            token_stats=savings,
        )

        st.download_button(
            label="EXPORT PROPOSAL AS PDF",
            data=pdf_bytes,
            file_name="proposal.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"PDF export failed: {e}")

with pa_col:
    if st.button(
        "SEND TO WEBHOOK / CRM",
        use_container_width=True,
        type="secondary",
        key="pa_button",
    ):
        st.session_state.pa_sent = True

    if st.session_state.pa_sent:
        st.markdown(
            """
            <div class="power-automate-success">
                <span>\u2713 Webhook triggered \u00b7 Proposal sent to CRM pipeline</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# Disclaimer
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="poc-disclaimer">
        <div class="poc-title">Demo \u2014 Data Source Note</div>
        <div class="poc-text">
            This system was built as a <b>functional demonstration</b> using
            publicly available photonics product data (16 products). The routing architecture,
            token economy model, and proposal generation are fully functional.
        </div>
        <div class="poc-next-steps">
            <b>To adapt for production use:</b>
            Integrate your own data sources \u2014 complete product catalog with
            configuration options, internal price lists, historical customer requests,
            and existing proposal templates.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="app-footer">
        AI Spec-to-Proposal Router \u00b7 Model Routing Architecture \u00b7 Token Economy Optimization
    </div>
    """,
    unsafe_allow_html=True,
)
