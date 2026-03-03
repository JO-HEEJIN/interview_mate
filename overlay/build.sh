#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "Building InterviewMate Overlay..."
swift build

APP_NAME="InterviewMate Overlay.app"
APP_DIR=".build/$APP_NAME"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"

# Clean previous bundle
rm -rf "$APP_DIR"

# Create .app bundle structure
mkdir -p "$MACOS_DIR"

# Copy binary
cp .build/debug/InterviewMateOverlay "$MACOS_DIR/"

# Copy Info.plist
cp Resources/Info.plist "$CONTENTS_DIR/"

echo ""
echo "Built: $APP_DIR"
echo ""
echo "Run with:"
echo "  open \"$APP_DIR\""
