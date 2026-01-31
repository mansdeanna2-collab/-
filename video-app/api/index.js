/**
 * uni-app 兼容的 API 模块
 * 使用 uni.request 替代 axios，支持 H5、App、小程序等多端
 * 包含请求重试、网络状态检测、错误处理等功能
 */

// API 基础配置
const CONFIG = {
  baseUrl: '/api',
  timeout: 30000,
  retryCount: 3,
  retryDelay: 1000
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
  networkType: 'unknown'
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
    }
  })
  
  uni.onNetworkStatusChange((res) => {
    networkStatus.isConnected = res.isConnected
    networkStatus.networkType = res.networkType
    
    if (!res.isConnected) {
      uni.showToast({
        title: '网络已断开',
        icon: 'none',
        duration: 2000
      })
    }
  })
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
      baseUrl = 'http://localhost:5000/api'
    }
  } catch (e) {
    console.warn('获取全局配置失败，使用默认 API 地址')
    baseUrl = 'http://localhost:5000/api'
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
 * 延迟函数
 * @param {number} ms 毫秒
 * @returns {Promise}
 */
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * 封装的请求方法（带重试机制）
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
  
  return new Promise((resolve, reject) => {
    const requestTask = uni.request({
      url: baseUrl + options.url,
      method: options.method || 'GET',
      data: options.data || options.params,
      timeout: options.timeout || CONFIG.timeout,
      header: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...options.headers
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
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
            console.log(`请求失败，${CONFIG.retryDelay}ms 后重试 (${retryCount + 1}/${CONFIG.retryCount})`)
            delay(CONFIG.retryDelay).then(() => {
              request(options, retryCount + 1).then(resolve).catch(reject)
            })
          } else {
            reject(new Error(errorMessage))
          }
        }
      },
      fail: (err) => {
        console.error('Request Error:', err)
        
        // 网络错误重试
        if (retryCount < CONFIG.retryCount) {
          console.log(`网络错误，${CONFIG.retryDelay}ms 后重试 (${retryCount + 1}/${CONFIG.retryCount})`)
          delay(CONFIG.retryDelay).then(() => {
            request(options, retryCount + 1).then(resolve).catch(reject)
          })
        } else {
          const errorMessage = err.errMsg || '网络请求失败'
          reject(new Error(errorMessage))
        }
      }
    })
    
    // 超时处理
    if (options.onProgress) {
      // 可以添加进度回调
    }
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
  }
}

// 导出配置更新方法
export function setApiConfig(config) {
  Object.assign(CONFIG, config)
}

// 导出网络状态
export function getNetworkStatus() {
  return { ...networkStatus }
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
  CONFIG
}
