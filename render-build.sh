#!/usr/bin/env bash
# render-build.sh

# Exit on error
set -e

# Install system dependencies
apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1

# Install Python dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt
