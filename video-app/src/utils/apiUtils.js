/**
 * API utility functions for consistent data extraction from API responses
 */

/**
 * Safely extract array data from API response
 * Handles cases where data might be null, undefined, or a non-array
 * 
 * @param {Object} result - API response object (typically { code, message, data })
 * @returns {Array} - Array of data or empty array
 * 
 * @example
 * const result = await videoApi.getVideos()
 * const videos = extractArrayData(result) // Always returns an array
 */
export function extractArrayData(result) {
  const data = result?.data ?? result
  return Array.isArray(data) ? data : []
}

/**
 * Safely extract object data from API response
 * Handles cases where data might be null, undefined, or not an object
 * 
 * @param {Object} result - API response object (typically { code, message, data })
 * @returns {Object} - Object data or empty object
 * 
 * @example
 * const result = await videoApi.getVideo(id)
 * const video = extractObjectData(result) // Always returns an object
 */
export function extractObjectData(result) {
  const data = result?.data ?? result
  return (data && typeof data === 'object' && !Array.isArray(data)) ? data : {}
}

export default {
  extractArrayData,
  extractObjectData
}
