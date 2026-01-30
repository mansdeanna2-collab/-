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

// Maximum size for reading text response (5MB)
const MAX_TEXT_SIZE = 5 * 1024 * 1024

/**
 * Check if a URL is valid (http or https)
 * @param {string} url - URL to check
 * @returns {boolean}
 */
function isValidUrl(url) {
  if (!url || typeof url !== 'string') return false
  return url.startsWith('http://') || url.startsWith('https://')
}

/**
 * Load image with base64 detection and conversion
 * Fetches the URL and checks if the response is raw base64 data.
 * If so, converts it to a proper data URL.
 * @param {HTMLImageElement} imgElement - The image element to load into
 * @param {string} url - The image URL to load
 */
export async function loadImageWithBase64Detection(imgElement, url) {
  // If it's already a data URL, use it directly
  if (url && url.startsWith('data:image/')) {
    imgElement.src = url
    return
  }

  // First try formatImageUrl for local base64 content
  const formattedUrl = formatImageUrl(url)
  if (formattedUrl && formattedUrl.startsWith('data:')) {
    imgElement.src = formattedUrl
    return
  }

  // Validate URL before fetching
  if (!isValidUrl(url)) {
    imgElement.src = formattedUrl || ''
    return
  }

  try {
    const response = await fetch(url, {
      method: 'GET',
      mode: 'cors',
      credentials: 'omit'
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const contentType = response.headers.get('content-type') || ''

    // If the response is an image binary, use the URL directly
    if (contentType.startsWith('image/')) {
      imgElement.src = url
      return
    }

    // Check content length to prevent memory issues
    const contentLength = parseInt(response.headers.get('content-length') || '0', 10)
    if (contentLength > MAX_TEXT_SIZE) {
      // Too large for base64 text, try as URL directly
      imgElement.src = url
      return
    }

    // If content-type is text or unknown, check if it's raw base64
    const text = await response.text()

    // Additional size check after reading
    if (text.length > MAX_TEXT_SIZE) {
      imgElement.src = url
      return
    }

    // Check for known base64 signatures
    const trimmedText = text.trim()
    let detectedMimeType = null
    for (const [signature, mimeType] of Object.entries(BASE64_SIGNATURES)) {
      if (trimmedText.startsWith(signature)) {
        detectedMimeType = mimeType
        break
      }
    }

    if (detectedMimeType) {
      // Clean and convert raw base64 to data URL
      const cleanedBase64 = cleanBase64Content(trimmedText)
      if (cleanedBase64) {
        imgElement.src = `data:${detectedMimeType};base64,${cleanedBase64}`
        return
      }
    }

    // Not recognized as base64, try using URL directly
    imgElement.src = url
  } catch (error) {
    // On fetch error (CORS, network, etc.), fall back to direct URL loading
    // The browser might be able to load it even if fetch fails
    imgElement.src = url
  }
}
