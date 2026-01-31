#!/bin/bash
# Post-install script to apply patches and fix Java version compatibility
# Also fixes deprecated Gradle features for Gradle 9.0 compatibility

set -e  # Exit on any error

# Cleanup function for trap
cleanup() {
    if [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
    fi
    if [ -n "$TEMP_DIR2" ] && [ -d "$TEMP_DIR2" ]; then
        rm -rf "$TEMP_DIR2"
    fi
}
trap cleanup EXIT

# Helper function for portable sed in-place editing
sed_inplace() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "$@"
    else
        sed -i "$@"
    fi
}

# Apply patches with patch-package
npx patch-package

# Fix capacitor-cordova-android-plugins template
# - Java version: VERSION_21 -> VERSION_17 for openjdk-17-jdk compatibility
# - Deprecated lintOptions -> lint for Gradle 9.0 compatibility
CORDOVA_TEMPLATE_PATH="node_modules/@capacitor/cli/assets/capacitor-cordova-android-plugins.tar.gz"

if [ -f "$CORDOVA_TEMPLATE_PATH" ]; then
    TEMP_DIR=$(mktemp -d)
    
    # Extract the template
    if ! tar -xzf "$CORDOVA_TEMPLATE_PATH" -C "$TEMP_DIR"; then
        echo "Error: Failed to extract capacitor-cordova-android-plugins template"
        exit 1
    fi
    
    if [ -f "$TEMP_DIR/build.gradle" ]; then
        # Fix Java version (change VERSION_21 to VERSION_17)
        sed_inplace 's/JavaVersion\.VERSION_21/JavaVersion.VERSION_17/g' "$TEMP_DIR/build.gradle"
        
        # Fix deprecated lintOptions -> lint for Gradle 9.0 compatibility
        sed_inplace 's/lintOptions/lint/g' "$TEMP_DIR/build.gradle"
    fi
    
    # Recreate the tar.gz with all original contents
    if ! (cd "$TEMP_DIR" && tar -czf capacitor-cordova-android-plugins.tar.gz ./*); then
        echo "Error: Failed to create modified capacitor-cordova-android-plugins template"
        exit 1
    fi
    
    # Replace the original
    cp "$TEMP_DIR/capacitor-cordova-android-plugins.tar.gz" "$CORDOVA_TEMPLATE_PATH"
    
    echo "✓ Fixed Java version and lintOptions deprecation in capacitor-cordova-android-plugins template"
fi

# Fix android-template
# - Deprecated rootProject.buildDir -> layout.buildDirectory for Gradle 9.0 compatibility
ANDROID_TEMPLATE_PATH="node_modules/@capacitor/cli/assets/android-template.tar.gz"

if [ -f "$ANDROID_TEMPLATE_PATH" ]; then
    TEMP_DIR2=$(mktemp -d)
    
    # Extract the template
    if ! tar -xzf "$ANDROID_TEMPLATE_PATH" -C "$TEMP_DIR2"; then
        echo "Error: Failed to extract android-template"
        exit 1
    fi
    
    if [ -f "$TEMP_DIR2/build.gradle" ]; then
        # Fix deprecated rootProject.buildDir -> layout.buildDirectory for Gradle 9.0 compatibility
        sed_inplace 's/rootProject\.buildDir/layout.buildDirectory/g' "$TEMP_DIR2/build.gradle"
    fi
    
    # Recreate the tar.gz with all original contents
    if ! (cd "$TEMP_DIR2" && tar -czf android-template.tar.gz ./*); then
        echo "Error: Failed to create modified android-template"
        exit 1
    fi
    
    # Replace the original
    cp "$TEMP_DIR2/android-template.tar.gz" "$ANDROID_TEMPLATE_PATH"
    
    echo "✓ Fixed buildDir deprecation in android-template"
fi
