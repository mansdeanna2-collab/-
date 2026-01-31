/**
 * uni-app 兼容的 API 模块
 * 使用 uni.request 替代 axios，支持 H5、App、小程序等多端
 * 包含请求重试、网络状态检测、错误处理等功能
 * 
 * 增强功能：
 * - 自动检测网络质量，调整超时时间
 * - API 健康检查
 * - 更细致的错误处理
 * - 数据格式验证
 * 
 * 配置说明：
 * - 可以通过 VITE_API_BASE_URL 环境变量配置 API 地址
 * - 也可以在 App.vue 中通过 globalData.apiBaseUrl 配置
 */

// Default fallback API base URL (without /api suffix)
const FALLBACK_API_BASE_URL = 'http://103.74.193.179:5000'

/**
 * Get the configured API base URL
 * Checks for VITE environment variable first, then falls back to default
 * @returns {string} The API base URL (without /api suffix)
 */
function getDefaultApiBaseUrl() {
  // Check for Vite environment variable
  // Note: This works in Vite H5 mode; in uni-app mode, the getApp() method is used instead
  if (typeof window !== 'undefined' && window.__VITE_API_BASE_URL__) {
    return window.__VITE_API_BASE_URL__
  }
  return FALLBACK_API_BASE_URL
}

// API 基础配置
const CONFIG = {
  baseUrl: '/api',
  timeout: 30000,
  retryCount: 3,
  retryDelay: 1000,
  // 弱网环境配置
  weakNetworkTimeout: 60000,
  weakNetworkRetryDelay: 2000,
  // 健康检查
  healthCheckInterval: 30000,
  lastHealthCheck: 0,
  isServerHealthy: true
}

// 错误码映射
const ERROR_MESSAGES = {
  400: '请求参数错误',
  401: '未授权，请重新登录',
  403: '拒绝访问',
  404: '请求的资源不存在',
  408: '请求超时',
  500: '服务器内部错误',
  502: '网关错误',
  503: '服务不可用',
  504: '网关超时'
}

// 不重试的状态码
const NO_RETRY_STATUS_CODES = [400, 401, 403, 404]

// 网络状态
let networkStatus = {
  isConnected: true,
  networkType: 'unknown',
  isWeakNetwork: false
}

/**
 * 初始化网络状态监听
 */
function initNetworkListener() {
  // #ifdef APP-PLUS || MP
  uni.getNetworkType({
    success: (res) => {
      networkStatus.networkType = res.networkType
      networkStatus.isConnected = res.networkType !== 'none'
      networkStatus.isWeakNetwork = ['2g', '3g'].includes(res.networkType)
    }
  })
  
  uni.onNetworkStatusChange((res) => {
    networkStatus.isConnected = res.isConnected
    networkStatus.networkType = res.networkType
    networkStatus.isWeakNetwork = ['2g', '3g'].includes(res.networkType)
    
    if (!res.isConnected) {
      uni.showToast({
        title: '网络已断开',
        icon: 'none',
        duration: 2000
      })
    } else if (networkStatus.isWeakNetwork) {
      uni.showToast({
        title: '当前网络信号较弱',
        icon: 'none',
        duration: 1500
      })
    }
  })
  // #endif
  
  // #ifdef H5
  // H5 环境网络监听
  if (typeof window !== 'undefined') {
    window.addEventListener('online', () => {
      networkStatus.isConnected = true
    })
    window.addEventListener('offline', () => {
      networkStatus.isConnected = false
    })
  }
  // #endif
}

// 初始化网络监听
initNetworkListener()

/**
 * 获取基础 URL
 * @returns {string}
 */
function getBaseUrl() {
  let baseUrl = CONFIG.baseUrl
  
  // #ifdef APP-PLUS
  try {
    const app = getApp()
    if (app && app.globalData && app.globalData.apiBaseUrl) {
      baseUrl = app.globalData.apiBaseUrl
    } else {
      // 从配置中读取或使用默认值
      baseUrl = `${getDefaultApiBaseUrl()}/api`
    }
  } catch (e) {
    console.warn('获取全局配置失败，使用默认 API 地址')
    baseUrl = `${getDefaultApiBaseUrl()}/api`
  }
  // #endif
  
  return baseUrl
}

/**
 * 检查网络状态
 * @returns {Promise<boolean>}
 */
function checkNetwork() {
  return new Promise((resolve) => {
    // #ifdef APP-PLUS || MP
    if (!networkStatus.isConnected) {
      uni.showToast({
        title: '网络连接不可用',
        icon: 'none'
      })
      resolve(false)
      return
    }
    // #endif
    resolve(true)
  })
}

/**
 * 获取当前请求超时时间 (根据网络状态自动调整)
 * @returns {number} 超时时间（毫秒）
 */
function getTimeout() {
  if (networkStatus && networkStatus.isWeakNetwork === true) {
    return CONFIG.weakNetworkTimeout
  }
  return CONFIG.timeout
}

/**
 * 获取当前重试延迟 (根据网络状态自动调整)
 * @returns {number} 延迟时间（毫秒）
 */
function getRetryDelay() {
  if (networkStatus && networkStatus.isWeakNetwork === true) {
    return CONFIG.weakNetworkRetryDelay
  }
  return CONFIG.retryDelay
}

/**
 * 延迟函数
 * @param {number} ms 毫秒
 * @returns {Promise}
 */
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * 验证 API 响应数据格式
 * @param {any} data 响应数据
 * @returns {Object} 验证结果
 */
function validateResponseData(data) {
  if (data === null || data === undefined) {
    return { valid: false, error: '服务器返回空数据' }
  }
  
  // 检查是否是对象或数组
  if (typeof data !== 'object') {
    return { valid: false, error: '服务器返回数据格式错误' }
  }
  
  return { valid: true, data }
}

/**
 * 封装的请求方法（带重试机制和智能超时）
 * @param {Object} options 请求配置
 * @param {number} retryCount 重试次数
 * @returns {Promise}
 */
async function request(options, retryCount = 0) {
  // 检查网络状态
  const isNetworkAvailable = await checkNetwork()
  if (!isNetworkAvailable) {
    return Promise.reject(new Error('网络不可用'))
  }
  
  const baseUrl = getBaseUrl()
  const currentTimeout = options.timeout || getTimeout()
  const currentRetryDelay = getRetryDelay()
  
  return new Promise((resolve, reject) => {
    uni.request({
      url: baseUrl + options.url,
      method: options.method || 'GET',
      data: options.data || options.params,
      timeout: currentTimeout,
      header: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...options.headers
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          // 验证响应数据
          const validation = validateResponseData(res.data)
          if (!validation.valid) {
            console.warn('API response validation failed:', validation.error)
          }
          
          // 标记服务器健康
          CONFIG.isServerHealthy = true
          CONFIG.lastHealthCheck = Date.now()
          
          resolve(res.data)
        } else {
          const errorMessage = ERROR_MESSAGES[res.statusCode] || `请求失败 (${res.statusCode})`
          console.error('API Error:', res.statusCode, errorMessage)
          
          // 某些错误码不重试
          if (NO_RETRY_STATUS_CODES.includes(res.statusCode)) {
            reject(new Error(errorMessage))
            return
          }
          
          // 其他错误尝试重试
          if (retryCount < CONFIG.retryCount) {
            console.log(`请求失败，${currentRetryDelay}ms 后重试 (${retryCount + 1}/${CONFIG.retryCount})`)
            delay(currentRetryDelay).then(() => {
              request(options, retryCount + 1).then(resolve).catch(reject)
            })
          } else {
            reject(new Error(errorMessage))
          }
        }
      },
      fail: (err) => {
        console.error('Request Error:', err)
        
        // 标记服务器可能不健康
        CONFIG.isServerHealthy = false
        
        // 解析错误类型
        const errMsg = err.errMsg || ''
        let userFriendlyMessage = '网络请求失败'
        
        if (errMsg.includes('timeout')) {
          userFriendlyMessage = networkStatus.isWeakNetwork 
            ? '网络信号弱，请求超时' 
            : '请求超时，请稍后重试'
        } else if (errMsg.includes('abort')) {
          userFriendlyMessage = '请求已取消'
        } else if (errMsg.includes('fail')) {
          userFriendlyMessage = '网络连接失败，请检查网络设置'
        }
        
        // 网络错误重试
        const currentRetryDelay = getRetryDelay()
        if (retryCount < CONFIG.retryCount) {
          console.log(`网络错误，${currentRetryDelay}ms 后重试 (${retryCount + 1}/${CONFIG.retryCount})`)
          delay(currentRetryDelay).then(() => {
            request(options, retryCount + 1).then(resolve).catch(reject)
          })
        } else {
          reject(new Error(userFriendlyMessage))
        }
      }
    })
  })
}

/**
 * GET 请求
 * @param {string} url 请求路径
 * @param {Object} params 查询参数
 * @returns {Promise}
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
 * @param {string} url 请求路径
 * @param {Object} data 请求体
 * @returns {Promise}
 */
function post(url, data = {}) {
  return request({
    url,
    method: 'POST',
    data
  })
}

/**
 * PUT 请求
 * @param {string} url 请求路径
 * @param {Object} data 请求体
 * @returns {Promise}
 */
function put(url, data = {}) {
  return request({
    url,
    method: 'PUT',
    data
  })
}

/**
 * DELETE 请求
 * @param {string} url 请求路径
 * @param {Object} params 查询参数
 * @returns {Promise}
 */
function del(url, params = {}) {
  return request({
    url,
    method: 'DELETE',
    params
  })
}

// Video API endpoints
export const videoApi = {
  /**
   * 获取视频列表（分页）
   * @param {Object} params - { limit, offset }
   * @returns {Promise}
   */
  getVideos(params = {}) {
    return get('/videos', params)
  },

  /**
   * 获取单个视频详情
   * @param {string|number} videoId 视频ID
   * @returns {Promise}
   */
  getVideo(videoId) {
    if (!videoId) {
      return Promise.reject(new Error('视频ID不能为空'))
    }
    return get(`/videos/${videoId}`)
  },

  /**
   * 搜索视频
   * @param {string} keyword 搜索关键词
   * @param {number} limit 每页数量
   * @param {number} offset 偏移量
   * @returns {Promise}
   */
  searchVideos(keyword, limit = 20, offset = 0) {
    if (!keyword || typeof keyword !== 'string' || !keyword.trim()) {
      return Promise.reject(new Error('搜索关键词不能为空'))
    }
    return get('/videos/search', { keyword: keyword.trim(), limit, offset })
  },

  /**
   * 按分类获取视频
   * @param {string} category 分类名称
   * @param {number} limit 每页数量
   * @param {number} offset 偏移量
   * @returns {Promise}
   */
  getVideosByCategory(category, limit = 20, offset = 0) {
    if (!category) {
      return Promise.reject(new Error('分类不能为空'))
    }
    return get('/videos/category', { category, limit, offset })
  },

  /**
   * 获取所有分类
   * @returns {Promise}
   */
  getCategories() {
    return get('/categories')
  },

  /**
   * 获取热门视频
   * @param {number} limit 数量限制
   * @returns {Promise}
   */
  getTopVideos(limit = 10) {
    return get('/videos/top', { limit })
  },

  /**
   * 更新播放次数
   * @param {string|number} videoId 视频ID
   * @returns {Promise}
   */
  updatePlayCount(videoId) {
    if (!videoId) {
      return Promise.reject(new Error('视频ID不能为空'))
    }
    return post(`/videos/${videoId}/play`)
  },

  /**
   * 获取数据库统计信息
   * @returns {Promise}
   */
  getStatistics() {
    return get('/statistics')
  },

  /**
   * 健康检查 - 检测 API 服务器是否可用
   * @returns {Promise<boolean>}
   */
  async healthCheck() {
    try {
      await get('/statistics')
      CONFIG.isServerHealthy = true
      CONFIG.lastHealthCheck = Date.now()
      return true
    } catch (e) {
      CONFIG.isServerHealthy = false
      return false
    }
  }
}

/**
 * 检查 API 服务器健康状态
 * @returns {Object} 健康状态信息
 */
export function getApiHealth() {
  return {
    isHealthy: CONFIG.isServerHealthy,
    lastCheck: CONFIG.lastHealthCheck,
    timeSinceLastCheck: Date.now() - CONFIG.lastHealthCheck
  }
}

// 导出配置更新方法
export function setApiConfig(config) {
  Object.assign(CONFIG, config)
}

// 导出网络状态
export function getNetworkStatus() {
  return { 
    ...networkStatus,
    isWeakNetwork: networkStatus.isWeakNetwork,
    currentTimeout: getTimeout()
  }
}

export default {
  request,
  get,
  post,
  put,
  del,
  videoApi,
  setApiConfig,
  getNetworkStatus,
  getApiHealth,
  CONFIG
}
