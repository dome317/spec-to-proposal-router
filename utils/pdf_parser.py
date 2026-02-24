"""PDF text extraction using PyMuPDF (fitz)."""

import fitz


def extract_text_from_pdf(file_bytes):
    """Extract all text content from a PDF file.

    Args:
        file_bytes: Raw bytes of the PDF file.

    Returns:
        Extracted text as a single string.
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text())
    doc.close()
    return "\n".join(text_parts).strip()
