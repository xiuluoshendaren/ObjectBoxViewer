#!/bin/bash
# Build ObjectBox Viewer for all platforms
# Note: You need to run this script on the target platform

set -e  # Exit on error

echo "========================================="
echo "ObjectBox Viewer Multi-Platform Builder"
echo "========================================="
echo ""
echo "This script will build ObjectBox Viewer for the current platform."
echo "To build for all platforms, you need to run this on:"
echo "  1. macOS (for both ARM64 and Intel versions)"
echo "  2. Windows (for Windows version)"
echo ""

# Detect current platform
OS="$(uname -s)"
ARCH="$(uname -m)"

echo ""
echo "Detected platform: $OS ($ARCH)"
echo ""

case "$OS" in
    Darwin)
        echo "Building for macOS..."

        if [ "$ARCH" = "arm64" ]; then
            echo "Architecture: Apple Silicon (ARM64)"
            bash build_macos_arm64.sh
        elif [ "$ARCH" = "x86_64" ]; then
            echo "Architecture: Intel (x86_64)"
            bash build_macos_intel.sh
        else
            echo "Warning: Unknown architecture $ARCH"
            echo "Building with default settings..."
            pyinstaller --clean --noconfirm ObjectBoxViewer.spec
        fi
        ;;

    CYGWIN*|MINGW*|MSYS*)
        echo "Building for Windows..."
        ./build_windows.bat
        ;;

    Linux)
        echo "Building for Linux..."
        echo "Note: Linux builds are not officially supported yet"
        pyinstaller --clean --noconfirm ObjectBoxViewer.spec
        ;;

    *)
        echo "Error: Unsupported platform $OS"
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo "Build process completed!"
echo "========================================="
