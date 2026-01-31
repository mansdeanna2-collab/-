/**
 * 通用工具函数模块
 * 提供格式化、验证、存储等常用功能
 */

/**
 * 格式化播放次数
 * @param {number} count 播放次数
 * @returns {string} 格式化后的字符串
 */
export function formatPlayCount(count) {
  if (!count || count < 0) return '0'
  
  if (count >= 100000000) {
    return (count / 100000000).toFixed(1) + '亿'
  }
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + '万'
  }
  return count.toString()
}

/**
 * 格式化时间
 * @param {number} seconds 秒数
 * @returns {string} 格式化后的时间字符串 (mm:ss 或 hh:mm:ss)
 */
export function formatDuration(seconds) {
  if (!seconds || seconds < 0) return '00:00'
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  const pad = (num) => num.toString().padStart(2, '0')
  
  if (hours > 0) {
    return `${pad(hours)}:${pad(minutes)}:${pad(secs)}`
  }
  return `${pad(minutes)}:${pad(secs)}`
}

/**
 * 格式化日期
 * @param {string|Date} dateStr 日期字符串或对象
 * @param {string} format 格式化模板
 * @returns {string} 格式化后的日期字符串
 */
export function formatDate(dateStr, format = 'YYYY-MM-DD') {
  if (!dateStr) return ''
  
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return dateStr
  
  const year = date.getFullYear()
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const day = date.getDate().toString().padStart(2, '0')
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  const seconds = date.getSeconds().toString().padStart(2, '0')
  
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 相对时间格式化
 * @param {string|Date} dateStr 日期字符串或对象
 * @returns {string} 相对时间描述
 */
export function formatRelativeTime(dateStr) {
  if (!dateStr) return ''
  
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return dateStr
  
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  const months = Math.floor(days / 30)
  const years = Math.floor(days / 365)
  
  if (years > 0) return `${years}年前`
  if (months > 0) return `${months}个月前`
  if (days > 0) return `${days}天前`
  if (hours > 0) return `${hours}小时前`
  if (minutes > 0) return `${minutes}分钟前`
  return '刚刚'
}

/**
 * 防抖函数
 * @param {Function} fn 要防抖的函数
 * @param {number} delay 延迟时间（毫秒）
 * @returns {Function} 防抖后的函数
 */
export function debounce(fn, delay = 300) {
  let timer = null
  return function(...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

/**
 * 节流函数
 * @param {Function} fn 要节流的函数
 * @param {number} interval 间隔时间（毫秒）
 * @returns {Function} 节流后的函数
 */
export function throttle(fn, interval = 300) {
  let lastTime = 0
  return function(...args) {
    const now = Date.now()
    if (now - lastTime >= interval) {
      lastTime = now
      fn.apply(this, args)
    }
  }
}

/**
 * 本地存储封装
 */
export const storage = {
  /**
   * 设置存储
   * @param {string} key 键名
   * @param {any} value 值
   */
  set(key, value) {
    try {
      uni.setStorageSync(key, JSON.stringify(value))
    } catch (e) {
      console.error('Storage set error:', e)
    }
  },
  
  /**
   * 获取存储
   * @param {string} key 键名
   * @param {any} defaultValue 默认值
   * @returns {any} 存储的值
   */
  get(key, defaultValue = null) {
    try {
      const value = uni.getStorageSync(key)
      if (value) {
        return JSON.parse(value)
      }
      return defaultValue
    } catch (e) {
      console.error('Storage get error:', e)
      return defaultValue
    }
  },
  
  /**
   * 移除存储
   * @param {string} key 键名
   */
  remove(key) {
    try {
      uni.removeStorageSync(key)
    } catch (e) {
      console.error('Storage remove error:', e)
    }
  },
  
  /**
   * 清空存储
   */
  clear() {
    try {
      uni.clearStorageSync()
    } catch (e) {
      console.error('Storage clear error:', e)
    }
  }
}

/**
 * 显示加载提示
 * @param {string} title 提示文字
 */
export function showLoading(title = '加载中...') {
  uni.showLoading({
    title,
    mask: true
  })
}

/**
 * 隐藏加载提示
 */
export function hideLoading() {
  uni.hideLoading()
}

/**
 * 显示 Toast 提示
 * @param {string} title 提示文字
 * @param {string} icon 图标类型
 * @param {number} duration 显示时间
 */
export function showToast(title, icon = 'none', duration = 2000) {
  uni.showToast({
    title,
    icon,
    duration
  })
}

/**
 * 显示确认对话框
 * @param {Object} options 配置选项
 * @returns {Promise<boolean>}
 */
export function showConfirm(options = {}) {
  return new Promise((resolve) => {
    uni.showModal({
      title: options.title || '提示',
      content: options.content || '',
      showCancel: options.showCancel !== false,
      cancelText: options.cancelText || '取消',
      confirmText: options.confirmText || '确定',
      success: (res) => {
        resolve(res.confirm)
      },
      fail: () => {
        resolve(false)
      }
    })
  })
}

/**
 * 复制文本到剪贴板
 * @param {string} text 要复制的文本
 * @returns {Promise<boolean>}
 */
export function copyToClipboard(text) {
  return new Promise((resolve) => {
    uni.setClipboardData({
      data: text,
      success: () => {
        resolve(true)
      },
      fail: () => {
        resolve(false)
      }
    })
  })
}

/**
 * 获取系统信息
 * @returns {Object} 系统信息
 */
export function getSystemInfo() {
  try {
    return uni.getSystemInfoSync()
  } catch (e) {
    console.error('Get system info error:', e)
    return {}
  }
}

/**
 * 判断是否为空
 * @param {any} value 要判断的值
 * @returns {boolean}
 */
export function isEmpty(value) {
  if (value === null || value === undefined) return true
  if (typeof value === 'string') return value.trim() === ''
  if (Array.isArray(value)) return value.length === 0
  if (typeof value === 'object') return Object.keys(value).length === 0
  return false
}

/**
 * 生成唯一ID
 * @returns {string}
 */
export function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 11)
}

/**
 * URL 参数解析
 * @param {string} url URL字符串
 * @returns {Object} 参数对象
 */
export function parseUrlParams(url) {
  const params = {}
  const queryString = url.split('?')[1]
  if (!queryString) return params
  
  queryString.split('&').forEach(param => {
    const [key, value] = param.split('=')
    if (key) {
      params[decodeURIComponent(key)] = value ? decodeURIComponent(value) : ''
    }
  })
  
  return params
}

/**
 * 构建 URL 查询字符串
 * @param {Object} params 参数对象
 * @returns {string} 查询字符串
 */
export function buildQueryString(params) {
  if (!params || typeof params !== 'object') return ''
  
  const pairs = []
  for (const key in params) {
    if (params[key] !== undefined && params[key] !== null) {
      pairs.push(`${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
    }
  }
  
  return pairs.length > 0 ? '?' + pairs.join('&') : ''
}

export default {
  formatPlayCount,
  formatDuration,
  formatDate,
  formatRelativeTime,
  debounce,
  throttle,
  storage,
  showLoading,
  hideLoading,
  showToast,
  showConfirm,
  copyToClipboard,
  getSystemInfo,
  isEmpty,
  generateId,
  parseUrlParams,
  buildQueryString
}
