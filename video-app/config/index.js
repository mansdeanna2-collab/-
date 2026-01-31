/**
 * 全局配置文件
 * 用于管理应用的全局配置项
 */

// 应用基础配置
export const APP_CONFIG = {
  // 应用名称
  name: '视频播放器',
  
  // 版本号
  version: '1.0.0',
  
  // 应用描述
  description: '视频播放器应用，支持H5和移动端App打包'
}

// API 配置
export const API_CONFIG = {
  // 开发环境 API 地址
  development: {
    baseUrl: 'http://103.74.193.179:5000/api',
    timeout: 30000
  },
  
  // 生产环境 API 地址
  production: {
    baseUrl: 'http://103.74.193.179:5000/api',
    timeout: 30000
  },
  
  // 获取当前环境的 API 配置
  get current() {
    // #ifdef H5
    // H5 环境使用相对路径，由 nginx 代理
    return {
      baseUrl: '/api',
      timeout: this.production.timeout
    }
    // #endif
    
    // #ifdef APP-PLUS
    // App 环境需要完整 URL
    const isDev = process.env.NODE_ENV === 'development'
    return isDev ? this.development : this.production
    // #endif
    
    // 默认返回开发环境配置
    return this.development
  }
}

// 分页配置
export const PAGINATION_CONFIG = {
  // 默认每页数量
  defaultPageSize: 20,
  
  // 可选的每页数量
  pageSizeOptions: [10, 20, 50, 100],
  
  // 触底加载距离
  onReachBottomDistance: 100
}

// 视频播放器配置
export const VIDEO_CONFIG = {
  // 是否自动播放
  autoplay: false,
  
  // 是否显示控制栏
  controls: true,
  
  // 是否循环播放
  loop: false,
  
  // 是否静音
  muted: false,
  
  // 播放器宽高比
  aspectRatio: 16 / 9,
  
  // 默认封面
  defaultPoster: '/static/images/default-poster.png'
}

// 缓存配置
export const CACHE_CONFIG = {
  // 缓存键名前缀
  prefix: 'video_app_',
  
  // 搜索历史
  searchHistory: {
    key: 'search_history',
    maxItems: 20
  },
  
  // 播放历史
  playHistory: {
    key: 'play_history',
    maxItems: 100
  },
  
  // 用户偏好设置
  userPreferences: {
    key: 'user_preferences'
  }
}

// 主题配置
export const THEME_CONFIG = {
  // 主色调
  primaryColor: '#00d4ff',
  
  // 次要色调
  secondaryColor: '#7c3aed',
  
  // 背景色
  backgroundColor: '#0a0a1a',
  
  // 卡片背景色
  cardBackgroundColor: 'rgba(255, 255, 255, 0.05)',
  
  // 文字颜色
  textColor: '#ffffff',
  
  // 次要文字颜色
  textSecondaryColor: '#8b8b8b',
  
  // 边框颜色
  borderColor: 'rgba(255, 255, 255, 0.1)',
  
  // 导航栏背景色
  navBarBackgroundColor: '#1a1a2e',
  
  // 成功色
  successColor: '#10b981',
  
  // 警告色
  warningColor: '#f59e0b',
  
  // 错误色
  errorColor: '#ef4444',
  
  // 金币色
  coinColor: '#ffd700'
}

// 错误消息配置
export const ERROR_MESSAGES = {
  network: '网络连接失败，请检查网络设置',
  timeout: '请求超时，请稍后重试',
  server: '服务器繁忙，请稍后重试',
  notFound: '请求的资源不存在',
  unauthorized: '登录已过期，请重新登录',
  unknown: '发生未知错误，请稍后重试'
}

// 提示消息配置
export const TOAST_MESSAGES = {
  loading: '加载中...',
  saving: '保存中...',
  success: '操作成功',
  failed: '操作失败',
  copied: '已复制到剪贴板',
  networkError: '网络异常，请检查网络连接'
}

// 正则表达式配置
export const REGEX_CONFIG = {
  // 手机号
  phone: /^1[3-9]\d{9}$/,
  
  // 邮箱
  email: /^[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$/,
  
  // URL
  url: /^https?:\/\/.+/,
  
  // 中文
  chinese: /[\u4e00-\u9fa5]/
}

// 导出默认配置
export default {
  APP_CONFIG,
  API_CONFIG,
  PAGINATION_CONFIG,
  VIDEO_CONFIG,
  CACHE_CONFIG,
  THEME_CONFIG,
  ERROR_MESSAGES,
  TOAST_MESSAGES,
  REGEX_CONFIG
}
