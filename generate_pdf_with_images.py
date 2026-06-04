#!/usr/bin/env python3
"""
Generate a well-formatted PDF of the complete Uzbek translation of
"Chess Is Child's Play" (Shaxmat - Bolalar O'yini) with embedded
chess diagram images, chapter dividers, and chapter icons.
"""

import os
import re
import json
from fpdf import FPDF
from fpdf.enums import XPos, YPos


# Chapter definitions: (filename, toc_title, chapter_number_or_None)
# chapter_number is used for divider/icon lookup (1-26 for actual chapters)
CHAPTERS = [
    ("00_preface.txt", "So'z boshi", None),
    ("00_authors_bio.txt", "Mualliflar haqida", None),
    ("01_why_chess.txt", "1-bob. Nima uchun shaxmat?", 1),
    ("02_what_to_expect.txt", "2-bob. Darslardan nimani kutish kerak", 2),
    ("03_tips_on_teaching.txt", "3-bob. O'qitish bo'yicha maslahatlar", 3),
    ("04_special_exercises.txt", "4-bob. Ikki-to'rt yoshlilar uchun maxsus mashqlar", 4),
    ("05_the_rook.txt", "5-bob. Tura", 5),
    ("06_how_to_take_pieces.txt", "6-bob. Boshqa o'yinchining donalarini qanday olish mumkin", 6),
    ("07_the_bishop.txt", "7-bob. Fil", 7),
    ("08_attack_and_defend.txt", "8-bob. Donalarni qanday hujum qilish va himoya qilish", 8),
    ("09_the_queen.txt", "9-bob. Farzin", 9),
    ("10_the_king.txt", "10-bob. Shoh", 10),
    ("11_check.txt", "11-bob. Shoh", 11),
    ("12_checkmate.txt", "12-bob. Mat", 12),
    ("13_the_knight.txt", "13-bob. Ot", 13),
    ("14_the_pawn.txt", "14-bob. Piyoda", 14),
    ("15_legal_and_illegal_moves.txt", "15-bob. Qonuniy va noqonuniy yurishlar", 15),
    ("16_how_to_set_up_chessboard.txt", "16-bob. Shaxmat taxtasini qanday joylashtirish", 16),
    ("17_the_first_game.txt", "17-bob. Birinchi o'yin", 17),
    ("18_castling.txt", "18-bob. Qal'a qilish", 18),
    ("19_tips_for_starting.txt", "19-bob. Shaxmat o'yinini qanday boshlash bo'yicha maslahatlar", 19),
    ("20_value_of_pieces.txt", "20-bob. Donalarning qiymati", 20),
    ("21_pieces_in_the_way.txt", "21-bob. Sizning donalaringiz yo'lda to'siq bo'lishi mumkin", 21),
    ("22_more_about_attacking.txt", "22-bob. Hujum haqida batafsil", 22),
    ("23_more_about_defending.txt", "23-bob. Himoya haqida batafsil", 23),
    ("24_getting_out_of_check.txt", "24-bob. Shohdan qanday chiqish", 24),
    ("25_more_about_checkmate.txt", "25-bob. Mat haqida batafsil", 25),
    ("26_stalemate_and_draw.txt", "26-bob. Pat va durang", 26),
    ("27_afterword.txt", "Xotima", None),
]

# Section headers to format distinctly
SECTION_HEADERS = [
    "Qahva suhbati",
    "Murabbiy maslahati",
    "Muammolar va yechimlar",
]

# Diagram pattern: matches [Diagramma X.Y]
DIAGRAM_PATTERN = re.compile(r'\[Diagramma\s+(\d+)\.(\d+)\]')

# Chapters that have icons (chapter_number -> icon_filename)
CHAPTER_ICONS = {
    2: "icon_1_page19.png",
    4: "icon_2_page34.png",
    5: "icon_3_page47.png",
    6: "icon_4_page59.png",
    11: "icon_5_page110.png",
    12: "icon_6_page121.png",
    13: "icon_7_page129.png",
    15: "icon_8_page160.png",
    16: "icon_9_page164.png",
    18: "icon_10_page177.png",
    19: "icon_11_page192.png",
    22: "icon_12_page223.png",
    23: "icon_13_page230.png",
}


class BookPDF(FPDF):
    """Custom PDF class for the chess book with embedded images."""

    def __init__(self, diagram_metadata):
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
        self.diagram_metadata = diagram_metadata

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

        return toc_page

    def add_toc_entry(self, title, page_num):
        """Record a TOC entry."""
        self.toc_entries.append((title, page_num))

    def write_toc(self, toc_page):
        """Write TOC entries on the TOC page."""
        current_page = self.page_no()
        self.page = toc_page
        self.set_y(52)

        avail_width = self.w - self.l_margin - self.r_margin

        for title, page_num in self.toc_entries:
            self.set_font('DejaVu', '', 11)
            title_width = self.get_string_width(title)
            page_str = str(page_num)
            page_width = self.get_string_width(page_str)

            dot_width = self.get_string_width('.')
            dots_space = avail_width - title_width - page_width - 4
            num_dots = max(3, int(dots_space / dot_width))
            dots = '.' * num_dots

            line = title + ' ' + dots + ' ' + page_str
            self.cell(0, 7, line, 0, align='L',
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.page = current_page

    def add_divider_page(self, chapter_num):
        """Add a full-page chapter divider image."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        divider_path = os.path.join(base_dir, "extracted_images", "dividers",
                                    f"divider_ch{chapter_num}.png")
        if os.path.exists(divider_path):
            self.add_page()
            # Fill the entire A4 page (210 x 297 mm)
            self.image(divider_path, x=0, y=0, w=210, h=297)

    def add_chapter(self, title, content, chapter_num=None):
        """Add a chapter to the PDF."""
        # Add chapter divider page if applicable
        if chapter_num is not None:
            self.add_divider_page(chapter_num)

        self.add_page()
        page_num = self.page_no()
        self.add_toc_entry(title, page_num)

        # Add chapter icon if applicable
        if chapter_num is not None and chapter_num in CHAPTER_ICONS:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(base_dir, "extracted_images", "icons",
                                     CHAPTER_ICONS[chapter_num])
            if os.path.exists(icon_path):
                # Place icon centered, ~20mm wide
                page_width = self.w - self.l_margin - self.r_margin
                icon_w = 20
                icon_x = self.l_margin + (page_width - icon_w) / 2
                self.image(icon_path, x=icon_x, y=self.get_y(), w=icon_w)
                self.ln(22)  # Space below icon

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

        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines - add spacing
            if not line:
                self.ln(3)
                i += 1
                continue

            # Check for diagram references
            match = DIAGRAM_PATTERN.match(line)
            if match:
                ch_num = match.group(1)
                diag_num = match.group(2)
                self._insert_diagram(ch_num, diag_num)
                i += 1
                continue

            # Check for section headers
            is_section_header = False
            for section in SECTION_HEADERS:
                if line.startswith(section):
                    self._write_section_header(line)
                    is_section_header = True
                    break

            if is_section_header:
                i += 1
                continue

            # Check for step/qadam headers
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
        """Write a section header."""
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

    def _insert_diagram(self, chapter_str, diagram_str):
        """Insert a chess diagram image at the current position."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        diagram_path = os.path.join(base_dir, "extracted_images", "diagrams",
                                    f"diagram_{chapter_str}_{diagram_str}.png")

        key = f"{chapter_str}.{diagram_str}"
        meta = self.diagram_metadata.get(key, {})
        is_wide = meta.get("wide", False)

        # Determine image width
        page_width = self.w - self.l_margin - self.r_margin  # ~170mm
        if is_wide:
            img_w = 170  # Nearly full page width
        else:
            img_w = 80   # Square diagram at 80mm

        # Calculate x position for centering
        x_pos = self.l_margin + (page_width - img_w) / 2

        # Calculate approximate image height for page break check
        if os.path.exists(diagram_path):
            if is_wide:
                # Wide diagrams: aspect ratio ~ 826:478 -> h = w * 478/826
                img_h = img_w * (meta.get("height", 478) / meta.get("width", 826))
            else:
                # Square diagrams: roughly square
                img_h = img_w * (meta.get("height", 450) / meta.get("width", 450))
        else:
            img_h = img_w  # fallback

        # Check if we need a page break (image + caption + margins)
        needed_space = img_h + 12  # image height + space for caption
        available = self.h - self.get_y() - 20  # bottom margin

        if needed_space > available:
            self.add_page()

        self.ln(4)

        if os.path.exists(diagram_path):
            y_pos = self.get_y()
            self.image(diagram_path, x=x_pos, y=y_pos, w=img_w)
            self.set_y(y_pos + img_h + 2)
        else:
            # Fallback: render as text placeholder if image missing
            self.set_font('DejaVu', 'I', 10)
            self.set_fill_color(230, 230, 250)
            self.cell(0, 8, f"[Diagramma {chapter_str}.{diagram_str}]", 1,
                      align='C', fill=True,
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Caption below diagram
        self.set_font('DejaVu', 'I', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, f"Diagramma {chapter_str}.{diagram_str}", 0,
                  align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)
        self.ln(4)


def main():
    """Main function to generate the PDF with images."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    chapters_dir = os.path.join(base_dir, 'chapters_uz')
    output_path = os.path.join(base_dir, "Shaxmat - bolalar o'yini (O'zbek tilida tarjima).pdf")

    # Load diagram metadata
    metadata_path = os.path.join(base_dir, "extracted_images", "diagram_metadata.json")
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            diagram_metadata = json.load(f)
        print(f"Loaded metadata for {len(diagram_metadata)} diagrams")
    else:
        print("WARNING: No diagram metadata found, using defaults")
        diagram_metadata = {}

    print("Creating PDF with images...")
    pdf = BookPDF(diagram_metadata)

    # Title page
    pdf.create_title_page()

    # Table of Contents page
    toc_page = pdf.create_toc_page()

    # Add chapters
    for filename, toc_title, chapter_num in CHAPTERS:
        filepath = os.path.join(chapters_dir, filename)
        if not os.path.exists(filepath):
            print(f"  WARNING: {filename} not found, skipping.")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        print(f"  Adding: {toc_title}")
        pdf.add_chapter(toc_title, content, chapter_num)

    # Write table of contents
    print("  Writing Table of Contents...")
    pdf.write_toc(toc_page)

    # Save PDF
    print(f"  Saving PDF to: {output_path}")
    pdf.output(output_path)

    # Verify
    file_size = os.path.getsize(output_path)
    print(f"\nPDF generated successfully!")
    print(f"  File size: {file_size / (1024*1024):.1f} MB")
    print(f"  Total pages: {pdf.page_no()}")
    print(f"  Chapters: {len(pdf.toc_entries)}")

    if file_size < 2 * 1024 * 1024:
        print("  WARNING: File seems small for a PDF with images.")

    return output_path


if __name__ == '__main__':
    main()
