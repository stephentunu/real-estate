#!/bin/bash
# Jaston Real Estate Platform Setup
# This script delegates to the main setup script in infrastructure/

echo "🏗️  Jaston Real Estate Platform Setup"
echo "======================================"

# Change to project root directory
cd "$(dirname "$0")"

# Run the main setup script with all arguments passed through
python3 infrastructure/setup.py "$@"
