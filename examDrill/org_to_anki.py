#!/usr/bin/env python3
"""
Optimized Org-drill to AnkiApp CSV Converter

This script converts Org-drill formatted flashcards to AnkiApp-compatible CSV format
with precise implementation of AnkiApp's required column structure and media handling.

Usage:
    python org_to_anki_csv.py input.org output_directory

Requirements:
    - Python 3.6+
    - re
    - os
    - sys
    - csv
    - shutil (for file operations)
"""

import re
import os
import sys
import csv
import shutil
import zipfile
from pathlib import Path

def extract_drill_cards(org_content):
    """Extract individual drill cards from org file with engineering precision."""
    # Pattern to capture the structure of engineering exam questions
    drill_pattern = r'(?:\*+\s+(?:TODO\s+)?(\d+).*?:drill:.*?(?=\*+\s+(?:TODO\s+)?\d+.*?:drill:|$))'

    # Process each card
    processed_cards = []
    for card_match in re.finditer(drill_pattern, org_content, re.DOTALL):
        card_text = card_match.group(0)

        # Extract card number with robust error handling
        card_num_match = re.search(r'\*+\s+(?:TODO\s+)?(\d+)', card_text)
        card_num = card_num_match.group(1) if card_num_match else "unknown"

        # Split into question and answer
        parts = card_text.split('****', 1)
        if len(parts) < 2:
            continue

        question = parts[0]
        answer = parts[1]

        # Extract question content - remove headers and properties
        question = re.sub(r'\*+\s+(?:TODO\s+)?\d+.*?:drill:.*?:END:', '', question, flags=re.DOTALL)
        question = question.strip()

        # Clean up answer
        answer = answer.strip()

        # Extract image references before processing text
        front_images = extract_images(question)
        back_images = extract_images(answer)

        # Process LaTeX - OPTIMIZED FOR ANKIAPP
        question = process_latex(question)
        answer = process_latex(answer)

        # Remove image references from text since they'll be in separate columns
        question = remove_image_references(question)
        answer = remove_image_references(answer)

        # Format the card data according to AnkiApp's expected structure
        card_data = {
            'id': card_num,
            'front': question,
            'back': answer,
            'tags': f"ME_Exam,Problem_{card_num}",
            'front_image': front_images[0] if front_images else "",
            'back_image': back_images[0] if back_images else "",
            'front_audio': "",
            'back_audio': ""
        }

        processed_cards.append(card_data)

    return processed_cards

def extract_images(text):
    """Extract image references from text with precise pattern matching."""
    image_pattern = r'\[\[\.\/images\/(\d+)\.png\]\]'
    return [match.group(1) + '.png' for match in re.finditer(image_pattern, text)]

def remove_image_references(text):
    """Remove image references from text for clean card content."""
    return re.sub(r'\[\[\.\/images\/\d+\.png\]\]', '', text)

def process_latex(text):
    """Convert Org-mode LaTeX to AnkiApp compatible format with engineering precision."""
    # Convert inline LaTeX: \(...\) to $...$ (standard LaTeX delimiters)
    text = re.sub(r'\\[(](.*?)\\[)]', r'$\1$', text)

    # Handle emphasized variables with proper HTML formatting
    text = re.sub(r'\*([a-zA-Z0-9]+)\*', r'<em>\1</em>', text)

    return text

def create_anki_csv(cards, output_dir):
    """Create AnkiApp-compatible CSV file with precise column structure."""
    os.makedirs(output_dir, exist_ok=True)

    # Create CSV file with AnkiApp's expected column structure
    csv_path = os.path.join(output_dir, 'anki_import.csv')
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)

        # Write each card as a row in the CSV
        for card in cards:
            writer.writerow([
                card['front'],          # Column 1: Front text
                card['back'],           # Column 2: Back text
                card['tags'],           # Column 3: Tags
                card['front_image'],    # Column 4: Front image filename
                card['back_image'],     # Column 5: Back image filename
                card['front_audio'],    # Column 6: Front audio filename
                card['back_audio']      # Column 7: Back audio filename
            ])

    return csv_path

def create_anki_zip(csv_path, cards, output_dir, source_image_dir):
    """Create a properly structured ZIP file for AnkiApp import with comprehensive image support."""
    # Define zip file path
    zip_path = os.path.join(output_dir, 'anki_import.zip')

    # Create ZIP file
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        # Add the CSV file with a relative path
        zip_file.write(csv_path, os.path.basename(csv_path))

        # Add all referenced images
        for card in cards:
            # Process front image
            if card['front_image']:
                source_path = os.path.join(source_image_dir, card['front_image'])
                if os.path.exists(source_path):
                    zip_file.write(source_path, card['front_image'])

            # Process back image
            if card['back_image']:
                source_path = os.path.join(source_image_dir, card['back_image'])
                if os.path.exists(source_path):
                    zip_file.write(source_path, card['back_image'])

    return zip_path

def create_html_preview(cards, output_dir):
    """Create HTML preview for verification with proper LaTeX rendering."""
    preview_path = os.path.join(output_dir, 'preview.html')
    with open(preview_path, 'w', encoding='utf-8') as f:
        f.write('''<!DOCTYPE html>
<html>
<head>
    <title>Engineering Exam Cards Preview</title>
    <style>
        body { font-family: 'Helvetica', sans-serif; margin: 20px; background: #f5f5f5; }
        .card { border: 1px solid #ccc; margin: 15px 0; padding: 15px; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card-header { background: #2c3e50; color: white; padding: 10px; margin: -15px -15px 15px; }
        .question { margin-bottom: 20px; }
        .answer { background: #f9f9f9; padding: 15px; border-left: 4px solid #2980b9; }
        img { max-width: 100%; border: 1px solid #ddd; }
        hr { border: 0; height: 1px; background: #ddd; margin: 20px 0; }
    </style>
    <script type="text/x-mathjax-config">
        MathJax.Hub.Config({
            tex2jax: {inlineMath: [['$','$'], ['\\\\(','\\\\)']]}
        });
    </script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS_HTML"></script>
</head>
<body>
    <h1>Mechanical Engineering Exam Flashcards</h1>
    <p>Preview of converted flashcards with LaTeX equations and technical diagrams</p>
''')

        # Create a directory to store images for preview
        preview_images_dir = os.path.join(output_dir, 'preview_images')
        os.makedirs(preview_images_dir, exist_ok=True)

        for card in cards:
            f.write(f'<div class="card">')
            f.write(f'<div class="card-header"><h3>Problem {card["id"]}</h3></div>')

            # Question section
            f.write(f'<div class="question"><strong>Question:</strong><br>{card["front"]}')

            # Include front image if available
            if card['front_image']:
                image_path = f'preview_images/{card["front_image"]}'
                f.write(f'<div><img src="{image_path}" alt="Question diagram"></div>')

            f.write('</div><hr>')

            # Answer section
            f.write(f'<div class="answer"><strong>Solution:</strong><br>{card["back"]}')

            # Include back image if available
            if card['back_image']:
                image_path = f'preview_images/{card["back_image"]}'
                f.write(f'<div><img src="{image_path}" alt="Solution diagram"></div>')

            f.write('</div></div>')

        f.write('</body></html>')

    return preview_path, preview_images_dir

def copy_images_for_preview(cards, source_image_dir, preview_images_dir):
    """Copy images for HTML preview with proper path handling."""
    for card in cards:
        # Copy front image if available
        if card['front_image']:
            source_path = os.path.join(source_image_dir, card['front_image'])
            if os.path.exists(source_path):
                shutil.copy(source_path, os.path.join(preview_images_dir, card['front_image']))

        # Copy back image if available
        if card['back_image']:
            source_path = os.path.join(source_image_dir, card['back_image'])
            if os.path.exists(source_path):
                shutil.copy(source_path, os.path.join(preview_images_dir, card['back_image']))

def create_instructions(output_dir, has_images):
    """Create comprehensive instructions file with technical precision."""
    instructions_path = os.path.join(output_dir, 'README.txt')
    with open(instructions_path, 'w', encoding='utf-8') as f:
        f.write('# Mechanical Engineering Exam Flashcards - AnkiApp Import Instructions\n\n')

        f.write('## CSV Format Compliance\n\n')
        f.write('The generated CSV file follows the official AnkiApp import format specification:\n')
        f.write('1. Column 1: Text for front of card\n')
        f.write('2. Column 2: Text for back of card\n')
        f.write('3. Column 3: List of tags, comma separated\n')
        f.write('4. Column 4: Filename for image on front of card\n')
        f.write('5. Column 5: Filename for image on back of card\n')
        f.write('6. Column 6: File name of audio file for front of card (not used)\n')
        f.write('7. Column 7: File name of audio file for back of card (not used)\n\n')

        f.write('## Import Method for Cards with Images\n\n')
        if has_images:
            f.write('This deck includes image references. For proper import:\n\n')
            f.write('1. Use the anki_import.zip file for import\n')
            f.write('2. In AnkiApp, select "Import" and choose the ZIP file\n')
            f.write('3. AnkiApp will automatically process both the CSV and included images\n\n')
        else:
            f.write('This deck does not contain image references. You can import the CSV file directly.\n\n')

        f.write('## Troubleshooting\n\n')
        f.write('1. Verify ZIP structure: The ZIP file must contain the CSV and image files at the root level\n')
        f.write('2. Image references: Ensure image filenames in the CSV match exactly the image files in the ZIP\n')
        f.write('3. Format verification: Check preview.html to confirm proper LaTeX rendering and image display\n\n')

        f.write('## Technical Notes\n\n')
        f.write('- LaTeX equations use standard $...$ delimiters compatible with AnkiApp\n')
        f.write('- Emphasized variables use HTML <em> tags for consistent rendering\n')
        f.write('- Image references are placed in dedicated columns as per AnkiApp specifications\n')

def main():
    """Main function implementing the conversion workflow with robust error handling."""
    if len(sys.argv) != 3:
        print("Usage: python org_to_anki_csv.py input.org output_directory")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    try:
        print("=== Engineering Flashcard Conversion Process ===")

        # Read input file
        print(f"Reading source file: {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            org_content = f.read()

        # Extract cards
        print("Extracting and processing flashcards...")
        cards = extract_drill_cards(org_content)
        print(f"Successfully extracted {len(cards)} engineering problem cards")

        # Determine if we have images
        has_images = any(card['front_image'] or card['back_image'] for card in cards)

        # Create CSV file
        print("Generating AnkiApp-compatible CSV...")
        csv_path = create_anki_csv(cards, output_dir)
        print(f"CSV file created: {csv_path}")

        # Handle images if present
        source_image_dir = os.path.join(os.path.dirname(input_file), "images")
        if has_images and os.path.exists(source_image_dir):
            print(f"Processing engineering diagrams from {source_image_dir}")

            # Create ZIP file with images
            zip_path = create_anki_zip(csv_path, cards, output_dir, source_image_dir)
            print(f"ZIP archive created with CSV and images: {zip_path}")

            # Create HTML preview
            preview_path, preview_images_dir = create_html_preview(cards, output_dir)
            copy_images_for_preview(cards, source_image_dir, preview_images_dir)
            print(f"HTML preview created: {preview_path}")
        else:
            print("No images found or source image directory does not exist")
            preview_path, _ = create_html_preview(cards, output_dir)
            print(f"Text-only HTML preview created: {preview_path}")

        # Create instructions
        create_instructions(output_dir, has_images)
        print(f"Comprehensive instructions created: {os.path.join(output_dir, 'README.txt')}")

        print("\n=== Conversion Complete ===")
        print(f"Output files available in: {output_dir}")
        if has_images:
            print(f"For import to AnkiApp: Use the ZIP file {os.path.join(output_dir, 'anki_import.zip')}")
        else:
            print(f"For import to AnkiApp: Use the CSV file {csv_path}")
        print("Verify output formatting in preview.html before importing")

    except Exception as e:
        print(f"Error processing engineering content: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
