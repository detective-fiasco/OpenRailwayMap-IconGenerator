#!/usr/bin/env bash
set -euo pipefail

SRC_DIR="out"
DST_DIR="compressed"

# Find all files recursively under out/
find "$SRC_DIR" -type f | while IFS= read -r input_file; do
  # Get relative path from source dir
  rel_path="${input_file#$SRC_DIR/}"

  # Build output path in compressed/ with same structure
  output_file="$DST_DIR/$rel_path"

  # Create destination folder
  mkdir -p "$(dirname "$output_file")"

  # Run rsvg-convert
  rsvg-convert "$input_file" --format svg > "$output_file"

  echo "Converted: $input_file -> $output_file"
done