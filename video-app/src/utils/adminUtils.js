/**
 * Admin Utilities
 * Shared utility functions for admin pages
 */

/**
 * Detect if running in standalone admin mode (port 8897)
 * @returns {boolean} True if running on port 8897
 */
export function isStandaloneMode() {
  return window.location.port === '8897'
}

/**
 * Get the frontend URL based on current mode
 * In standalone mode, returns URL to port 3000
 * In embedded mode, returns root '/'
 * @returns {string} Frontend URL
 */
export function getFrontendUrl() {
  if (isStandaloneMode()) {
    const currentHost = window.location.hostname
    return `http://${currentHost}:3000`
  }
  return '/'
}

/**
 * Get the admin path for a given page
 * In standalone mode, returns path relative to root (e.g., /dashboard)
 * In embedded mode, returns path under /admin (e.g., /admin/dashboard)
 * @param {string} page - Page name (e.g., 'dashboard')
 * @returns {string} Full admin path
 */
export function getAdminPath(page) {
  if (isStandaloneMode()) {
    return `/${page}`
  }
  return `/admin/${page}`
}

export default {
  isStandaloneMode,
  getFrontendUrl,
  getAdminPath
}
