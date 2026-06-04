#!/usr/bin/env python3
"""
Extract chess diagram images, chapter divider images, and chapter icons
from the English PDF of "Chess Is Child's Play".
"""

import os
import json
import fitz  # PyMuPDF


# English PDF path
PDF_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "Chess Is Childs Play Teaching Techniques That Work "
    "(Laura Sherman, Bill Kilpatrick) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
)

# Output directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIAGRAMS_DIR = os.path.join(BASE_DIR, "extracted_images", "diagrams")
DIVIDERS_DIR = os.path.join(BASE_DIR, "extracted_images", "dividers")
ICONS_DIR = os.path.join(BASE_DIR, "extracted_images", "icons")

# Chapter page ranges (0-indexed)
CHAPTER_RANGES = {
    1: (10, 17), 2: (18, 21), 3: (22, 32), 4: (33, 45),
    5: (46, 57), 6: (58, 66), 7: (67, 74), 8: (75, 92),
    9: (93, 104), 10: (105, 108), 11: (109, 119), 12: (120, 127),
    13: (128, 136), 14: (137, 158), 15: (159, 162), 16: (163, 170),
    17: (171, 175), 18: (176, 190), 19: (191, 207), 20: (208, 214),
    21: (215, 221), 22: (222, 228), 23: (229, 244), 24: (245, 255),
    25: (256, 276), 26: (277, 287),
}

# Chapter divider pages (1-indexed, these are full-page decorative images)
DIVIDER_PAGES_1INDEXED = [
    10, 18, 22, 33, 46, 58, 67, 75, 93, 105, 109, 120,
    128, 137, 159, 163, 171, 176, 191, 208, 215, 222, 229, 245, 256, 277
]


def is_chess_diagram(w, h):
    """Check if image dimensions match a chess diagram (small or wide)."""
    small = (380 <= w <= 470 and 380 <= h <= 470)
    wide = (800 <= w <= 870 and 350 <= h <= 500)
    return small or wide


def is_wide_diagram(w, h):
    """Check if a chess diagram is the wide variant."""
    return 800 <= w <= 870 and 350 <= h <= 500


def is_divider(w, h):
    """Check if image is a full-page chapter divider."""
    return w >= 900 and h >= 900


def is_icon(w, h):
    """Check if image is a chapter icon."""
    return 140 <= w <= 230 and 140 <= h <= 230


def extract_images():
    """Extract all images from the English PDF."""
    os.makedirs(DIAGRAMS_DIR, exist_ok=True)
    os.makedirs(DIVIDERS_DIR, exist_ok=True)
    os.makedirs(ICONS_DIR, exist_ok=True)

    doc = fitz.open(PDF_PATH)
    print(f"Opened PDF: {len(doc)} pages")

    # Track which xrefs we've already processed to avoid duplicates
    processed_xrefs = set()

    # Metadata for diagram dimensions (wide vs small)
    diagram_metadata = {}

    # --- Extract chess diagrams by chapter ---
    total_diagrams = 0
    for chapter_num in range(1, 27):
        start_page, end_page = CHAPTER_RANGES[chapter_num]
        diagram_count = 0

        for page_idx in range(start_page, end_page + 1):
            page = doc[page_idx]
            images = page.get_images(full=True)

            for img_info in images:
                xref = img_info[0]
                if xref in processed_xrefs:
                    continue

                # Get image dimensions
                w = img_info[2]  # width
                h = img_info[3]  # height

                if is_chess_diagram(w, h):
                    processed_xrefs.add(xref)
                    diagram_count += 1
                    total_diagrams += 1

                    # Extract image
                    img_data = doc.extract_image(xref)
                    img_bytes = img_data["image"]
                    ext = img_data["ext"]

                    filename = f"diagram_{chapter_num}_{diagram_count}.png"
                    filepath = os.path.join(DIAGRAMS_DIR, filename)

                    with open(filepath, 'wb') as f:
                        f.write(img_bytes)

                    # Record if wide or small
                    diagram_metadata[f"{chapter_num}.{diagram_count}"] = {
                        "wide": is_wide_diagram(w, h),
                        "width": w,
                        "height": h,
                    }

        print(f"  Chapter {chapter_num}: {diagram_count} diagrams")

    print(f"\nTotal chess diagrams extracted: {total_diagrams}")

    # Save diagram metadata
    metadata_path = os.path.join(BASE_DIR, "extracted_images", "diagram_metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(diagram_metadata, f, indent=2)
    print(f"Saved diagram metadata to {metadata_path}")

    # --- Extract chapter dividers ---
    divider_xrefs = set()
    divider_count = 0
    for ch_idx, page_1indexed in enumerate(DIVIDER_PAGES_1INDEXED):
        page_0indexed = page_1indexed - 1
        page = doc[page_0indexed]
        images = page.get_images(full=True)

        for img_info in images:
            xref = img_info[0]
            w = img_info[2]
            h = img_info[3]

            if is_divider(w, h) and xref not in divider_xrefs:
                divider_xrefs.add(xref)
                divider_count += 1
                ch_num = ch_idx + 1

                img_data = doc.extract_image(xref)
                img_bytes = img_data["image"]

                filename = f"divider_ch{ch_num}.png"
                filepath = os.path.join(DIVIDERS_DIR, filename)

                with open(filepath, 'wb') as f:
                    f.write(img_bytes)
                break  # Only one divider per page

    print(f"\nTotal chapter dividers extracted: {divider_count}")

    # --- Extract chapter icons ---
    icon_xrefs = set()
    icon_count = 0
    # Icons typically appear on chapter start pages (same as divider pages or page after)
    for page_1indexed in DIVIDER_PAGES_1INDEXED:
        # Check divider page and the next page
        for offset in range(0, 3):
            page_0indexed = page_1indexed - 1 + offset
            if page_0indexed >= len(doc):
                continue
            page = doc[page_0indexed]
            images = page.get_images(full=True)

            for img_info in images:
                xref = img_info[0]
                w = img_info[2]
                h = img_info[3]

                if is_icon(w, h) and xref not in icon_xrefs:
                    icon_xrefs.add(xref)
                    icon_count += 1

                    img_data = doc.extract_image(xref)
                    img_bytes = img_data["image"]

                    filename = f"icon_{icon_count}_page{page_1indexed + offset}.png"
                    filepath = os.path.join(ICONS_DIR, filename)

                    with open(filepath, 'wb') as f:
                        f.write(img_bytes)

    print(f"Total chapter icons extracted: {icon_count}")

    doc.close()
    print("\nDone!")
    return total_diagrams


if __name__ == '__main__':
    count = extract_images()
    if count != 256:
        print(f"\nWARNING: Expected 256 diagrams but got {count}")
    else:
        print(f"\nSUCCESS: All 256 diagrams extracted!")
