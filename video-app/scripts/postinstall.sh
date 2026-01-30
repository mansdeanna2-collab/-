#!/bin/bash
# Post-install script to apply patches and fix Java version compatibility

# Apply patches with patch-package
npx patch-package

# Fix Java version in capacitor-cordova-android-plugins template
# The template uses Java 21 but we need Java 17 for compatibility with openjdk-17-jdk
TEMPLATE_PATH="node_modules/@capacitor/cli/assets/capacitor-cordova-android-plugins.tar.gz"

if [ -f "$TEMPLATE_PATH" ]; then
    TEMP_DIR=$(mktemp -d)
    
    # Extract the template
    tar -xzf "$TEMPLATE_PATH" -C "$TEMP_DIR"
    
    # Fix Java version in build.gradle (change VERSION_21 to VERSION_17)
    if [ -f "$TEMP_DIR/build.gradle" ]; then
        sed -i 's/JavaVersion\.VERSION_21/JavaVersion.VERSION_17/g' "$TEMP_DIR/build.gradle"
    fi
    
    # Recreate the tar.gz
    (cd "$TEMP_DIR" && tar -czf capacitor-cordova-android-plugins.tar.gz build.gradle src)
    
    # Replace the original
    cp "$TEMP_DIR/capacitor-cordova-android-plugins.tar.gz" "$TEMPLATE_PATH"
    
    # Cleanup
    rm -rf "$TEMP_DIR"
    
    echo "✓ Fixed Java version in capacitor-cordova-android-plugins template"
fi
