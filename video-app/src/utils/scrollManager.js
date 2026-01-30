/**
 * Scroll Position Manager
 * 
 * Provides robust scroll position management for app-like behavior.
 * Stores scroll positions by route name and supports multiple scrollable containers.
 * 
 * This manager is designed for:
 * - Native app packaging (Capacitor/Cordova)
 * - Mobile web apps
 * - Desktop web apps
 */

// Store scroll positions keyed by route path
const scrollPositions = new Map()

/**
 * Get the primary scrollable element
 * Handles different environments (web, mobile app, etc.)
 * @returns {Element} The scrollable element
 */
function getScrollElement() {
  // In most cases, the document element or body is the scroll container
  // Some mobile environments use document.body
  return document.documentElement.scrollTop > 0 
    ? document.documentElement 
    : document.body
}

/**
 * Get current scroll position from either documentElement or body
 * @returns {number} Current scroll position
 */
export function getCurrentScrollPosition() {
  return Math.max(
    window.pageYOffset || 0,
    document.documentElement.scrollTop || 0,
    document.body.scrollTop || 0
  )
}

/**
 * Save the current scroll position for a specific route
 * @param {string} routePath - The route path to associate with the scroll position
 * @param {number} [position] - Optional specific position to save, otherwise current position is used
 */
export function saveScrollPosition(routePath, position) {
  const scrollY = position !== undefined ? position : getCurrentScrollPosition()
  scrollPositions.set(routePath, scrollY)
}

/**
 * Get the saved scroll position for a specific route
 * @param {string} routePath - The route path to get the scroll position for
 * @returns {number} The saved scroll position, or 0 if not found
 */
export function getScrollPosition(routePath) {
  return scrollPositions.get(routePath) || 0
}

/**
 * Restore scroll position for a specific route
 * Uses multiple attempts with increasing delays to ensure restoration works
 * in various environments (especially mobile apps where rendering may be delayed)
 * 
 * @param {string} routePath - The route path to restore scroll position for
 * @param {Object} options - Options for restoration
 * @param {number} options.maxAttempts - Maximum number of restoration attempts (default: 5)
 * @param {number} options.initialDelay - Initial delay in ms before first attempt (default: 0)
 * @returns {Promise<boolean>} Whether scroll restoration was successful
 */
export function restoreScrollPosition(routePath, options = {}) {
  const { maxAttempts = 5, initialDelay = 0 } = options
  const targetPosition = getScrollPosition(routePath)
  
  if (targetPosition === 0) {
    // No saved position or position is 0, nothing to restore
    return Promise.resolve(true)
  }
  
  return new Promise((resolve) => {
    let attempts = 0
    
    const attemptRestore = () => {
      attempts++
      
      // Try multiple methods to set scroll position for cross-browser/platform support
      window.scrollTo({
        top: targetPosition,
        left: 0,
        behavior: 'instant'
      })
      
      // Also try direct assignment for environments where scrollTo doesn't work
      document.documentElement.scrollTop = targetPosition
      document.body.scrollTop = targetPosition
      
      // Verify if scroll was successful
      const currentPos = getCurrentScrollPosition()
      const tolerance = 5 // Allow 5px tolerance for rounding differences
      
      if (Math.abs(currentPos - targetPosition) <= tolerance) {
        resolve(true)
        return
      }
      
      // If we haven't reached max attempts and scroll wasn't restored, try again
      if (attempts < maxAttempts) {
        // Use exponential backoff for retry delays (20ms, 40ms, 80ms, 160ms)
        const delay = 20 * Math.pow(2, attempts - 1)
        setTimeout(attemptRestore, delay)
      } else {
        // Max attempts reached, resolve anyway
        resolve(false)
      }
    }
    
    // Start restoration after initial delay (allows for DOM to be ready)
    if (initialDelay > 0) {
      setTimeout(attemptRestore, initialDelay)
    } else {
      attemptRestore()
    }
  })
}

/**
 * Clear saved scroll position for a specific route
 * @param {string} routePath - The route path to clear
 */
export function clearScrollPosition(routePath) {
  scrollPositions.delete(routePath)
}

/**
 * Clear all saved scroll positions
 */
export function clearAllScrollPositions() {
  scrollPositions.clear()
}

/**
 * Check if there's a saved scroll position for a route
 * @param {string} routePath - The route path to check
 * @returns {boolean} Whether a scroll position is saved
 */
export function hasScrollPosition(routePath) {
  return scrollPositions.has(routePath) && scrollPositions.get(routePath) > 0
}

export default {
  saveScrollPosition,
  getScrollPosition,
  restoreScrollPosition,
  clearScrollPosition,
  clearAllScrollPositions,
  hasScrollPosition,
  getCurrentScrollPosition
}
