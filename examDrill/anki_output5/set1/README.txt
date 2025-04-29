# Mechanical Engineering Exam Flashcards - AnkiApp XML Import Instructions

## XML Format Compliance

The generated XML file follows the official AnkiApp XML import format specification:
- XML schema includes the deck, fields, and cards structure required by AnkiApp
- LaTeX equations are formatted using the <tex> tags for proper rendering
- Images are included as blobs with SHA256 hash IDs as required by the specification

## Import Method

For proper import into AnkiApp:

1. Use the anki_import.zip file for import
2. In AnkiApp, select "Import" and choose the ZIP file
3. AnkiApp will automatically process the XML and included images

## Advantages of XML Import

1. Native LaTeX support: Equations are properly rendered without custom layouts
2. Proper formatting: Multiple choice options and newlines are preserved
3. No need for custom layouts: The XML structure defines the card format

## Troubleshooting

1. Verify XML structure: The XML file should be valid according to AnkiApp schema
2. Image references: Ensure image blob IDs match the SHA256 hashes in the XML
3. Format verification: Check preview.html to confirm proper LaTeX rendering and image display

