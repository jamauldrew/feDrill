#!/bin/bash

# Define the target colors
TARGET_FOREGROUND_COLOR="#bbc2cf"
TARGET_BACKGROUND_COLOR="#282c34"

# Define the original colors
ORIGINAL_FOREGROUND_COLOR="#000000"
ORIGINAL_BACKGROUND_COLOR="#ffffff"

# Define the directory containing the images
IMAGE_DIR="./images"

# Process each PNG image in the directory
for image in "$IMAGE_DIR"/*.png; do
    # Create a temporary image for processing
    temp_image="${image%.png}_temp.png"
    
    # Convert the foreground and background colors
    convert "$image" -fuzz 20% -fill "$TARGET_FOREGROUND_COLOR" -opaque "$ORIGINAL_FOREGROUND_COLOR" "$temp_image"
    convert "$temp_image" -fuzz 20% -fill "$TARGET_BACKGROUND_COLOR" -opaque "$ORIGINAL_BACKGROUND_COLOR" "${image%.png}_colored.png"
    
    # Remove the temporary image
    rm "$temp_image"
    
    # Optionally, replace the original image with the colored one
    mv "${image%.png}_colored.png" "$image"
done

echo "Images have been updated to the target colors: foreground $TARGET_FOREGROUND_COLOR and background $TARGET_BACKGROUND_COLOR"
