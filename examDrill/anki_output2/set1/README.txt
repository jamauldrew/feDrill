# Mechanical Engineering Exam Flashcards - AnkiApp Import Instructions

## CSV Format Compliance

The generated CSV file follows the official AnkiApp import format specification:
1. Column 1: Text for front of card
2. Column 2: Text for back of card
3. Column 3: List of tags, comma separated
4. Column 4: Filename for image on front of card
5. Column 5: Filename for image on back of card
6. Column 6: File name of audio file for front of card (not used)
7. Column 7: File name of audio file for back of card (not used)

## Import Method for Cards with Images

This deck includes image references. For proper import:

1. Use the anki_import.zip file for import
2. In AnkiApp, select "Import" and choose the ZIP file
3. AnkiApp will automatically process both the CSV and included images

## Troubleshooting

1. Verify ZIP structure: The ZIP file must contain the CSV and image files at the root level
2. Image references: Ensure image filenames in the CSV match exactly the image files in the ZIP
3. Format verification: Check preview.html to confirm proper LaTeX rendering and image display

## Technical Notes

- LaTeX equations use standard $...$ delimiters compatible with AnkiApp
- Emphasized variables use HTML <em> tags for consistent rendering
- Image references are placed in dedicated columns as per AnkiApp specifications
