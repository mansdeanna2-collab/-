package com.videoapp.player.util;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.util.Base64;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import java.util.HashMap;
import java.util.Map;
import java.util.regex.Pattern;

/**
 * Image utilities for handling various image URL formats
 */
public final class ImageUtils {

    private static final String TAG = "ImageUtils";

    private ImageUtils() {
        // Private constructor to prevent instantiation
    }

    // Base64 image signatures for common image formats
    private static final Map<String, String> BASE64_SIGNATURES = new HashMap<>();
    static {
        BASE64_SIGNATURES.put("/9j/", "image/jpeg");    // JPEG
        BASE64_SIGNATURES.put("iVBOR", "image/png");    // PNG
        BASE64_SIGNATURES.put("R0lGO", "image/gif");    // GIF
        BASE64_SIGNATURES.put("UklGR", "image/webp");   // WebP
        BASE64_SIGNATURES.put("Qk", "image/bmp");       // BMP
    }

    // Pattern for standard base64 characters (with padding)
    private static final Pattern BASE64_PATTERN = Pattern.compile("^[A-Za-z0-9+/]+={0,2}$");
    // Pattern for URL-safe base64 characters (with padding)
    private static final Pattern BASE64_URL_SAFE_PATTERN = Pattern.compile("^[A-Za-z0-9_-]+={0,2}$");
    private static final Pattern WHITESPACE_PATTERN = Pattern.compile("[\\s\\r\\n]+");

    /**
     * Format image URL - handles base64 content, data URLs, and regular URLs
     */
    @NonNull
    public static String formatImageUrl(@Nullable String url) {
        if (url == null || url.trim().isEmpty()) {
            return "";
        }

        String trimmed = url.trim();

        // If already a data URL, clean and validate it
        if (trimmed.startsWith("data:")) {
            return cleanDataUrl(trimmed);
        }

        // If a valid URL, return as-is
        if (trimmed.startsWith("http://") || trimmed.startsWith("https://")) {
            return trimmed;
        }

        // Check for known base64 image signatures
        for (Map.Entry<String, String> entry : BASE64_SIGNATURES.entrySet()) {
            if (trimmed.startsWith(entry.getKey())) {
                // Clean base64: remove whitespace
                String cleaned = cleanBase64Content(trimmed);
                if (cleaned != null) {
                    return "data:" + entry.getValue() + ";base64," + cleaned;
                }
            }
        }

        // For other potential base64 content
        String cleanContent = cleanBase64Content(trimmed);
        if (cleanContent != null && cleanContent.length() > 100) {
            // Default to JPEG for unknown base64 content (most common)
            return "data:image/jpeg;base64," + cleanContent;
        }

        // Otherwise, return as-is
        return trimmed;
    }

    /**
     * Clean a data URL by removing whitespace from the base64 content
     */
    @NonNull
    private static String cleanDataUrl(@NonNull String dataUrl) {
        try {
            int commaIndex = dataUrl.indexOf(",");
            if (commaIndex == -1) {
                return dataUrl;
            }
            
            String header = dataUrl.substring(0, commaIndex + 1);
            String base64Part = dataUrl.substring(commaIndex + 1);
            
            // Remove whitespace from base64 content
            String cleaned = WHITESPACE_PATTERN.matcher(base64Part).replaceAll("");
            
            return header + cleaned;
        } catch (Exception e) {
            Log.w(TAG, "Error cleaning data URL", e);
            return dataUrl;
        }
    }

    /**
     * Check if URL is a data URL (base64 image)
     */
    public static boolean isDataUrl(@Nullable String url) {
        return url != null && url.startsWith("data:");
    }

    /**
     * Decode base64 image to Bitmap with improved error handling
     */
    @Nullable
    public static Bitmap decodeBase64Image(@NonNull String dataUrl) {
        try {
            // Extract base64 content from data URL
            String base64Data;
            if (dataUrl.contains(",")) {
                base64Data = dataUrl.substring(dataUrl.indexOf(",") + 1);
            } else {
                base64Data = dataUrl;
            }

            // Remove any whitespace
            base64Data = WHITESPACE_PATTERN.matcher(base64Data).replaceAll("");

            // Try standard base64 first
            byte[] decodedBytes;
            try {
                decodedBytes = Base64.decode(base64Data, Base64.DEFAULT);
            } catch (IllegalArgumentException e) {
                // Try URL-safe base64 if standard fails
                try {
                    decodedBytes = Base64.decode(base64Data, Base64.URL_SAFE);
                } catch (IllegalArgumentException e2) {
                    Log.w(TAG, "Failed to decode base64 image", e2);
                    return null;
                }
            }

            if (decodedBytes == null || decodedBytes.length == 0) {
                return null;
            }

            // Decode with options to avoid memory issues
            BitmapFactory.Options options = new BitmapFactory.Options();
            options.inPreferredConfig = Bitmap.Config.RGB_565; // Use less memory
            
            Bitmap bitmap = BitmapFactory.decodeByteArray(decodedBytes, 0, decodedBytes.length, options);
            if (bitmap == null) {
                // Try without options
                bitmap = BitmapFactory.decodeByteArray(decodedBytes, 0, decodedBytes.length);
            }
            
            return bitmap;
        } catch (Exception e) {
            Log.w(TAG, "Error decoding base64 image", e);
            return null;
        } catch (OutOfMemoryError e) {
            Log.e(TAG, "Out of memory decoding base64 image", e);
            return null;
        }
    }

    /**
     * Clean and validate base64 content
     */
    @Nullable
    private static String cleanBase64Content(@NonNull String content) {
        // Remove whitespace
        String cleaned = WHITESPACE_PATTERN.matcher(content).replaceAll("");

        // Minimum length check
        if (cleaned.length() < 4) {
            return null;
        }

        // Validate base64 characters and proper padding
        // Accept both standard and URL-safe base64
        if (!BASE64_PATTERN.matcher(cleaned).matches() && 
            !BASE64_URL_SAFE_PATTERN.matcher(cleaned).matches()) {
            return null;
        }

        // Check length is valid for base64 (must be multiple of 4)
        if (cleaned.length() % 4 != 0) {
            // Try to add padding
            int padNeeded = 4 - (cleaned.length() % 4);
            StringBuilder sb = new StringBuilder(cleaned);
            for (int i = 0; i < padNeeded; i++) {
                sb.append('=');
            }
            cleaned = sb.toString();
        }

        return cleaned;
    }
}
