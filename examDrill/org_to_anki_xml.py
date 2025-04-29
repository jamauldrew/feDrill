#!/usr/bin/env python3
"""
Org-drill to AnkiApp XML Converter

This script converts Org-drill formatted flashcards to AnkiApp-compatible XML format
with precise implementation of AnkiApp's required schema structure and LaTeX handling.

Usage:
    python org_to_anki_xml.py input.org output_directory

Requirements:
    - Python 3.6+
    - re
    - os
    - sys
    - hashlib (for generating blob IDs)
    - shutil (for file operations)
"""

# import re
# import os
import sys
# import hashlib
# import shutil
# import zipfile
import xml.sax.saxutils as saxutils
from pathlib import Path
import os, re, shutil, zipfile
from hashlib import sha256

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

        # Extract image references - using a more comprehensive pattern
        front_images = extract_images(question)
        back_images = extract_images(answer)

        # Save original content with image references for preview
        original_question = question
        original_answer = answer

        # Process LaTeX for AnkiApp XML format
        question = process_latex_for_xml(question)
        answer = process_latex_for_xml(answer)

        # Format the card data for XML export
        card_data = {
            'id': card_num,
            'front': question,
            'back': answer,
            'tags': f"ME_Exam,Problem_{card_num}",
            'front_images': front_images,
            'back_images': back_images,
            'front_audio': "",
            'back_audio': "",
            'original_front': original_question,
            'original_back': original_answer
        }

        processed_cards.append(card_data)

    return processed_cards

def extract_images(text):
    """Extract image references from text with improved pattern matching."""
    # More flexible pattern to catch various image reference formats
    # image_pattern = r'\[\[\.?\/?(images\/)?(\d+)\.png\]\]'
    image_pattern = r'\[\[\.?\/?(images\/)?([\w-]+)\.png\]\]'
    return [match.group(2) + '.png' for match in re.finditer(image_pattern, text)]

def process_latex_for_xml(text):
    """Convert Org-mode LaTeX to AnkiApp XML-compatible format."""
    # First escape XML special characters properly
    text = saxutils.escape(text)

    # Handle multiple choice options formatting with proper XML structure
    # Convert (A), (B), etc. in LaTeX to proper formatting
    text = re.sub(r'\\[(]([A-D])\\[)]', r'<b>\1</b>', text)

    # Convert $A$, $B$, etc. to proper formatting
    text = re.sub(r'\$([A-D])\$', r'<b>\1</b>', text)

    # Convert inline LaTeX: \(...\) to proper XML LaTeX format
    text = re.sub(r'\\[(](.*?)\\[)]', r'<tex>\1</tex>', text)

    # Convert $...$ to proper XML LaTeX format
    text = re.sub(r'\$(.*?)\$', r'<tex>\1</tex>', text)

    # Handle emphasized variables with proper XML formatting
    text = re.sub(r'\*([a-zA-Z0-9]+)\*', r'<b>\1</b>', text)

    # Preserve newlines as <br/> tags (self-closing XML tags) for proper display
    text = text.replace('\n\n', '<br></br><br></br>')
    text = text.replace('\n', '<br></br>')

    # Handle image references for XML format - preserve image filenames
    text = re.sub(r'\[\[\.?\/?(images\/)?(\d+)\.png\]\]', r'<img id="\2.png" />', text)

    return text

def calculate_sha256(path):
    """Calculate SHA256 hash in base16 (hexadecimal) format as required by AnkiApp."""
    h = sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()  # Ensure we return the hexadecimal representation

def create_anki_xml(cards, output_dir):
    """Create AnkiApp-compatible XML with diagnostic test elements."""
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    xml_path = os.path.join(output_dir, 'anki_import.xml')
    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<deck name="Mechanical Engineering Exam" tags="ME_Exam,EIT">\n')

        # Define fields structure
        f.write('  <fields>\n')
        f.write('    <rich-text lang="en-US" name="Front" sides="11"></rich-text>\n')
        f.write('    <rich-text lang="en-US" name="Back" sides="01"></rich-text>\n')
        f.write('  </fields>\n')

        # Add a test card with basic image (for diagnostic purposes)
        f.write('  <cards>\n')

        # Add diagnostic test card
        f.write('    <card tags="TEST">\n')
        f.write('      <rich-text name="Front">This is a test card with hardcoded image reference</rich-text>\n')
        f.write('      <rich-text name="Back">The image should appear below if the format is correct:<br></br><img id="TEST_HASH" /></rich-text>\n')
        f.write('    </card>\n')

        # Add regular cards
        for card in cards:
            f.write(f'    <card tags="{card["tags"]}">\n')
            f.write(f'      <rich-text name="Front">{card["front"]}</rich-text>\n')
            f.write(f'      <rich-text name="Back">{card["back"]}</rich-text>\n')
            f.write(f'    </card>\n')

        f.write('  </cards>\n')
        f.write('</deck>\n')

    return xml_path

def process_images_for_anki(cards, source_image_dir, output_dir):
    """Process images with multiple storage strategies to ensure compatibility."""
    blobs_dir = os.path.join(output_dir, 'blobs')
    os.makedirs(blobs_dir, exist_ok=True)

    image_reference_map = {}
    all_images = set()
    for card in cards:
        all_images.update(card.get('front_images', []))
        all_images.update(card.get('back_images', []))

    print(f"Processing {len(all_images)} unique binary assets for blob storage")

    for image_filename in all_images:
        source_path = os.path.join(source_image_dir, image_filename)

        if os.path.exists(source_path):
            # Calculate SHA256 hash in hexadecimal format
            binary_hash = calculate_sha256(source_path)
            file_ext = os.path.splitext(image_filename)[1]  # Get the file extension

            # Store with multiple strategies to ensure one works:

            # 1. Store with original filename (for backward compatibility)
            shutil.copy(source_path, os.path.join(blobs_dir, image_filename))

            # 2. Store with hash as filename without extension
            shutil.copy(source_path, os.path.join(blobs_dir, binary_hash))

            # 3. Store with hash as filename with extension
            shutil.copy(source_path, os.path.join(blobs_dir, binary_hash + file_ext))

            # Create reference mapping
            image_base = os.path.splitext(image_filename)[0]
            image_reference_map[image_base] = {
                'original_filename': image_filename,
                'hash_id': binary_hash,
                'file_extension': file_ext
            }
        else:
            print(f"Warning: {image_filename} not found")

    print(f"Completed blob processing: {len(image_reference_map)} unique assets stored with multiple filename strategies")

    return image_reference_map

def update_xml_with_blob_references(xml_path, image_reference_map):
    """Update XML with precise AnkiApp-compliant image references."""
    with open(xml_path, 'r', encoding='utf-8') as f:
        xml_content = f.read()

    for image_base in image_reference_map:
        reference_info = image_reference_map[image_base]

        # Match the exact format from AnkiApp docs: <img id="{SHA_256 hash of file}" />
        old_tag = f'<img id="{image_base}.png" />'
        new_tag = f'<img id="{reference_info["hash_id"]}" />'

        xml_content = xml_content.replace(old_tag, new_tag)

    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(xml_content)

    return xml_content

def create_anki_zip_with_verification(xml_path, blobs_dir, output_dir):
    """Create AnkiApp-compatible ZIP with precise directory structure."""
    zip_path = os.path.join(output_dir, 'anki_import.zip')

    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        # Add XML directly to root
        zip_file.write(xml_path, os.path.basename(xml_path))

        # Create blobs directory in the ZIP
        for blob_filename in os.listdir(blobs_dir):
            blob_path = os.path.join(blobs_dir, blob_filename)
            if os.path.isfile(blob_path):
                # Store with path "blobs/filename" - ensure this exact structure
                zip_file.write(blob_path, os.path.join('blobs', blob_filename))

    # Verify the structure
    with zipfile.ZipFile(zip_path, 'r') as verify_zip:
        files = verify_zip.namelist()
        print("ZIP file structure verification:")
        print(f"- XML file in root: {os.path.basename(xml_path) in files}")
        print(f"- 'blobs/' directory present: {any(f.startswith('blobs/') for f in files)}")
        print(f"- Number of files in blobs: {sum(1 for f in files if f.startswith('blobs/'))}")

    return zip_path

# def main_processing_workflow(input_file, output_dir):
#     """
#     Integrated workflow for AnkiApp-compatible conversion with technical precision.
#     """
#     # Extract cards from org file
#     with open(input_file, 'r', encoding='utf-8') as f:
#         org_content = f.read()

#     cards = extract_drill_cards(org_content)
#     print(f"Extracted {len(cards)} engineering problem cards for conversion")

#     # Determine source image directory
#     source_image_dir = os.path.join(os.path.dirname(input_file), "images")
#     if not os.path.exists(source_image_dir):
#         print(f"ERROR: Source image directory not found: {source_image_dir}")
#         return

#     # Create XML with proper card structure
#     xml_path = create_anki_xml(cards, output_dir)
#     print(f"Created AnkiApp schema XML: {xml_path}")

#     # Process images with blob protocol
#     image_reference_map = process_images_for_anki(cards, source_image_dir, output_dir)

#     # Update XML with hash-based blob references
#     update_xml_with_blob_references(xml_path, image_reference_map)

#     # Create ZIP with verification
#     blobs_dir = os.path.join(output_dir, 'blobs')
#     zip_path = create_anki_zip_with_verification(xml_path, blobs_dir, output_dir)

#     print(f"Conversion complete: {zip_path}")
#     print(f"Technical verification complete - binary asset reference integrity confirmed")

def create_html_preview(cards, output_dir, image_id_map=None):
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
        .option { font-weight: bold; }
        .image-placeholder { color: #cc0000; font-style: italic; padding: 5px; border: 1px dashed #cc0000; display: inline-block; }
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
            # We'll use the original content for the preview to better preserve formatting
            front = card['original_front']
            back = card['original_back']

            # Process for preview - replace image references
            for img in card['front_images']:
                img_num = img.split('.')[0]
                img_tag = f'<img src="preview_images/{img}" alt="Question diagram">'
                front = re.sub(r'\[\[\.?\/?(images\/)?{}\.png\]\]'.format(img_num), img_tag, front)

            for img in card['back_images']:
                img_num = img.split('.')[0]
                img_tag = f'<img src="preview_images/{img}" alt="Solution diagram">'
                back = re.sub(r'\[\[\.?\/?(images\/)?{}\.png\]\]'.format(img_num), img_tag, back)

            # Handle LaTeX for preview
            front = re.sub(r'\\[(](.*?)\\[)]', r'\\(\1\\)', front)
            back = re.sub(r'\\[(](.*?)\\[)]', r'\\(\1\\)', back)

            # Format paragraphs
            front = front.replace('\n\n', '<br><br>')
            back = back.replace('\n\n', '<br><br>')

            # Write card to HTML
            f.write(f'<div class="card">')
            f.write(f'<div class="card-header"><h3>Problem {card["id"]}</h3></div>')
            f.write(f'<div class="question"><strong>Question:</strong><br>{front}</div><hr>')
            f.write(f'<div class="answer"><strong>Solution:</strong><br>{back}</div>')
            f.write('</div>')

        f.write('</body></html>')

    return preview_path, preview_images_dir

def copy_images_for_preview(cards, source_image_dir, preview_images_dir):
    """Copy images for HTML preview with proper path handling."""
    copied_images = set()
    missing_images = set()

    for card in cards:
        # Process all front images
        for img in card['front_images']:
            source_path = os.path.join(source_image_dir, img)
            if os.path.exists(source_path):
                target_path = os.path.join(preview_images_dir, img)
                shutil.copy(source_path, target_path)
                copied_images.add(img)
            else:
                missing_images.add(img)

        # Process all back images
        for img in card['back_images']:
            source_path = os.path.join(source_image_dir, img)
            if os.path.exists(source_path):
                target_path = os.path.join(preview_images_dir, img)
                shutil.copy(source_path, target_path)
                copied_images.add(img)
            else:
                missing_images.add(img)

    return copied_images, missing_images

def create_instructions(output_dir):
    """Create comprehensive instructions file for using the XML import."""
    instructions_path = os.path.join(output_dir, 'README.txt')
    with open(instructions_path, 'w', encoding='utf-8') as f:
        f.write('# Mechanical Engineering Exam Flashcards - AnkiApp XML Import Instructions\n\n')

        f.write('## XML Format Compliance\n\n')
        f.write('The generated XML file follows the official AnkiApp XML import format specification:\n')
        f.write('- XML schema includes the deck, fields, and cards structure required by AnkiApp\n')
        f.write('- LaTeX equations are formatted using the <tex> tags for proper rendering\n')
        f.write('- Images are included as blobs with SHA256 hash IDs as required by the specification\n\n')

        f.write('## Import Method\n\n')
        f.write('For proper import into AnkiApp:\n\n')
        f.write('1. Use the anki_import.zip file for import\n')
        f.write('2. In AnkiApp, select "Import" and choose the ZIP file\n')
        f.write('3. AnkiApp will automatically process the XML and included images\n\n')

        f.write('## Advantages of XML Import\n\n')
        f.write('1. Native LaTeX support: Equations are properly rendered without custom layouts\n')
        f.write('2. Proper formatting: Multiple choice options and newlines are preserved\n')
        f.write('3. No need for custom layouts: The XML structure defines the card format\n\n')

        f.write('## Troubleshooting\n\n')
        f.write('1. Verify XML structure: The XML file should be valid according to AnkiApp schema\n')
        f.write('2. Image references: Ensure image blob IDs match the SHA256 hashes in the XML\n')
        f.write('3. Format verification: Check preview.html to confirm proper LaTeX rendering and image display\n\n')

def create_image_report(output_dir, copied_images, missing_images):
    """Create a report of image processing results."""
    report_path = os.path.join(output_dir, 'image_report.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('# Image Processing Report\n\n')

        f.write('## Successfully Processed Images\n\n')
        if copied_images:
            for img in sorted(copied_images):
                f.write(f'- {img}\n')
        else:
            f.write('No images were successfully processed.\n')

        f.write('\n## Missing Images\n\n')
        if missing_images:
            f.write('The following image references were found but the image files were not located:\n\n')
            for img in sorted(missing_images):
                f.write(f'- {img}\n')
        else:
            f.write('All referenced images were found and processed successfully.\n')

        f.write('\n## Troubleshooting\n\n')
        f.write('If images are missing:\n')
        f.write('1. Ensure the "images" directory is in the same location as the source org file\n')
        f.write('2. Check that image filenames match the references in the org file\n')
        f.write('3. For missing images in the preview, check the image_report.txt file\n')

def validate_xml(xml_path):
    """Validate the XML file against XML syntax rules."""
    # Simple validation - doesn't check against schema but ensures well-formed XML
    try:
        from xml.etree import ElementTree
        ElementTree.parse(xml_path)
        return True, "XML is well-formed"
    except Exception as e:
        return False, str(e)

def main():
    """Main function implementing the conversion workflow with robust error handling."""
    if len(sys.argv) != 3:
        print("Usage: python org_to_anki_xml.py input.org output_directory")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    try:
        print("=== Engineering Flashcard XML Conversion Process ===")

        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Read input file
        print(f"Reading source file: {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            org_content = f.read()

        # Extract cards
        print("Extracting and processing flashcards...")
        cards = extract_drill_cards(org_content)
        print(f"Successfully extracted {len(cards)} engineering problem cards")

        # Determine if we have images
        has_images = any(card['front_images'] or card['back_images'] for card in cards)

        # Create XML file - ensure directory exists
        print("Generating AnkiApp-compatible XML...")
        xml_path = create_anki_xml(cards, output_dir)

        # Validate XML
        is_valid, message = validate_xml(xml_path)
        if is_valid:
            print(f"XML file created and validated: {xml_path}")
        else:
            print(f"WARNING: XML file created but validation failed: {message}")

        # Handle images if present
        source_image_dir = os.path.join(os.path.dirname(input_file), "images")
        copied_images = set()
        missing_images = set()

        if has_images:
            print(f"Looking for engineering diagrams in {source_image_dir}")

            if os.path.exists(source_image_dir):
                print(f"Processing engineering diagrams with enhanced blob protocol...")

                # Implement enhanced binary asset processing
                image_reference_map = process_images_for_anki(cards, source_image_dir, output_dir)

                # Update XML with correct hash-based references
                update_xml_with_blob_references(xml_path, image_reference_map)

                # Create technically verified ZIP archive
                blobs_dir = os.path.join(output_dir, 'blobs')
                zip_path = create_anki_zip_with_verification(xml_path, blobs_dir, output_dir)

                print(f"ZIP archive created with technical verification: {zip_path}")

                # Create HTML preview with resolved image references
                preview_path, preview_images_dir = create_html_preview(cards, output_dir)
                copied_images, missing_images = copy_images_for_preview(cards, source_image_dir, preview_images_dir)
                print(f"HTML preview created: {preview_path}")
            else:
                print(f"WARNING: Image directory not found at {source_image_dir}")
                preview_path, _ = create_html_preview(cards, output_dir)
        else:
            print("No image references found in the cards")
            preview_path, _ = create_html_preview(cards, output_dir)
            print(f"Text-only HTML preview created: {preview_path}")

        # Create instructions and reports
        create_instructions(output_dir)
        if has_images:
            create_image_report(output_dir, copied_images, missing_images)

        print("\n=== Conversion Complete ===")
        print(f"Output files available in: {output_dir}")

    except Exception as e:
        print(f"Error processing engineering content: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
