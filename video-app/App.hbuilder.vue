<template>
  <view class="app">
    <!-- #ifdef H5 -->
    <router-view></router-view>
    <!-- #endif -->
    <!-- #ifndef H5 -->
    <!-- uni-app pages are managed by pages.json -->
    <!-- #endif -->
  </view>
</template>

<script>
import { API_CONFIG, APP_CONFIG } from '@/config'

export default {
  name: 'App',
  
  globalData: {
    // API 基础地址
    apiBaseUrl: API_CONFIG.current.baseUrl,
    
    // 应用版本
    version: APP_CONFIG.version,
    
    // 用户信息
    userInfo: null,
    
    // 系统信息
    systemInfo: null,
    
    // 状态栏高度
    statusBarHeight: 0,
    
    // 导航栏高度
    navBarHeight: 44,
    
    // 是否已初始化
    isInitialized: false
  },
  
  onLaunch() {
    console.log('App Launch - Version:', APP_CONFIG.version)
    
    // 初始化应用
    this.initApp()
  },
  
  onShow() {
    console.log('App Show')
  },
  
  onHide() {
    console.log('App Hide')
  },
  
  onError(error) {
    console.error('App Error:', error)
    // 可以在这里上报错误日志
  },
  
  methods: {
    /**
     * 初始化应用
     */
    async initApp() {
      try {
        // 获取系统信息
        await this.getSystemInfo()
        
        // 设置状态栏样式
        this.setStatusBarStyle()
        
        // 检查更新
        this.checkUpdate()
        
        // 标记初始化完成
        this.globalData.isInitialized = true
        
        console.log('App initialized successfully')
      } catch (error) {
        console.error('App initialization failed:', error)
      }
    },
    
    /**
     * 获取系统信息
     */
    getSystemInfo() {
      return new Promise((resolve) => {
        try {
          const systemInfo = uni.getSystemInfoSync()
          this.globalData.systemInfo = systemInfo
          this.globalData.statusBarHeight = systemInfo.statusBarHeight || 20
          
          // #ifdef MP-WEIXIN
          // 微信小程序获取胶囊按钮位置
          const menuButtonInfo = uni.getMenuButtonBoundingClientRect()
          this.globalData.navBarHeight = menuButtonInfo.bottom + menuButtonInfo.top - systemInfo.statusBarHeight
          // #endif
          
          resolve(systemInfo)
        } catch (error) {
          console.error('Get system info failed:', error)
          resolve(null)
        }
      })
    },
    
    /**
     * 设置状态栏样式
     */
    setStatusBarStyle() {
      // #ifdef APP-PLUS
      try {
        plus.navigator.setStatusBarStyle('light')
        plus.navigator.setStatusBarBackground('#1a1a2e')
      } catch (e) {
        console.warn('Set status bar style failed:', e)
      }
      // #endif
    },
    
    /**
     * 检查应用更新
     */
    checkUpdate() {
      // #ifdef APP-PLUS
      // App 端可以在这里检查热更新
      // #endif
      
      // #ifdef MP-WEIXIN
      // 微信小程序检查更新
      if (uni.canIUse('getUpdateManager')) {
        const updateManager = uni.getUpdateManager()
        
        updateManager.onCheckForUpdate((res) => {
          if (res.hasUpdate) {
            console.log('发现新版本')
          }
        })
        
        updateManager.onUpdateReady(() => {
          uni.showModal({
            title: '更新提示',
            content: '新版本已经准备好，是否重启应用？',
            success: (res) => {
              if (res.confirm) {
                updateManager.applyUpdate()
              }
            }
          })
        })
        
        updateManager.onUpdateFailed(() => {
          console.error('新版本下载失败')
        })
      }
      // #endif
    }
  }
}
</script>

<style>
/* 全局样式 */
page {
  background-color: #0a0a1a;
  color: #ffffff;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans SC', sans-serif;
  font-size: 28rpx;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 盒模型 */
view, text, image, button, input, textarea, scroll-view {
  box-sizing: border-box;
}

/* #ifndef H5 */
/* 非 H5 平台隐藏滚动条 */
::-webkit-scrollbar {
  display: none;
  width: 0;
  height: 0;
  color: transparent;
}
/* #endif */

/* 重置按钮样式 */
button {
  margin: 0;
  padding: 0;
  background: transparent;
  border: none;
  line-height: inherit;
  font-size: inherit;
  color: inherit;
}

button::after {
  border: none;
}

/* 输入框样式 */
input {
  box-sizing: border-box;
}

input::placeholder {
  color: #666;
}

/* 图片默认样式 */
image {
  display: block;
  max-width: 100%;
}

/* 文本溢出省略 */
.text-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.text-ellipsis-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.text-ellipsis-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Flex 布局助手 */
.flex {
  display: flex;
}

.flex-row {
  display: flex;
  flex-direction: row;
}

.flex-col {
  display: flex;
  flex-direction: column;
}

.flex-wrap {
  flex-wrap: wrap;
}

.flex-1 {
  flex: 1;
}

.items-center {
  align-items: center;
}

.justify-center {
  justify-content: center;
}

.justify-between {
  justify-content: space-between;
}

.justify-around {
  justify-content: space-around;
}

/* 安全区域适配 */
.safe-area-bottom {
  padding-bottom: constant(safe-area-inset-bottom);
  padding-bottom: env(safe-area-inset-bottom);
}

.safe-area-top {
  padding-top: constant(safe-area-inset-top);
  padding-top: env(safe-area-inset-top);
}

/* 滚动条样式 (H5) */
/* #ifdef H5 */
::-webkit-scrollbar {
  display: block;
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
/* #endif */
</style>
