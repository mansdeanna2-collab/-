/**
 * Image utilities for handling base64 content, data URLs, and regular URLs
 */

// Base64 image signatures for common image formats
const BASE64_SIGNATURES = {
  '/9j/': 'image/jpeg',      // JPEG
  'iVBOR': 'image/png',      // PNG  
  'R0lGO': 'image/gif',      // GIF
  'UklGR': 'image/webp',     // WebP (RIFF header)
  'Qk': 'image/bmp'          // BMP
}

/**
 * Clean and validate base64 content
 * Returns cleaned base64 string or null if invalid
 * @param {string} content - The content to clean and validate
 * @returns {string|null} - Cleaned base64 string or null if invalid
 */
export function cleanBase64Content(content) {
  if (!content || typeof content !== 'string') return null
  
  // Remove all whitespace (newlines, spaces, tabs, carriage returns)
  const cleaned = content.replace(/[\s\r\n]+/g, '')
  
  // Minimum length check
  if (cleaned.length < 4) {
    return null
  }
  
  // Validate base64 characters and proper padding
  // Base64 alphabet: A-Z, a-z, 0-9, +, /
  // Padding: = (0-2 at end)
  if (!/^[A-Za-z0-9+/]+={0,2}$/.test(cleaned)) {
    return null
  }
  
  // Check that length is valid for base64 (must be multiple of 4 with padding)
  // Valid base64 strings have length % 4 === 0
  if (cleaned.length % 4 !== 0) {
    return null
  }
  
  return cleaned
}

/**
 * Format image URL - handles base64 content, data URLs, and regular URLs
 * Enhanced implementation with better validation and edge case handling
 * @param {string} url - The URL or base64 content to format
 * @returns {string} - Formatted URL or data URL
 */
export function formatImageUrl(url) {
  if (!url) return ''
  
  // Trim whitespace for consistent detection
  const trimmed = url.trim()
  
  // If already a data URL, validate and clean
  if (trimmed.startsWith('data:')) {
    // Clean whitespace first, then validate structure
    const cleaned = trimmed.replace(/\s/g, '')
    // Basic structure check: data:image/xxx;base64,xxx
    // Allow any mime type characters including uppercase
    if (/^data:image\/[a-zA-Z0-9+-]+;base64,.+$/.test(cleaned)) {
      return cleaned
    }
    // Return original if it doesn't match expected format
    return trimmed
  }
  
  // If already a valid URL (http/https), encode and return
  if (trimmed.startsWith('http://') || trimmed.startsWith('https://')) {
    try {
      // Check if URL is already encoded
      const decoded = decodeURI(trimmed)
      if (decoded !== trimmed) {
        return trimmed // Already encoded
      }
      return encodeURI(trimmed)
    } catch (e) {
      // If decodeURI fails, URL might be malformed, return as-is
      return trimmed
    }
  }
  
  // Check for known base64 image headers
  for (const [signature, mimeType] of Object.entries(BASE64_SIGNATURES)) {
    if (trimmed.startsWith(signature)) {
      // Clean base64: remove whitespace (newlines, spaces, tabs)
      const cleanBase64 = cleanBase64Content(trimmed)
      if (cleanBase64) {
        return `data:${mimeType};base64,${cleanBase64}`
      }
    }
  }
  
  // For other potential base64 content: must be long and contain only base64 characters
  // This is a conservative check to avoid false positives
  const cleanContent = cleanBase64Content(trimmed)
  if (cleanContent && cleanContent.length > 100) {
    // Default to PNG for unknown base64 content
    return 'data:image/png;base64,' + cleanContent
  }
  
  // Otherwise, treat as regular URL and encode
  try {
    return encodeURI(trimmed)
  } catch (e) {
    return trimmed
  }
}

/**
 * Safely encode URL for video sources (doesn't need base64 handling for video URLs)
 * @param {string} url - The URL to encode
 * @returns {string} - Encoded URL
 */
export function safeEncodeURI(url) {
  if (!url) return ''
  try {
    const decoded = decodeURI(url)
    if (decoded !== url) {
      return url // Already encoded
    }
    return encodeURI(url)
  } catch (e) {
    return url
  }
}
