#!/bin/bash
# Build ObjectBox Viewer for macOS ARM64 (Apple Silicon)

set -e  # Exit on error

echo "========================================="
echo "Building ObjectBox Viewer for macOS ARM64"
echo "========================================="

# Check PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    echo "Error: PyInstaller not found"
    echo "Please install it: pip install pyinstaller"
    exit 1
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/*

# Build for ARM64
echo "Building for ARM64 architecture..."
pyinstaller \
    --clean \
    --noconfirm \
    --target-arch arm64 \
    main.py \
    --name ObjectBoxViewer \
    --windowed \
    --add-data "src:src" \
    --hidden-import customtkinter \
    --hidden-import lmdb \
    --hidden-import PIL \
    --hidden-import tkinter.ttk

# Check if build succeeded
if [ -d "dist/ObjectBoxViewer.app" ]; then
    echo "✅ Build successful!"
    echo "📦 Output: dist/ObjectBoxViewer.app"

    # Get app size
    app_size=$(du -sh "dist/ObjectBoxViewer.app" | cut -f1)
    echo "📊 App size: $app_size"
else
    echo "❌ Build failed!"
    exit 1
fi

echo "========================================="
echo "Build complete!"
echo "========================================="
