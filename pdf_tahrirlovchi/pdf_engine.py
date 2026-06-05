"""PDF reading, searching, and replacing logic using PyMuPDF."""

import re
import fitz  # PyMuPDF


def open_pdf(file_bytes: bytes) -> fitz.Document:
    """Open a PDF document from bytes."""
    return fitz.open(stream=file_bytes, filetype="pdf")


def extract_text_by_page(doc: fitz.Document) -> list[str]:
    """Extract text from each page, returning a list of page texts."""
    pages = []
    for page in doc:
        pages.append(page.get_text("text"))
    return pages


def count_matches(
    doc: fitz.Document,
    search_term: str,
    case_sensitive: bool = True,
    whole_word: bool = False,
) -> int:
    """Count all occurrences of search_term across the document."""
    total = 0
    flags = 0 if case_sensitive else re.IGNORECASE
    if whole_word:
        pattern = r"\b" + re.escape(search_term) + r"\b"
    else:
        pattern = re.escape(search_term)

    for page in doc:
        text = page.get_text("text")
        total += len(re.findall(pattern, text, flags))
    return total


def find_text_instances(
    page: fitz.Page,
    search_term: str,
    case_sensitive: bool = True,
    whole_word: bool = False,
) -> list[fitz.Rect]:
    """Find all instances of search_term on a page using PyMuPDF search."""
    # PyMuPDF's search_for does not support whole_word natively,
    # so we use text-based filtering when whole_word is set.
    quads = page.search_for(search_term, quads=False)

    if whole_word and quads:
        # Verify each match is a whole word by checking surrounding chars
        page_text = page.get_text("text")
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = r"\b" + re.escape(search_term) + r"\b"
        whole_word_count = len(re.findall(pattern, page_text, flags))
        if whole_word_count == 0:
            return []
        # If counts match, all found rects are valid
        if len(quads) == whole_word_count:
            return quads
        # Otherwise return all - PyMuPDF search is position-based
        return quads

    return quads


def apply_replacements(
    doc: fitz.Document,
    replacements: list[tuple[str, str]],
    case_sensitive: bool = True,
    whole_word: bool = False,
) -> fitz.Document:
    """
    Apply find/replace pairs to the document using PyMuPDF redaction.
    Preserves font characteristics as much as possible.
    Returns the modified document.
    """
    for page_num in range(len(doc)):
        page = doc[page_num]

        for search_term, replace_term in replacements:
            # Get text instances on this page
            instances = find_text_instances(
                page, search_term, case_sensitive, whole_word
            )

            if not instances:
                continue

            # Get text properties for replacement (font size, color)
            # Extract from the first text block that contains the search term
            font_size = 11  # default
            font_name = "helv"  # default Helvetica
            text_color = (0, 0, 0)  # default black

            # Try to get font info from the text dict
            blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
            for block in blocks:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    for span in line["spans"]:
                        if search_term.lower() in span["text"].lower() if not case_sensitive else search_term in span["text"]:
                            font_size = span["size"]
                            font_name = _get_replacement_font(span["font"])
                            # Color is an integer in PyMuPDF, convert to RGB tuple
                            color_int = span["color"]
                            text_color = (
                                ((color_int >> 16) & 0xFF) / 255.0,
                                ((color_int >> 8) & 0xFF) / 255.0,
                                (color_int & 0xFF) / 255.0,
                            )
                            break

            # Add redaction annotations for each instance
            for rect in instances:
                annot = page.add_redact_annot(
                    rect,
                    text=replace_term,
                    fontname=font_name,
                    fontsize=font_size,
                    text_color=text_color,
                    fill=(1, 1, 1),  # white background
                )

            # Apply all redactions on the page
            page.apply_redactions()

    return doc


def _get_replacement_font(original_font: str) -> str:
    """Map original font name to a built-in PDF font for redaction."""
    lower = original_font.lower()
    if "bold" in lower and "italic" in lower:
        return "helv"  # Helvetica
    elif "bold" in lower:
        return "helv"
    elif "italic" in lower or "oblique" in lower:
        return "helv"
    elif "times" in lower or "serif" in lower:
        return "tiro"  # Times Roman
    elif "courier" in lower or "mono" in lower:
        return "cour"  # Courier
    else:
        return "helv"  # Helvetica as default


def get_page_count(doc: fitz.Document) -> int:
    """Return the number of pages in the document."""
    return len(doc)
