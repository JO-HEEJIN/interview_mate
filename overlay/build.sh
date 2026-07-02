#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "Building InterviewMate Overlay..."
swift build

APP_NAME="InterviewMate Overlay.app"
APP_DIR=".build/$APP_NAME"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

# Clean previous bundle
rm -rf "$APP_DIR"

# Create .app bundle structure
mkdir -p "$MACOS_DIR" "$RESOURCES_DIR"

# Copy binary
cp .build/debug/InterviewMateOverlay "$MACOS_DIR/"

# Copy Info.plist
cp Resources/Info.plist "$CONTENTS_DIR/"

# Copy app icon
cp Resources/AppIcon.icns "$RESOURCES_DIR/"

# Code signing — a STABLE identity keeps TCC (Screen Recording) permission across rebuilds.
# Ad-hoc signing ("-") produces a different signature every build, which makes macOS
# treat each build as a new app and reset its permissions.
# Defaults to the Apple-issued Developer ID (stable designated requirement — best for TCC).
# Override with `SIGN_IDENTITY="..." ./build.sh` to use a different identity.
SIGN_IDENTITY="${SIGN_IDENTITY:-Developer ID Application: Heejin Jo (PT69WLF486)}"
if security find-identity -v -p codesigning 2>/dev/null | grep -q "$SIGN_IDENTITY"; then
    codesign --force --identifier ing.interviewmate.overlay --sign "$SIGN_IDENTITY" "$APP_DIR"
    echo "Signed with identity: $SIGN_IDENTITY"
else
    codesign --force --identifier ing.interviewmate.overlay --sign - "$APP_DIR"
    echo "WARNING: identity '$SIGN_IDENTITY' not found — signed ad-hoc."
    echo "         Screen Recording permission WILL reset on every rebuild."
    echo "         Create a self-signed 'Code Signing' cert named '$SIGN_IDENTITY' in Keychain Access to fix this."
fi

echo ""
echo "Built: $APP_DIR"
echo ""
echo "Run with:"
echo "  open \"$APP_DIR\""
