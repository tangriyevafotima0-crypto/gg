#!/usr/bin/env python3
"""
Extract text from the chess book PDF and organize it into separate chapter files.
Uses pdfplumber to extract text page by page, identifies chapter boundaries using
a printed-page-number-to-PDF-page-index mapping, and saves each chapter as a
separate text file in chapters_en/ directory.
"""

import os
import re
import pdfplumber

PDF_PATH = "Chess Is Childs Play Teaching Techniques That Work (Laura Sherman, Bill Kilpatrick) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
OUTPUT_DIR = "chapters_en"

# Chapter structure from Table of Contents with PRINTED page numbers.
CHAPTERS = [
    ("00_preface", "Preface", 9),
    ("00_authors_bio", "Authors' biographies", 10),
    ("01_why_chess", "Chapter 1. Why Chess?", 11),
    ("02_what_to_expect", "Chapter 2. What You Should Expect from the Lessons", 19),
    ("03_tips_on_teaching", "Chapter 3. Tips on Teaching", 23),
    ("04_special_exercises", "Chapter 4. Special Exercises for Two-to Four-Year-Olds", 35),
    ("05_the_rook", "Chapter 5. The Rook", 49),
    ("06_how_to_take_pieces", "Chapter 6. How to Take the Other Player's Pieces", 61),
    ("07_the_bishop", "Chapter 7. The Bishop", 71),
    ("08_attack_and_defend", "Chapter 8. How to Attack and Defend Pieces", 79),
    ("09_the_queen", "Chapter 9. The Queen", 97),
    ("10_the_king", "Chapter 10. The King", 109),
    ("11_check", "Chapter 11. Check", 113),
    ("12_checkmate", "Chapter 12. Checkmate", 125),
    ("13_the_knight", "Chapter 13. The Knight", 133),
    ("14_the_pawn", "Chapter 14. The Pawn", 143),
    ("15_legal_and_illegal_moves", "Chapter 15. Legal and Illegal Moves", 165),
    ("16_how_to_set_up_chessboard", "Chapter 16. How to Set Up the Chessboard", 169),
    ("17_the_first_game", "Chapter 17. The First Game", 177),
    ("18_castling", "Chapter 18. Castling", 183),
    ("19_tips_for_starting", "Chapter 19. Tips for How to Start a Game of Chess", 199),
    ("20_value_of_pieces", "Chapter 20. Value of the Pieces", 217),
    ("21_pieces_in_the_way", "Chapter 21. Your Pieces Can Get in the Way", 225),
    ("22_more_about_attacking", "Chapter 22. More About Attacking", 233),
    ("23_more_about_defending", "Chapter 23. More About Defending", 241),
    ("24_getting_out_of_check", "Chapter 24. Getting Out of Check", 257),
    ("25_more_about_checkmate", "Chapter 25. More About Checkmate", 269),
    ("26_stalemate_and_draw", "Chapter 26. Stalemate and Draw", 291),
    ("27_afterword", "Afterword", 302),
]


def build_printed_to_pdf_mapping(all_pages_text):
    """
    Build a mapping from printed page numbers to PDF page indices (0-indexed).
    
    Each page in the book has a printed page number at the bottom of the text.
    We extract these to create a reliable mapping.
    """
    printed_to_pdf = {}
    
    for pdf_idx, text in enumerate(all_pages_text):
        if not text.strip():
            continue
        lines = text.strip().split('\n')
        # The printed page number is typically the last line, a standalone number
        last_line = lines[-1].strip()
        if last_line.isdigit():
            printed_page = int(last_line)
            # Sanity check: printed page should be reasonable (9-302 range for this book)
            if 9 <= printed_page <= 310:
                printed_to_pdf[printed_page] = pdf_idx
    
    return printed_to_pdf


def find_pdf_page_for_printed(printed_page, printed_to_pdf, all_pages_text):
    """
    Find the PDF page index for a given printed page number.
    
    For chapters that start on a new printed page, the chapter content begins
    on that printed page. Sometimes the exact printed page number is in our
    mapping; other times we need to find the closest match.
    
    Some chapters start with image/title pages that have no extractable text.
    In those cases, we look for the first page with text at or after the expected location.
    """
    # Direct lookup
    if printed_page in printed_to_pdf:
        return printed_to_pdf[printed_page]
    
    # The printed page might be a title/image page with no text.
    # In that case, the actual content starts on the NEXT printed page.
    # Look for the nearest available printed page at or after the target.
    for pp in range(printed_page, printed_page + 5):
        if pp in printed_to_pdf:
            # The content page is at this PDF index, but the chapter might actually
            # start one PDF page before (the image/title page)
            pdf_idx = printed_to_pdf[pp]
            # Check if the previous page is blank/image (belongs to this chapter)
            if pdf_idx > 0 and not all_pages_text[pdf_idx - 1].strip():
                return pdf_idx - 1
            return pdf_idx
    
    # Fallback: interpolate from nearby known pages
    known_pages = sorted(printed_to_pdf.keys())
    for i, kp in enumerate(known_pages):
        if kp > printed_page:
            if i > 0:
                prev_pp = known_pages[i - 1]
                prev_pdf = printed_to_pdf[prev_pp]
                # Estimate based on page difference
                diff = printed_page - prev_pp
                return prev_pdf + diff
            break
    
    return None


def extract_chapters():
    """Main function to extract and save chapter texts."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"Opening PDF: {PDF_PATH}")
    pdf = pdfplumber.open(PDF_PATH)
    total_pages = len(pdf.pages)
    print(f"Total PDF pages: {total_pages}")
    
    # Extract all page texts
    print("Extracting text from all pages...")
    all_pages_text = []
    for i in range(total_pages):
        text = pdf.pages[i].extract_text() or ""
        all_pages_text.append(text)
    
    # Build printed-to-PDF page mapping
    print("Building page number mapping...")
    printed_to_pdf = build_printed_to_pdf_mapping(all_pages_text)
    print(f"  Found {len(printed_to_pdf)} pages with printed page numbers")
    
    # Show some mapping samples for verification
    sample_pages = [9, 10, 11, 19, 23, 49, 97, 143, 199, 269, 291, 302]
    for sp in sample_pages:
        if sp in printed_to_pdf:
            print(f"  Printed page {sp} -> PDF page {printed_to_pdf[sp]} (0-indexed)")
    
    # Determine PDF page ranges for each chapter
    print(f"\nDetermining chapter boundaries...")
    chapter_pages = []
    
    for i, (filename, title, printed_page) in enumerate(CHAPTERS):
        pdf_start = find_pdf_page_for_printed(printed_page, printed_to_pdf, all_pages_text)
        
        if pdf_start is None:
            print(f"  WARNING: Could not find PDF page for '{title}' (printed page {printed_page})")
            pdf_start = 0
        
        chapter_pages.append((filename, title, printed_page, pdf_start))
    
    # Now extract text for each chapter using the determined ranges
    print(f"\nExtracting {len(chapter_pages)} chapters...")
    total_chars = 0
    
    for i, (filename, title, printed_page, pdf_start) in enumerate(chapter_pages):
        # End page is one before the start of the next chapter
        if i + 1 < len(chapter_pages):
            pdf_end = chapter_pages[i + 1][3] - 1
        else:
            # Last chapter (Afterword) - goes to the last content page
            # Skip the back cover (last page)
            pdf_end = total_pages - 2  # Exclude back cover
        
        chapter_text_parts = []
        
        for page_idx in range(pdf_start, min(pdf_end + 1, total_pages)):
            page_text = all_pages_text[page_idx]
            if page_text.strip():
                # Remove the printed page number from the bottom
                lines = page_text.split('\n')
                if lines and lines[-1].strip().isdigit():
                    lines = lines[:-1]
                chapter_text_parts.append('\n'.join(lines))
        
        chapter_text = '\n\n'.join(chapter_text_parts)
        
        # Save the chapter file
        output_path = os.path.join(OUTPUT_DIR, f"{filename}.txt")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(chapter_text)
        
        char_count = len(chapter_text)
        total_chars += char_count
        page_count = pdf_end - pdf_start + 1
        print(f"  {filename}.txt - {char_count:,} chars ({page_count} pages: PDF {pdf_start}-{pdf_end})")
    
    print(f"\nTotal characters extracted: {total_chars:,}")
    print(f"Expected (from extracted_text.txt): ~272,245")
    print(f"Difference: {total_chars - 272245:+,} chars")
    print(f"\nAll {len(chapter_pages)} chapter files saved to {OUTPUT_DIR}/")
    
    # Verify all files exist
    files = sorted(os.listdir(OUTPUT_DIR))
    print(f"\nFiles in {OUTPUT_DIR}/ ({len(files)} total):")
    for f in files:
        filepath = os.path.join(OUTPUT_DIR, f)
        size = os.path.getsize(filepath)
        print(f"  {f} ({size:,} bytes)")
    
    pdf.close()


if __name__ == "__main__":
    extract_chapters()
