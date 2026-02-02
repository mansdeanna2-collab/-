/**
 * Format utilities for consistent display formatting across the app
 */

/**
 * Format play count with Chinese number formatting
 * @param {number} count - The play count to format
 * @returns {string} - Formatted play count string
 */
export function formatPlayCount(count) {
  if (!count || count <= 0) return '0'
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + '万'
  }
  return count.toString()
}

/**
 * Format duration from seconds to HH:MM:SS or MM:SS
 * @param {number} seconds - Duration in seconds
 * @returns {string} - Formatted duration string
 */
export function formatDuration(seconds) {
  if (!seconds || seconds <= 0) return '00:00'
  
  const hrs = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hrs > 0) {
    return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${mins}:${secs.toString().padStart(2, '0')}`
}
