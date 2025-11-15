#!/bin/bash

# Exit if any of the following commands exit with non-0, and echo our commands back
set -ex"

# Zip all files from src into dist/lambda.zip
# Exclude __pycache__ folders and .pyc files
(cd src && zip -r dist/lambda.zip . -x "*.pyc" -x "*/__pycache__/*")