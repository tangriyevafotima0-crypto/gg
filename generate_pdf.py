#!/usr/bin/env python3
"""
Generate a well-formatted PDF of the complete Uzbek translation of
"Chess Is Child's Play" (Shaxmat - Bolalar O'yini).
"""

import os
import re
from fpdf import FPDF
from fpdf.enums import XPos, YPos


# Chapter definitions: (filename, toc_title)
CHAPTERS = [
    ("00_preface.txt", "So'z boshi"),
    ("00_authors_bio.txt", "Mualliflar haqida"),
    ("01_why_chess.txt", "1-bob. Nima uchun shaxmat?"),
    ("02_what_to_expect.txt", "2-bob. Darslardan nimani kutish kerak"),
    ("03_tips_on_teaching.txt", "3-bob. O'qitish bo'yicha maslahatlar"),
    ("04_special_exercises.txt", "4-bob. Ikki-to'rt yoshlilar uchun maxsus mashqlar"),
    ("05_the_rook.txt", "5-bob. Tura"),
    ("06_how_to_take_pieces.txt", "6-bob. Boshqa o'yinchining donalarini qanday olish mumkin"),
    ("07_the_bishop.txt", "7-bob. Fil"),
    ("08_attack_and_defend.txt", "8-bob. Donalarni qanday hujum qilish va himoya qilish"),
    ("09_the_queen.txt", "9-bob. Farzin"),
    ("10_the_king.txt", "10-bob. Shoh"),
    ("11_check.txt", "11-bob. Shoh"),
    ("12_checkmate.txt", "12-bob. Mat"),
    ("13_the_knight.txt", "13-bob. Ot"),
    ("14_the_pawn.txt", "14-bob. Piyoda"),
    ("15_legal_and_illegal_moves.txt", "15-bob. Qonuniy va noqonuniy yurishlar"),
    ("16_how_to_set_up_chessboard.txt", "16-bob. Shaxmat taxtasini qanday joylashtirish"),
    ("17_the_first_game.txt", "17-bob. Birinchi o'yin"),
    ("18_castling.txt", "18-bob. Qal'a qilish"),
    ("19_tips_for_starting.txt", "19-bob. Shaxmat o'yinini qanday boshlash bo'yicha maslahatlar"),
    ("20_value_of_pieces.txt", "20-bob. Donalarning qiymati"),
    ("21_pieces_in_the_way.txt", "21-bob. Sizning donalaringiz yo'lda to'siq bo'lishi mumkin"),
    ("22_more_about_attacking.txt", "22-bob. Hujum haqida batafsil"),
    ("23_more_about_defending.txt", "23-bob. Himoya haqida batafsil"),
    ("24_getting_out_of_check.txt", "24-bob. Shohdan qanday chiqish"),
    ("25_more_about_checkmate.txt", "25-bob. Mat haqida batafsil"),
    ("26_stalemate_and_draw.txt", "26-bob. Pat va durang"),
    ("27_afterword.txt", "Xotima"),
]

# Section headers to format distinctly
SECTION_HEADERS = [
    "Qahva suhbati",
    "Murabbiy maslahati",
    "Muammolar va yechimlar",
]

# Diagram pattern
DIAGRAM_PATTERN = re.compile(r'\[Diagramma\s+\d+\.\d+\]')


class BookPDF(FPDF):
    """Custom PDF class for the chess book."""

    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(20, 20, 20)

        # Load fonts
        font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
        self.add_font('DejaVu', '', os.path.join(font_dir, 'DejaVuSans.ttf'))
        self.add_font('DejaVu', 'B', os.path.join(font_dir, 'DejaVuSans-Bold.ttf'))
        self.add_font('DejaVu', 'I', os.path.join(font_dir, 'DejaVuSans-Oblique.ttf'))

        self.chapter_title = ""
        self.toc_entries = []  # (title, page_number)
        self.in_header_footer = False

    def header(self):
        """Add header to each page (except title page and TOC)."""
        self.in_header_footer = True
        if self.page_no() > 2:
            self.set_font('DejaVu', 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 5, "Shaxmat - Bolalar O'yini", 0, align='C',
                      new_x=XPos.RIGHT, new_y=YPos.TOP)
            self.ln(8)
            self.set_text_color(0, 0, 0)
        self.in_header_footer = False

    def footer(self):
        """Add page number footer."""
        self.in_header_footer = True
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font('DejaVu', '', 9)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, str(self.page_no()), 0, align='C',
                      new_x=XPos.RIGHT, new_y=YPos.TOP)
            self.set_text_color(0, 0, 0)
        self.in_header_footer = False

    def create_title_page(self):
        """Create the title page."""
        self.add_page()
        self.ln(50)

        # Main title
        self.set_font('DejaVu', 'B', 28)
        self.cell(0, 15, "SHAXMAT - BOLALAR O'YINI", 0, align='C',
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(10)

        # Subtitle
        self.set_font('DejaVu', 'I', 18)
        self.cell(0, 10, "O'qitish texnikalari", 0, align='C',
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(20)

        # Authors
        self.set_font('DejaVu', '', 14)
        self.cell(0, 8, "Laura Sherman va Bill Kilpatrick", 0, align='C',
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(60)

        # Translation note
        self.set_font('DejaVu', 'I', 12)
        self.cell(0, 8, "O'zbek tiliga tarjima", 0, align='C',
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def create_toc_page(self):
        """Create the table of contents page. Returns the page number where TOC starts."""
        self.add_page()
        toc_page = self.page_no()

        self.set_font('DejaVu', 'B', 20)
        self.cell(0, 12, "Mundarija", 0, align='C',
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(10)

        # TOC entries will be filled in after all chapters are added
        return toc_page

    def add_toc_entry(self, title, page_num):
        """Record a TOC entry."""
        self.toc_entries.append((title, page_num))

    def write_toc(self, toc_page):
        """Write TOC entries on the TOC page."""
        # Save current page
        current_page = self.page_no()

        # Go to TOC page
        self.page = toc_page
        self.set_y(52)  # After title

        avail_width = self.w - self.l_margin - self.r_margin

        for title, page_num in self.toc_entries:
            self.set_font('DejaVu', '', 11)
            title_width = self.get_string_width(title)
            page_str = str(page_num)
            page_width = self.get_string_width(page_str)

            # Calculate dot width
            dot_width = self.get_string_width('.')
            dots_space = avail_width - title_width - page_width - 4
            num_dots = max(3, int(dots_space / dot_width))
            dots = '.' * num_dots

            line = title + ' ' + dots + ' ' + page_str
            self.cell(0, 7, line, 0, align='L',
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Restore page
        self.page = current_page

    def add_chapter(self, title, content):
        """Add a chapter to the PDF."""
        self.add_page()
        page_num = self.page_no()
        self.add_toc_entry(title, page_num)

        # Chapter title
        self.set_font('DejaVu', 'B', 16)
        self.multi_cell(0, 9, title, 0, 'L')
        self.ln(6)

        # Process content
        self._write_content(content)

        return page_num

    def _write_content(self, content):
        """Write chapter content with formatting."""
        lines = content.split('\n')
        i = 0
        in_section = False

        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines - add spacing
            if not line:
                self.ln(3)
                i += 1
                continue

            # Check for diagram references
            if DIAGRAM_PATTERN.match(line):
                self._write_diagram_placeholder(line)
                i += 1
                continue

            # Check for section headers
            is_section_header = False
            for section in SECTION_HEADERS:
                if line.startswith(section):
                    self._write_section_header(line)
                    is_section_header = True
                    in_section = True
                    break

            if is_section_header:
                i += 1
                continue

            # Check for step/qadam headers (e.g., "Qadam 1:", "1a.", "1b.")
            if re.match(r'^(Qadam\s+\d+|^\d+[a-z]?[\.\)])', line):
                self._write_step_header(line)
                i += 1
                continue

            # Regular body text
            self._write_body_text(line)
            i += 1

    def _write_body_text(self, text):
        """Write regular body text."""
        self.set_font('DejaVu', '', 11)
        self.multi_cell(0, 6, text, 0, 'J')
        self.ln(1)

    def _write_section_header(self, text):
        """Write a section header (Qahva suhbati, Murabbiy maslahati, etc.)."""
        self.ln(4)
        self.set_font('DejaVu', 'B', 12)
        self.set_fill_color(240, 240, 240)
        self.multi_cell(0, 8, text, 0, 'L', fill=True)
        self.ln(2)

    def _write_step_header(self, text):
        """Write a step header."""
        self.ln(3)
        self.set_font('DejaVu', 'B', 11)
        self.multi_cell(0, 6, text, 0, 'L')
        self.ln(1)

    def _write_diagram_placeholder(self, text):
        """Write a diagram placeholder in a distinct format."""
        self.ln(4)
        self.set_font('DejaVu', 'I', 10)
        self.set_fill_color(230, 230, 250)
        # Center the diagram reference
        self.cell(0, 8, text, 1, align='C', fill=True,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(4)


def main():
    """Main function to generate the PDF."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    chapters_dir = os.path.join(base_dir, 'chapters_uz')
    output_path = os.path.join(base_dir, "Shaxmat - bolalar o'yini (O'zbek tilida tarjima).pdf")

    print("Creating PDF...")
    pdf = BookPDF()

    # Title page
    pdf.create_title_page()

    # Table of Contents page
    toc_page = pdf.create_toc_page()

    # Add chapters
    for filename, toc_title in CHAPTERS:
        filepath = os.path.join(chapters_dir, filename)
        if not os.path.exists(filepath):
            print(f"  WARNING: {filename} not found, skipping.")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        print(f"  Adding: {toc_title}")
        pdf.add_chapter(toc_title, content)

    # Write table of contents
    print("  Writing Table of Contents...")
    pdf.write_toc(toc_page)

    # Save PDF
    print(f"  Saving PDF to: {output_path}")
    pdf.output(output_path)

    # Verify
    file_size = os.path.getsize(output_path)
    print(f"\nPDF generated successfully!")
    print(f"  File size: {file_size / 1024:.1f} KB")
    print(f"  Total pages: {pdf.page_no()}")
    print(f"  Chapters: {len(pdf.toc_entries)}")

    if file_size < 100 * 1024:
        print("  WARNING: File seems small, may be incomplete.")

    return output_path


if __name__ == '__main__':
    main()
