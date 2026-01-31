/**
 * uni-app 兼容的 API 模块
 * 使用 uni.request 替代 axios，支持 H5、App、小程序等多端
 */

// API 基础配置
const BASE_URL = '/api'
const TIMEOUT = 30000

/**
 * 封装的请求方法
 * @param {Object} options 请求配置
 * @returns {Promise}
 */
function request(options) {
  return new Promise((resolve, reject) => {
    // 根据平台设置基础 URL
    let baseUrl = BASE_URL
    
    // #ifdef APP-PLUS
    // App 环境需要完整 URL，从全局配置获取
    try {
      const app = getApp()
      if (app && app.globalData && app.globalData.apiBaseUrl) {
        baseUrl = app.globalData.apiBaseUrl
      } else {
        baseUrl = 'http://localhost:5000/api'
      }
    } catch (e) {
      baseUrl = 'http://localhost:5000/api'
    }
    // #endif

    uni.request({
      url: baseUrl + options.url,
      method: options.method || 'GET',
      data: options.data || options.params,
      timeout: options.timeout || TIMEOUT,
      header: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          console.error('API Error:', res)
          reject(new Error(`Request failed with status ${res.statusCode}`))
        }
      },
      fail: (err) => {
        console.error('Request Error:', err)
        reject(err)
      }
    })
  })
}

/**
 * GET 请求
 */
function get(url, params = {}) {
  return request({
    url,
    method: 'GET',
    params
  })
}

/**
 * POST 请求
 */
function post(url, data = {}) {
  return request({
    url,
    method: 'POST',
    data
  })
}

// Video API endpoints
export const videoApi = {
  // Get all videos with pagination
  getVideos(params = {}) {
    return get('/videos', params)
  },

  // Get video by ID
  getVideo(videoId) {
    return get(`/videos/${videoId}`)
  },

  // Search videos by keyword
  searchVideos(keyword, limit = 20, offset = 0) {
    return get('/videos/search', { keyword, limit, offset })
  },

  // Get videos by category
  getVideosByCategory(category, limit = 20, offset = 0) {
    return get('/videos/category', { category, limit, offset })
  },

  // Get all categories
  getCategories() {
    return get('/categories')
  },

  // Get top videos by play count
  getTopVideos(limit = 10) {
    return get('/videos/top', { limit })
  },

  // Update play count
  updatePlayCount(videoId) {
    return post(`/videos/${videoId}/play`)
  },

  // Get database statistics
  getStatistics() {
    return get('/statistics')
  }
}

export default {
  request,
  get,
  post,
  videoApi
}
