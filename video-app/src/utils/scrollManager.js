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
 * 
 * Key improvements for reliable scroll restoration:
 * - Uses requestAnimationFrame for smoother restoration timing
 * - Handles browser's automatic scroll restoration interference
 * - Supports various scroll container configurations across browsers
 */

// Store scroll positions keyed by route path
const scrollPositions = new Map()

// Flag to temporarily disable browser's scroll restoration
let isRestoringScroll = false

/**
 * Get current scroll position from either documentElement or body
 * Uses multiple fallbacks for cross-browser compatibility
 * @returns {number} Current scroll position
 */
export function getCurrentScrollPosition() {
  // window.scrollY is the most reliable in modern browsers
  // Fall back to pageYOffset for older browsers, then check documentElement and body
  return window.scrollY ?? window.pageYOffset ?? Math.max(
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
 * Set scroll position using multiple methods for cross-browser compatibility
 * @param {number} position - Target scroll position
 */
function setScrollPosition(position) {
  // Try window.scrollTo first (most reliable in modern browsers)
  try {
    window.scrollTo({
      top: position,
      left: 0,
      behavior: 'instant'
    })
  } catch {
    // Fallback for older browsers that don't support options
    window.scrollTo(0, position)
  }
  
  // Also set directly on scrollable elements for maximum compatibility
  // Some mobile browsers and WebView environments need this
  document.documentElement.scrollTop = position
  document.body.scrollTop = position
}

/**
 * Restore scroll position for a specific route
 * Uses requestAnimationFrame and multiple attempts to ensure restoration works
 * in various environments (especially mobile apps where rendering may be delayed)
 * 
 * Key improvements:
 * - Uses requestAnimationFrame for better timing with browser paint cycles
 * - Sets isRestoringScroll flag to prevent interference
 * - Uses progressive delays with requestAnimationFrame batching
 * 
 * @param {string} routePath - The route path to restore scroll position for
 * @param {Object} options - Options for restoration
 * @param {number} options.maxAttempts - Maximum number of restoration attempts (default: 8)
 * @param {number} options.initialDelay - Initial delay in ms before first attempt (default: 0)
 * @returns {Promise<boolean>} Whether scroll restoration was successful
 */
export function restoreScrollPosition(routePath, options = {}) {
  const { maxAttempts = 8, initialDelay = 0 } = options
  const targetPosition = getScrollPosition(routePath)
  
  if (targetPosition === 0) {
    // No saved position or position is 0, nothing to restore
    return Promise.resolve(true)
  }
  
  // Set flag to indicate we're restoring scroll
  isRestoringScroll = true
  
  return new Promise((resolve) => {
    let attempts = 0
    
    const attemptRestore = () => {
      attempts++
      
      // Use requestAnimationFrame for better timing with browser paint cycle
      requestAnimationFrame(() => {
        setScrollPosition(targetPosition)
        
        // Use another rAF to verify after paint
        requestAnimationFrame(() => {
          const currentPos = getCurrentScrollPosition()
          const tolerance = 10 // Allow 10px tolerance for rounding and layout differences
          
          if (Math.abs(currentPos - targetPosition) <= tolerance) {
            isRestoringScroll = false
            resolve(true)
            return
          }
          
          // If we haven't reached max attempts and scroll wasn't restored, try again
          if (attempts < maxAttempts) {
            // Use shorter delays early (10ms, 20ms, 30ms...) then longer (50ms, 100ms)
            const delay = attempts <= 4 ? 10 * attempts : 50 * (attempts - 3)
            setTimeout(attemptRestore, delay)
          } else {
            // Max attempts reached, try one final immediate scroll and resolve
            setScrollPosition(targetPosition)
            isRestoringScroll = false
            resolve(false)
          }
        })
      })
    }
    
    // Start restoration after initial delay (allows for DOM to be ready)
    if (initialDelay > 0) {
      setTimeout(attemptRestore, initialDelay)
    } else {
      // Use requestAnimationFrame even for immediate start for better timing
      requestAnimationFrame(attemptRestore)
    }
  })
}

/**
 * Check if scroll restoration is currently in progress
 * Useful for preventing interference from other scroll handlers
 * @returns {boolean} Whether scroll restoration is in progress
 */
export function isScrollRestoring() {
  return isRestoringScroll
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
  getCurrentScrollPosition,
  isScrollRestoring
}
