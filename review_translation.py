#!/usr/bin/env python3
"""
Translation Quality Review Script
Performs automated checks on the Uzbek translation of "Chess Is Child's Play"

Checks performed:
1. File size proportionality (Uzbek vs English)
2. Untranslated English words detection
3. Terminology consistency verification
4. Section header consistency
"""

import os
import re
from pathlib import Path

EN_DIR = Path("chapters_en")
UZ_DIR = Path("chapters_uz")

# Expected terminology
CHESS_PIECES = {
    "Shoh": "King",
    "Farzin": "Queen", 
    "Tura": "Rook",
    "Fil": "Bishop",
    "Ot": "Knight",
    "Piyoda": "Pawn",
}

# Terms that should NOT appear (inconsistent variants)
INCORRECT_VARIANTS = {
    "Vazir": "Should be 'Farzin' for Queen",
    "Qirol": "Should be 'Shoh' for King",
    "Ladia": "Should be 'Tura' for Rook",
    "Slon": "Should be 'Fil' for Bishop",
    "Kon": "Should be 'Ot' for Knight (Russian term)",
    "Peshka": "Should be 'Piyoda' for Pawn",
}

# Section headers that should be consistent
EXPECTED_HEADERS = [
    "Qahva suhbati",      # Coffee Talk
    "Murabbiy maslahati",  # Coach's Corner
    "Muammolar va yechimlar",  # Troubleshooting / Problems and Solutions
]

# Common English words that should not appear in translation
COMMON_ENGLISH_WORDS = [
    r'\bthe\b', r'\bis\b', r'\bare\b', r'\bcan\b', r'\bwill\b',
    r'\bshould\b', r'\bwould\b', r'\bcould\b', r'\bhave\b', r'\bhas\b',
    r'\bwith\b', r'\bthis\b', r'\bthat\b', r'\bfrom\b', r'\bthey\b',
    r'\btheir\b', r'\byour\b', r'\byou\b', r'\bwhat\b', r'\bwhen\b',
    r'\bwhere\b', r'\bhow\b', r'\bchild\b', r'\bchildren\b',
    r'\bpiece\b', r'\bpieces\b', r'\bboard\b', r'\bmove\b', r'\bmoves\b',
    r'\bgame\b', r'\bgames\b', r'\bplay\b', r'\bplayer\b',
    r'\bsquare\b', r'\bsquares\b',
]

# Words that are acceptable in English (proper nouns, technical terms)
ALLOWED_ENGLISH = [
    "Chess", "Laura", "Bill", "Dan", "Florida", "Los-Anjeles", "California",
    "IQ", "Your Chess Coach", "Coffee Talk", "Coach", "Mini-game",
    "www", "com", "ChessIsChildsPlay", "Palm", "Report", "Christine",
    "John", "Kennedy", "Cheryl", "Coles", "Bronx", "Public School",
    "en passant", "X", "O", "Diagram", "http", "online",
    "The Palm Report", "The Benefits", "L",
]


def get_file_pairs():
    """Get matching English and Uzbek file pairs."""
    en_files = sorted(EN_DIR.glob("*.txt"))
    pairs = []
    for en_file in en_files:
        uz_file = UZ_DIR / en_file.name
        if uz_file.exists():
            pairs.append((en_file, uz_file))
        else:
            print(f"WARNING: Missing Uzbek translation for {en_file.name}")
    return pairs


def check_file_sizes(pairs):
    """Check that Uzbek files are proportional in size to English files."""
    print("\n" + "=" * 60)
    print("CHECK 1: File Size Proportionality")
    print("=" * 60)
    
    issues = []
    ratios = []
    
    for en_file, uz_file in pairs:
        en_size = en_file.stat().st_size
        uz_size = uz_file.stat().st_size
        
        if en_size == 0:
            continue
            
        ratio = uz_size / en_size
        ratios.append((en_file.name, ratio, en_size, uz_size))
        
        # Uzbek text tends to be slightly longer due to agglutinative nature
        # Flag if ratio is too low (< 0.5) or too high (> 2.5)
        if ratio < 0.5:
            issues.append(f"  WARN: {en_file.name} - Uzbek file seems too short (ratio: {ratio:.2f}, EN: {en_size}b, UZ: {uz_size}b)")
        elif ratio > 2.5:
            issues.append(f"  WARN: {en_file.name} - Uzbek file seems too long (ratio: {ratio:.2f}, EN: {en_size}b, UZ: {uz_size}b)")
    
    if issues:
        print("Issues found:")
        for issue in issues:
            print(issue)
    else:
        print("  All file sizes are proportional (no chapters drastically shorter or longer)")
    
    # Print summary
    avg_ratio = sum(r[1] for r in ratios) / len(ratios) if ratios else 0
    print(f"\n  Average UZ/EN size ratio: {avg_ratio:.2f}")
    print(f"  Min ratio: {min(r[1] for r in ratios):.2f} ({min(ratios, key=lambda x: x[1])[0]})")
    print(f"  Max ratio: {max(r[1] for r in ratios):.2f} ({max(ratios, key=lambda x: x[1])[0]})")
    
    return issues


def check_untranslated_words(pairs):
    """Search for common untranslated English words."""
    print("\n" + "=" * 60)
    print("CHECK 2: Untranslated English Words")
    print("=" * 60)
    
    issues = []
    
    for _, uz_file in pairs:
        content = uz_file.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip lines that are clearly references, citations or proper nouns
            if line.strip().startswith('-') or line.strip().startswith('www'):
                continue
            if 'Diagramma' in line or 'Diagram' in line:
                continue
                
            for pattern in COMMON_ENGLISH_WORDS:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    word = match.group()
                    # Check if it's within an allowed context
                    context = line[max(0, match.start()-20):match.end()+20]
                    
                    # Skip if it's part of an allowed phrase
                    is_allowed = False
                    for allowed in ALLOWED_ENGLISH:
                        if allowed.lower() in context.lower():
                            is_allowed = True
                            break
                    
                    # Skip if in quotes (likely a proper name or title)
                    if '"' in context or "'" in context:
                        is_allowed = True
                    
                    if not is_allowed:
                        issues.append(f"  {uz_file.name}:{line_num} - Found '{word}' in: ...{context.strip()}...")
    
    if issues:
        print(f"Found {len(issues)} potential untranslated words:")
        # Show first 20 issues
        for issue in issues[:20]:
            print(issue)
        if len(issues) > 20:
            print(f"  ... and {len(issues) - 20} more")
    else:
        print("  No untranslated English words found")
    
    return issues


def check_terminology_consistency(pairs):
    """Check that chess terminology is used consistently."""
    print("\n" + "=" * 60)
    print("CHECK 3: Terminology Consistency")
    print("=" * 60)
    
    issues = []
    
    for _, uz_file in pairs:
        content = uz_file.read_text(encoding='utf-8')
        
        # Check for incorrect variants
        for variant, correction in INCORRECT_VARIANTS.items():
            # Use word boundary matching, but exclude cases where the variant
            # is part of another word (e.g., "do'kon" contains "kon")
            pattern = r'(?<![a-zA-Z\'\u2019])' + variant + r'(?![a-zA-Z\'\u2019])'
            found_matches = re.findall(pattern, content, re.IGNORECASE)
            # Filter out false positives where variant is part of compound words
            real_matches = []
            for m in re.finditer(pattern, content, re.IGNORECASE):
                # Check surrounding context for word boundaries
                start = max(0, m.start() - 5)
                end = min(len(content), m.end() + 5)
                context = content[start:end]
                # Skip if it's part of a word like "do'kon"
                if "'" in content[max(0, m.start()-3):m.start()]:
                    continue
                if "\u2019" in content[max(0, m.start()-3):m.start()]:
                    continue
                real_matches.append(m.group())
            if real_matches:
                issues.append(f"  {uz_file.name}: Found '{variant}' ({len(real_matches)} times) - {correction}")
    
    # Check correct terminology is present in relevant chapters
    piece_chapters = {
        "05_the_rook.txt": "Tura",
        "07_the_bishop.txt": "Fil",
        "09_the_queen.txt": "Farzin",
        "10_the_king.txt": "Shoh",
        "13_the_knight.txt": "Ot",
        "14_the_pawn.txt": "Piyoda",
    }
    
    for chapter, expected_term in piece_chapters.items():
        uz_file = UZ_DIR / chapter
        if uz_file.exists():
            content = uz_file.read_text(encoding='utf-8')
            count = len(re.findall(r'\b' + expected_term + r'\b', content))
            if count < 5:
                issues.append(f"  {chapter}: Expected term '{expected_term}' appears only {count} times (seems low)")
    
    if issues:
        print("Issues found:")
        for issue in issues:
            print(issue)
    else:
        print("  All terminology is consistent across chapters")
    
    return issues


def check_section_headers(pairs):
    """Check that section headers are translated consistently."""
    print("\n" + "=" * 60)
    print("CHECK 4: Section Header Consistency")
    print("=" * 60)
    
    issues = []
    header_usage = {header: [] for header in EXPECTED_HEADERS}
    
    for _, uz_file in pairs:
        content = uz_file.read_text(encoding='utf-8')
        
        for header in EXPECTED_HEADERS:
            if header in content:
                header_usage[header].append(uz_file.name)
    
    # Check for variant spellings of headers
    variant_headers = {
        "Kofe suhbati": "Should be 'Qahva suhbati'",
        "Coffee Talk": "Should be translated to 'Qahva suhbati'",
        "Coach's Corner": "Should be translated to 'Murabbiy maslahati'",
        "Troubleshooting": "Should be translated to 'Muammolar va yechimlar'",
    }
    
    for _, uz_file in pairs:
        content = uz_file.read_text(encoding='utf-8')
        for variant, correction in variant_headers.items():
            if variant in content:
                issues.append(f"  {uz_file.name}: Found '{variant}' - {correction}")
    
    print("  Header usage summary:")
    for header, files in header_usage.items():
        print(f"    '{header}': used in {len(files)} chapters")
    
    if issues:
        print("\n  Issues found:")
        for issue in issues:
            print(issue)
    else:
        print("\n  All section headers are consistent")
    
    return issues


def check_step_and_minigame_terms(pairs):
    """Check that 'Step' is translated as 'Qadam' and 'Mini-game' as 'Mini-o'yin'."""
    print("\n" + "=" * 60)
    print("CHECK 5: Step/Mini-game Terminology")
    print("=" * 60)
    
    issues = []
    qadam_count = 0
    mini_oyin_count = 0
    
    for _, uz_file in pairs:
        content = uz_file.read_text(encoding='utf-8')
        
        # Count correct usage
        qadam_count += len(re.findall(r'Qadam \d+', content))
        mini_oyin_count += len(re.findall(r"Mini-o'yin", content, re.IGNORECASE))
        
        # Check for untranslated "Step X:"
        step_matches = re.findall(r'Step \d+', content)
        if step_matches:
            issues.append(f"  {uz_file.name}: Found untranslated 'Step' ({len(step_matches)} times)")
        
        # Check for untranslated "Mini-game" (English form)
        minigame_matches = re.findall(r'Mini-game', content, re.IGNORECASE)
        if minigame_matches:
            issues.append(f"  {uz_file.name}: Found untranslated 'Mini-game' ({len(minigame_matches)} times)")
    
    print(f"  'Qadam' (Step) used: {qadam_count} times")
    print(f"  'Mini-o'yin' (Mini-game) used: {mini_oyin_count} times")
    
    if issues:
        print("\n  Issues found:")
        for issue in issues:
            print(issue)
    else:
        print("\n  All Step/Mini-game terms are properly translated")
    
    return issues


def check_diagram_references(pairs):
    """Check that diagram references are preserved."""
    print("\n" + "=" * 60)
    print("CHECK 6: Diagram References")
    print("=" * 60)
    
    issues = []
    
    for en_file, uz_file in pairs:
        en_content = en_file.read_text(encoding='utf-8')
        uz_content = uz_file.read_text(encoding='utf-8')
        
        # Count diagram references in English
        en_diagrams = re.findall(r'Diagram\s*(\d+\.\d+)', en_content)
        uz_diagrams = re.findall(r'Diagramma?\s*(\d+\.\d+)', uz_content)
        
        # Also check [Diagramma X.Y] format
        uz_diagrams_bracket = re.findall(r'\[Diagramma?\s*(\d+\.\d+)\]', uz_content)
        
        en_set = set(en_diagrams)
        uz_set = set(uz_diagrams)
        
        if en_set and not uz_set:
            issues.append(f"  {en_file.name}: English has {len(en_set)} diagram refs, Uzbek has none")
        elif en_set and len(en_set) > len(uz_set) + 2:
            missing = en_set - uz_set
            if missing:
                issues.append(f"  {en_file.name}: Missing diagrams in UZ: {sorted(missing)[:5]}")
    
    if issues:
        print("Issues found:")
        for issue in issues:
            print(issue)
    else:
        print("  All diagram references are preserved")
    
    return issues


def main():
    print("=" * 60)
    print("TRANSLATION QUALITY REVIEW - Automated Checks")
    print("Chess Is Child's Play - English to Uzbek")
    print("=" * 60)
    
    pairs = get_file_pairs()
    print(f"\nFound {len(pairs)} file pairs to review")
    
    all_issues = []
    
    all_issues.extend(check_file_sizes(pairs))
    all_issues.extend(check_untranslated_words(pairs))
    all_issues.extend(check_terminology_consistency(pairs))
    all_issues.extend(check_section_headers(pairs))
    all_issues.extend(check_step_and_minigame_terms(pairs))
    all_issues.extend(check_diagram_references(pairs))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total issues found: {len(all_issues)}")
    
    if all_issues:
        print("\nAll issues:")
        for i, issue in enumerate(all_issues, 1):
            print(f"  {i}. {issue.strip()}")
    else:
        print("No critical issues found!")
    
    return len(all_issues)


if __name__ == "__main__":
    main()
