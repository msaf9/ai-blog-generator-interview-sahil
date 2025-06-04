#!/usr/bin/env bash

# Precondition: Flask server must be running on localhost:80
# This script calls /generate for a fixed keyword and writes output to a file.

KEYWORD="wireless earbuds"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="daily_${KEYWORD// /_}_${TIMESTAMP}.json"

# URL-encode the keyword for the query string
ENCODED_KEYWORD=$(python3 - <<EOF
import urllib.parse
print(urllib.parse.quote("${KEYWORD}"))
EOF
)

# Make the request to the Flask server and save the output
curl "http://localhost:80/generate?keyword=${ENCODED_KEYWORD}" -o "$OUTPUT_FILE"

echo "Saved response to $OUTPUT_FILE"
