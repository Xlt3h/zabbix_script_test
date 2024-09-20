#!/bin/bash

# Check if URL parameter is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <URL> [<Destination Directory>]"
  exit 1
fi

# Assign the URL from the parameter
URL="$1"

# Extract the filename from the URL
FILENAME=$(basename "$URL")

# Check if a destination directory is provided
if [ -z "$2" ]; then
  DEST_DIR="."
else
  DEST_DIR="$2"
fi

# Create the destination directory if it doesn't exist
mkdir -p "$DEST_DIR"

# Use wget to download the file to the specified directory with the extracted filename
wget -O "$DEST_DIR/$FILENAME" "$URL"

# Check if the download was successful
if [ $? -eq 0 ]; then
  echo "Download completed: $DEST_DIR/$FILENAME"
else
  echo "Download failed!"
  exit 1
fi
