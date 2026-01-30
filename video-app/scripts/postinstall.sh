#!/bin/bash
# Post-install script to apply patches and fix Java version compatibility

set -e  # Exit on any error

# Cleanup function for trap
cleanup() {
    if [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
    fi
}
trap cleanup EXIT

# Apply patches with patch-package
npx patch-package

# Fix Java version in capacitor-cordova-android-plugins template
# The template uses Java 21 but we need Java 17 for compatibility with openjdk-17-jdk
TEMPLATE_PATH="node_modules/@capacitor/cli/assets/capacitor-cordova-android-plugins.tar.gz"

if [ -f "$TEMPLATE_PATH" ]; then
    TEMP_DIR=$(mktemp -d)
    
    # Extract the template
    if ! tar -xzf "$TEMPLATE_PATH" -C "$TEMP_DIR"; then
        echo "Error: Failed to extract template"
        exit 1
    fi
    
    # Fix Java version in build.gradle (change VERSION_21 to VERSION_17)
    # Use portable sed syntax that works on both Linux and macOS
    if [ -f "$TEMP_DIR/build.gradle" ]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' 's/JavaVersion\.VERSION_21/JavaVersion.VERSION_17/g' "$TEMP_DIR/build.gradle"
        else
            sed -i 's/JavaVersion\.VERSION_21/JavaVersion.VERSION_17/g' "$TEMP_DIR/build.gradle"
        fi
    fi
    
    # Recreate the tar.gz with all original contents
    if ! (cd "$TEMP_DIR" && tar -czf capacitor-cordova-android-plugins.tar.gz ./*); then
        echo "Error: Failed to create modified template"
        exit 1
    fi
    
    # Replace the original
    cp "$TEMP_DIR/capacitor-cordova-android-plugins.tar.gz" "$TEMPLATE_PATH"
    
    echo "✓ Fixed Java version in capacitor-cordova-android-plugins template"
fi
