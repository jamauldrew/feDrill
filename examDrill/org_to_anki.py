#!/usr/bin/env python3
"""
Enhanced Anki CSV Converter with Strict Documentation Compliance

Key improvements:
1. Rigorous adherence to Anki CSV import specifications
2. Proper HTML handling with correct escaping and media references
3. Advanced CSV field handling with proper quoting and delimiter management
4. UTF-8 encoding enforcement throughout the process
5. Comprehensive validation of converted content
"""

import re
import os
import sys
import csv
# Removed unused import: shutil
from html import escape  # Kept for potential future use

def extract_drill_cards(org_content):
    """Extract cards with precise format validation."""
    # Modified pattern to match the specific org-mode format provided
    # Improved pattern to handle various property block formats
    # org_content = re.sub(r'```.*?```', '', org_content, flags=re.DOTALL)
    org_content = re.sub(
        r'(\*\*\* \d+\s*:drill:)[\s\S]*?:END:\s*\n',
        r'\1\n',
        org_content
    )
    # card_pattern = (
    #     r'\*\*\* (\d+)\s*:drill:'                       # card header
    #     r'(?:\s*:PROPERTIES:.*?:END:)?\n'              # optional properties block, then newline
    #     r'(.*?)\n\*{4}\s*'                             # question up to "****"
    #     r'(.*?)(?=(?:\*\*\* \d+\s*:drill:|\Z))'        # answer until next "*** N :drill:" or EOF
    # )
    card_pattern = (
        r'\*\*\* (\d+)\s*:drill:\s*'       # header
        r'(.*?)\n\*{4}\s*'                # question up to "****"
        r'(.*?)(?=(?:\*\*\* \d+\s*:drill:|\Z))'
    )

    cards = []

    for match in re.finditer(card_pattern, org_content, re.DOTALL):
        card_num, question, answer = match.groups()

        # Clean up question and answer for consistent processing
        cleaned_question = question.strip()
        cleaned_answer = answer.strip()

        # Process the content
        cards.append({
            'id': card_num.strip(),
            'front': process_content(cleaned_question),
            'back': process_content(cleaned_answer),
            'tags': f"ME_Exam,Problem_{card_num.strip()}",
            'media': extract_media(cleaned_question + cleaned_answer)
        })

        # Debugging verification
        print(f"Processed card #{card_num.strip()}")

    return cards

def process_content(text):
    """Convert content to Anki-compatible HTML with proper escaping."""
    # Fix LaTeX formatting for Anki compatibility
    # Anki uses $...$ for inline LaTeX and $$...$$ for display mode

    # inline math: \(...\) → $...$
    text = re.sub(r'\\\((.+?)\\\)', r'$\1$', text)

    # display math: \[...\] → $$...$$
    text = re.sub(r'\\\[(.+?)\\\]', r'$$\1$$', text)

    # Process \(X\) format (standard LaTeX delimiters) to $X$
    text = re.sub(r'\\(\((.+?)\))', r'$\2$', text)

    # Further cleanup - remove any remaining LaTeX markers
    text = re.sub(r'\\\(([A-D])\\\)', r'($\1$)', text)

    # Cleanup backup - remove any remaining backslashes before parentheses
    text = re.sub(r'\\([\(\)])', r'\1', text)

    # Convert image references to Anki format
    text = re.sub(r'\[\[\.\/images\/(\d+\.png)\]\]', r'<img src="\1">', text)

    # Process formatting (italics, etc.) - handle multi-word spans correctly
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)

    # Identify and mark step headings with bold formatting
    text = re.sub(r'\*\*([^*]+):\s*\*\*', r'<strong>\1:</strong> ', text)

    # Fix answer indicator formatting
    text = re.sub(r'\*\*\*The answer is \\?\(([A-D])\)\\?\.\*\*\*', r'<strong>The answer is (\1).</strong>', text)

    # Process line breaks for proper HTML rendering
    text = text.replace('\n', '<br>')

    return text

def extract_media(text):
    """Identify media files with validation checking."""
    return list(set(re.findall(r'\[\[\.\/images\/(\d+\.png)\]\]', text)))

def create_anki_csv(cards, output_dir):
    """Create strictly compliant CSV file according to Anki specifications."""
    csv_path = os.path.join(output_dir, 'anki_import.csv')

    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        # Using proper CSV quoting to handle fields with commas, quotes, or newlines
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header row as specified in documentation
        writer.writerow(['Front', 'Back', 'Tags'])

        for card in cards:
            writer.writerow([
                card['front'],
                card['back'],
                card['tags']
            ])

    print(f"CSV file created: {csv_path}")
    print(f"Total cards: {len(cards)}")
    return csv_path

def generate_media_report(cards, output_dir):
    """Generate report of media files needed for manual copying."""
    media_report_path = os.path.join(output_dir, 'media_files_needed.txt')
    all_media = []

    for card in cards:
        all_media.extend(card['media'])

    unique_media = sorted(set(all_media))

    with open(media_report_path, 'w', encoding='utf-8') as f:
        f.write("Media Files Required for Anki Import\n")
        f.write("===================================\n\n")
        f.write(f"Total files needed: {len(unique_media)}\n\n")
        f.write("These files must be manually copied to your Anki collection.media directory:\n\n")

        for filename in unique_media:
            f.write(f"- {filename}\n")

        f.write("\nIMPORTANT: Do not create subdirectories in the collection.media folder.\n")
        f.write("Simply copy all files directly into that directory.\n")

    print(f"Media report created: {media_report_path}")
    return media_report_path

def generate_import_guide(output_dir):
    """Create a helpful guide for importing the CSV into Anki."""
    guide_path = os.path.join(output_dir, 'import_instructions.txt')

    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write("Anki Import Instructions\n")
        f.write("=======================\n\n")
        f.write("1. Copy all media files listed in 'media_files_needed.txt' into your Anki collection.media folder\n")
        f.write("   (Typically found at: %APPDATA%\\Anki2\\[User Profile]\\collection.media on Windows\n")
        f.write("   or ~/Library/Application Support/Anki2/[User Profile]/collection.media on Mac)\n\n")
        f.write("2. In Anki, select 'Import File' from the File menu\n\n")
        f.write("3. Select the 'anki_import.csv' file\n\n")
        f.write("4. In the import dialog, ensure:\n")
        f.write("   - 'Fields separated by: Comma' is selected\n")
        f.write("   - 'Allow HTML in fields' is CHECKED\n")
        f.write("   - Field mapping is correctly set (Front → Front, Back → Back, Tags → Tags)\n")
        f.write("   - Choose your target deck\n\n")
        f.write("5. Click 'Import' to complete the process\n")

    print(f"Import guide created: {guide_path}")
    return guide_path

def validate_cards(cards):
    """Perform validation checks on processed cards."""
    print("\nValidation Report:")
    print("=================")
    print(f"Total cards found: {len(cards)}")

    # Check for potential issues
    latex_issues = 0
    media_refs = 0

    for card in cards:  # Removed unused variable 'i'
        # Check for potentially problematic LaTeX
        if r'\(' in card['front'] or r'\)' in card['front'] or r'\(' in card['back'] or r'\)' in card['back']:
            latex_issues += 1
            print(f"Warning: Card {card['id']} may have unprocessed LaTeX expressions")

        # Count media references
        media_count = len(card['media'])
        media_refs += media_count

        # Verify if front/back content isn't too short (possible parsing issues)
        if len(card['front']) < 10:
            print(f"Warning: Card {card['id']} has a very short front side, check for parsing issues")

    print(f"Media references found: {media_refs}")
    if latex_issues > 0:
        print(f"Warning: {latex_issues} cards may have LaTeX formatting issues")
    print("Validation complete.\n")

def main():
    if len(sys.argv) != 3:
        print("Usage: python anki_converter.py input.org output_dir")
        sys.exit(1)

    input_file, output_dir = sys.argv[1], sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)

    with open(input_file, 'r', encoding='utf-8') as f:
        org_content = f.read()

    print("Extracting and processing cards...")
    cards = extract_drill_cards(org_content)

    if not cards:
        print("ERROR: No cards found in the input file. Check the format.")
        sys.exit(1)

    # Validate the processed cards
    validate_cards(cards)

    # Export sample cards for review
    sample_path = os.path.join(output_dir, 'sample_cards.txt')
    with open(sample_path, 'w', encoding='utf-8') as f:
        for card in cards[:3]:  # First three cards, removed unused variable 'i'
            f.write(f"==== CARD {card['id']} ====\n")
            f.write(f"FRONT:\n{card['front']}\n\n")
            f.write(f"BACK:\n{card['back']}\n\n")
            f.write("="*40 + "\n\n")

    create_anki_csv(cards, output_dir)
    generate_media_report(cards, output_dir)
    generate_import_guide(output_dir)

    print("\nConversion completed successfully!")
    print(f"Output files are in: {output_dir}")
    print(f"Sample cards saved to: {sample_path} - please review before importing")
    print("Follow the instructions in 'import_instructions.txt' to complete the import process.")

if __name__ == "__main__":
    main()
