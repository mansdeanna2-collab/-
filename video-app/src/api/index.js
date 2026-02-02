import axios from 'axios'

// Simple in-memory cache for API responses
// Note: This cache stores the transformed response data (after axios response interceptor)
// which returns response.data directly. The cache stores whatever the API endpoint returns.
const cache = new Map()
const CACHE_TTL = 5 * 60 * 1000 // 5 minutes cache TTL
const MAX_CACHE_SIZE = 50 // Maximum number of entries to prevent memory leaks

/**
 * Clean up expired entries and enforce max cache size
 * This is called periodically to prevent memory leaks
 */
function cleanupCache() {
  const now = Date.now()
  
  // First, remove all expired entries
  for (const [key, value] of cache.entries()) {
    if (now - value.timestamp >= CACHE_TTL) {
      cache.delete(key)
    }
  }
  
  // If still over max size, remove oldest entries
  if (cache.size > MAX_CACHE_SIZE) {
    const entries = Array.from(cache.entries())
      .sort((a, b) => a[1].timestamp - b[1].timestamp)
    
    const toRemove = cache.size - MAX_CACHE_SIZE
    for (let i = 0; i < toRemove; i++) {
      cache.delete(entries[i][0])
    }
  }
}

/**
 * Get cached response if valid
 * @param {string} key - Cache key
 * @returns {any|null} - Cached data or null if expired/missing
 */
function getCached(key) {
  const cached = cache.get(key)
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data
  }
  cache.delete(key) // Clean up expired entry
  return null
}

/**
 * Set cache entry with automatic cleanup
 * @param {string} key - Cache key
 * @param {any} data - Data to cache (this is the transformed response from axios interceptor)
 */
function setCache(key, data) {
  // Clean up before adding new entry to prevent unbounded growth
  if (cache.size >= MAX_CACHE_SIZE) {
    cleanupCache()
  }
  cache.set(key, { data, timestamp: Date.now() })
}

/**
 * Generate cache key from URL and params
 * @param {string} url - Request URL
 * @param {object} params - Request params
 * @returns {string} - Cache key
 */
function getCacheKey(url, params = {}) {
  // Sort keys for consistent cache keys regardless of property order
  const sortedParams = Object.keys(params)
    .sort()
    .reduce((acc, key) => {
      acc[key] = params[key]
      return acc
    }, {})
  return url + '?' + JSON.stringify(sortedParams)
}

// Get API base URL from environment variable
// VITE_API_BASE_URL should be set to the API server URL without the /api suffix (e.g., http://103.74.193.179:5000)
// In development, the Vite dev server proxies /api requests, so we can use relative path
const getApiBaseUrl = () => {
  const envBaseUrl = import.meta.env.VITE_API_BASE_URL
  if (envBaseUrl) {
    // Remove trailing slash if present
    const baseUrl = envBaseUrl.endsWith('/') ? envBaseUrl.slice(0, -1) : envBaseUrl
    // Check if URL already ends with /api to avoid duplicate /api/api
    if (baseUrl.endsWith('/api')) {
      return baseUrl
    }
    return `${baseUrl}/api`
  }
  // Fallback to relative path for development or when env var is not set
  return '/api'
}

// Create axios instance with base configuration
const api = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor with retry configuration
api.interceptors.request.use(
  config => {
    // Add retry count to config for tracking
    config.retryCount = config.retryCount || 0
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor with enhanced error handling
api.interceptors.response.use(
  response => {
    return response.data
  },
  async error => {
    const config = error.config
    
    // Retry logic for network errors (up to 2 retries)
    if (
      config &&
      config.retryCount < 2 &&
      (!error.response || error.response.status >= 500)
    ) {
      config.retryCount += 1
      
      // Exponential backoff: 1s, 2s
      const delay = config.retryCount * 1000
      await new Promise(resolve => setTimeout(resolve, delay))
      
      return api(config)
    }
    
    // Enhanced error logging with more context
    const errorInfo = {
      url: config?.url,
      status: error.response?.status,
      message: error.message,
      retries: config?.retryCount || 0
    }
    console.error('API Error:', errorInfo)
    
    return Promise.reject(error)
  }
)

/**
 * GET request with optional caching
 * 
 * Note: This function caches the transformed response data (after axios response interceptor).
 * The response interceptor returns `response.data`, so the cache stores the API's data payload
 * directly (typically an object with `code`, `message`, and `data` fields from our API format).
 * 
 * @param {string} url - Request URL
 * @param {object} params - Request params
 * @param {boolean} useCache - Whether to use cache (default: true)
 * @returns {Promise} - API response (the transformed data from interceptor)
 */
async function cachedGet(url, params = {}, useCache = true) {
  const cacheKey = getCacheKey(url, params)
  
  if (useCache) {
    const cached = getCached(cacheKey)
    if (cached) {
      return cached
    }
  }
  
  const response = await api.get(url, { params })
  
  if (useCache) {
    setCache(cacheKey, response)
  }
  
  return response
}

// Video API endpoints
export const videoApi = {
  // Get all videos with pagination
  getVideos(params = {}) {
    return cachedGet('/videos', params)
  },

  // Get video by ID
  getVideo(videoId) {
    return cachedGet(`/videos/${videoId}`)
  },

  // Search videos by keyword (no cache - user-initiated searches should be fresh)
  searchVideos(keyword, limit = 20, offset = 0) {
    return api.get('/videos/search', { params: { keyword, limit, offset } })
  },

  // Get videos by category
  getVideosByCategory(category, limit = 20, offset = 0) {
    return cachedGet('/videos/category', { category, limit, offset })
  },

  // Get all categories (cache for longer as categories rarely change)
  getCategories() {
    return cachedGet('/categories')
  },

  // Get top videos by play count
  getTopVideos(limit = 10) {
    return cachedGet('/videos/top', { limit })
  },

  // Update play count (no cache - POST request)
  updatePlayCount(videoId) {
    return api.post(`/videos/${videoId}/play`)
  },

  // Get database statistics
  getStatistics() {
    return cachedGet('/statistics')
  },

  // Clear all cached data (useful for force refresh)
  clearCache() {
    cache.clear()
  }
}

export default api
