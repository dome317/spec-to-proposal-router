"""PDF export for proposal documents using fpdf2."""

import datetime
import re
from fpdf import FPDF
from fpdf.enums import XPos, YPos


def _strip_markdown(text):
    """Remove markdown formatting for plain-text PDF rendering."""
    lines = text.split("\n")
    cleaned = []
    in_code_block = False
    for line in lines:
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            cleaned.append(line)
            continue
        line = re.sub(r"^#{1,4}\s+", "", line)
        line = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
        line = re.sub(r"\*(.+?)\*", r"\1", line)
        line = re.sub(r"`(.+?)`", r"\1", line)
        if re.match(r"^\s*\|.*\|.*\|", line):
            if re.match(r"^\s*\|[-\s|:]+\|$", line):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            line = "  " + "  |  ".join(cells)
        cleaned.append(line)
    return "\n".join(cleaned)


_FONT_PATHS = [
    # Windows
    ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
    # Linux (Streamlit Cloud / Ubuntu)
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
     "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
    # macOS
    ("/System/Library/Fonts/Helvetica.ttc", None),
]


def _sanitize_text(text):
    """Replace Unicode chars that Helvetica cannot render."""
    replacements = {
        "\u2013": "-", "\u2014": "-", "\u2015": "-",
        "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2026": "...", "\u2022": "-",
        "\u00b7": "-", "\u2192": "->",
        "\u25c0": "<", "\u25b6": ">",
        "\u2713": "OK", "\u2717": "X", "\u25cb": "~",
    }
    for char, repl in replacements.items():
        text = text.replace(char, repl)
    return text


class ProposalPDF(FPDF):
    """Custom PDF class with professional branding."""

    def __init__(self):
        super().__init__()
        self._font_loaded = False
        for regular, bold in _FONT_PATHS:
            try:
                import os
                if not os.path.exists(regular):
                    continue
                self.add_font("UniFont", fname=regular)
                if bold and os.path.exists(bold):
                    self.add_font("UniFont", style="B", fname=bold)
                self._font_loaded = True
                break
            except Exception:
                continue

    def _set_font_safe(self, size=11, style=""):
        if self._font_loaded:
            self.set_font("UniFont", style=style, size=size)
        else:
            self.set_font("Helvetica", style=style, size=size)

    def _safe_text(self, text):
        """Ensure text is safe for the current font."""
        if self._font_loaded:
            return text
        return _sanitize_text(text)

    def _cell_ln(self, w, h, txt, **kwargs):
        """cell() with automatic line break using new fpdf2 API."""
        self.cell(w, h, txt, new_x=XPos.LMARGIN, new_y=YPos.NEXT, **kwargs)

    def header(self):
        self._set_font_safe(size=10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "Spec-to-Proposal Router | AI-Generated Proposal Draft", align="L")
        self.ln(10)
        self.set_draw_color(0, 157, 226)
        self.set_line_width(0.4)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-30)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)
        self._set_font_safe(size=7)
        self.set_text_color(150, 150, 150)
        disclaimer = (
            "AI-generated draft - not a binding statement. "
            "Created with privacy-compliant AI processing."
        )
        self.multi_cell(0, 3.5, disclaimer, align="C")
        self.ln(1)
        self._set_font_safe(size=7)
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.cell(0, 3.5, f"Generated on {date_str} | Page {self.page_no()}/{{nb}}", align="C")


def generate_proposal_pdf(
    customer_spec,
    routing_info,
    product_matches,
    feasibility_matrix,
    proposal_text,
    token_stats,
):
    """Generate a professional PDF proposal document.

    Returns:
        PDF file as bytes.
    """
    pdf = ProposalPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=35)

    pdf._set_font_safe(size=20, style="B")
    pdf.set_text_color(10, 22, 40)
    pdf._cell_ln(0, 12, "Spec-to-Proposal Router")

    pdf._set_font_safe(size=14, style="B")
    pdf.set_text_color(0, 157, 226)
    pdf._cell_ln(0, 10, "AI-Generated Proposal Draft")
    pdf.ln(5)

    pdf._set_font_safe(size=11, style="B")
    pdf.set_text_color(10, 22, 40)
    pdf._cell_ln(0, 8, "1. Customer Specification")
    pdf._set_font_safe(size=10)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 5.5, pdf._safe_text(customer_spec[:1000]))
    pdf.ln(5)

    pdf._set_font_safe(size=11, style="B")
    pdf.set_text_color(10, 22, 40)
    pdf._cell_ln(0, 8, "2. Routing Decision")
    pdf._set_font_safe(size=10)
    pdf.set_text_color(60, 60, 60)
    complexity = routing_info.get("complexity", "N/A")
    model = routing_info.get("selected_model_label", routing_info.get("selected_model", "N/A"))
    latency = routing_info.get("total_latency_ms", "N/A")
    pdf._cell_ln(0, 6, pdf._safe_text(f"  Complexity: {complexity} | Model: {model} | Latency: {latency}ms"))
    pdf.ln(5)

    if product_matches:
        pdf._set_font_safe(size=11, style="B")
        pdf.set_text_color(10, 22, 40)
        pdf._cell_ln(0, 8, "3. Matching Products")
        pdf._set_font_safe(size=10)
        pdf.set_text_color(60, 60, 60)
        for match in product_matches[:5]:
            product = match.get("product", match)
            name = product.get("name", product.get("product_name", "N/A"))
            score = match.get("score", match.get("match_score", "N/A"))
            pdf._cell_ln(0, 6, pdf._safe_text(f"  - {name} (Match: {score}%)"))
        pdf.ln(5)

    if feasibility_matrix:
        pdf._set_font_safe(size=11, style="B")
        pdf.set_text_color(10, 22, 40)
        pdf._cell_ln(0, 8, "4. Feasibility Matrix")
        pdf._set_font_safe(size=10)
        pdf.set_text_color(60, 60, 60)
        for param, status_info in feasibility_matrix.items():
            if isinstance(status_info, dict):
                status = status_info.get("status", "N/A")
                note = status_info.get("note", "")
                pdf._cell_ln(0, 6, pdf._safe_text(f"  {param}: {status} - {note}"))
            else:
                pdf._cell_ln(0, 6, pdf._safe_text(f"  {param}: {status_info}"))
        pdf.ln(5)

    pdf._set_font_safe(size=11, style="B")
    pdf.set_text_color(10, 22, 40)
    pdf._cell_ln(0, 8, "5. Proposal")
    pdf._set_font_safe(size=10)
    pdf.set_text_color(60, 60, 60)
    cleaned_text = _strip_markdown(proposal_text)
    cleaned_text = pdf._safe_text(cleaned_text)
    pdf.multi_cell(0, 5.5, cleaned_text)
    pdf.ln(5)

    pdf._set_font_safe(size=11, style="B")
    pdf.set_text_color(10, 22, 40)
    pdf._cell_ln(0, 8, "6. Token Analysis")
    pdf._set_font_safe(size=10)
    pdf.set_text_color(60, 60, 60)
    total_tokens = token_stats.get("total_tokens", 0)
    total_cost = token_stats.get("actual_total_cost", 0)
    savings_pct = token_stats.get("savings_pct", 0)
    pdf._cell_ln(0, 6, f"  Total tokens: {total_tokens:,}")
    pdf._cell_ln(0, 6, f"  Cost: ${total_cost:.4f}")
    pdf._cell_ln(0, 6, f"  Savings vs. flagship: {savings_pct}%")

    return bytes(pdf.output())
