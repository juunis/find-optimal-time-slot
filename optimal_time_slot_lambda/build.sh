#!/bin/bash

# Exit if any of the following commands exit with non-0, and echo our commands back
set -ex

# Paths
LAMBDA_SRC_DIR="optimal-time-slot/src"
DIST_DIR="optimal-time-slot/dist"
ZIP_FILE="$DIST_DIR/lambda.zip"

# Zip all files from src into dist/lambda.zip
# Exclude __pycache__ folders and .pyc files
(cd "$LAMBDA_SRC_DIR" && zip -r "$ZIP_FILE" . -x "*.pyc" -x "*/__pycache__/*")