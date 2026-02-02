<template>
  <div class="page-container">
    <div class="page-header">
      <h1>{{ title }}</h1>
      <p class="subtitle">{{ subtitle }}</p>
    </div>
    
    <div class="profile-card" @click="handleProfileClick">
      <div class="avatar">
        <span>{{ isLoggedIn ? userInfo.avatar : '👤' }}</span>
      </div>
      <div class="user-info">
        <h2>{{ isLoggedIn ? userInfo.nickname : '游客用户' }}</h2>
        <p>{{ isLoggedIn ? `金币: ${userInfo.coins}` : '点击登录获取更多功能' }}</p>
      </div>
      <span class="profile-arrow">→</span>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <div class="stat-card" @click="showWatchHistory">
        <span class="stat-number">{{ stats.watchCount }}</span>
        <span class="stat-label">观看记录</span>
      </div>
      <div class="stat-card" @click="showFavorites">
        <span class="stat-number">{{ stats.favoriteCount }}</span>
        <span class="stat-label">我的收藏</span>
      </div>
      <div class="stat-card" @click="showCoins">
        <span class="stat-number">{{ stats.coins }}</span>
        <span class="stat-label">金币余额</span>
      </div>
    </div>
    
    <ul class="menu-list">
      <li class="menu-item" @click="openAdmin">
        <span class="menu-icon">🛠️</span>
        <span class="menu-text">管理后台</span>
        <span class="menu-arrow">→</span>
      </li>
      <li class="menu-item" @click="showWatchHistory">
        <span class="menu-icon">📜</span>
        <span class="menu-text">观看历史</span>
        <span class="menu-badge" v-if="stats.watchCount > 0">{{ stats.watchCount }}</span>
        <span class="menu-arrow">→</span>
      </li>
      <li class="menu-item" @click="showFavorites">
        <span class="menu-icon">⭐</span>
        <span class="menu-text">我的收藏</span>
        <span class="menu-badge" v-if="stats.favoriteCount > 0">{{ stats.favoriteCount }}</span>
        <span class="menu-arrow">→</span>
      </li>
      <li class="menu-item" @click="showCoins">
        <span class="menu-icon">💰</span>
        <span class="menu-text">我的金币</span>
        <span class="menu-badge coins" v-if="stats.coins > 0">{{ stats.coins }}</span>
        <span class="menu-arrow">→</span>
      </li>
      <li class="menu-item" @click="openSettings">
        <span class="menu-icon">⚙️</span>
        <span class="menu-text">设置</span>
        <span class="menu-arrow">→</span>
      </li>
      <li class="menu-item" @click="openHelp">
        <span class="menu-icon">❓</span>
        <span class="menu-text">帮助与反馈</span>
        <span class="menu-arrow">→</span>
      </li>
      <li class="menu-item" @click="clearCache">
        <span class="menu-icon">🗑️</span>
        <span class="menu-text">清除缓存</span>
        <span class="menu-arrow">→</span>
      </li>
    </ul>

    <!-- App Info -->
    <div class="app-info">
      <p>悟空视频 v1.0.0</p>
      <p class="copyright">© 2026 WuKong Video</p>
    </div>

    <!-- Toast Message -->
    <transition name="toast">
      <div v-if="toastMessage" class="toast-message">
        {{ toastMessage }}
      </div>
    </transition>
  </div>
</template>

<script>
import { videoApi } from '@/api'

export default {
  name: 'ProfileView',
  data() {
    return {
      title: '个人中心',
      subtitle: '管理您的账户',
      isLoggedIn: false,
      userInfo: {
        nickname: '游客用户',
        avatar: '👤',
        coins: 0
      },
      stats: {
        watchCount: 0,
        favoriteCount: 0,
        coins: 0
      },
      toastMessage: ''
    }
  },
  mounted() {
    this.loadUserStats()
  },
  methods: {
    loadUserStats() {
      // Load from local storage
      const watchHistory = JSON.parse(window.localStorage.getItem('watchHistory') || '[]')
      const favorites = JSON.parse(window.localStorage.getItem('favorites') || '[]')
      const coins = parseInt(window.localStorage.getItem('userCoins') || '0', 10)
      
      this.stats = {
        watchCount: watchHistory.length,
        favoriteCount: favorites.length,
        coins: coins
      }
    },
    handleProfileClick() {
      this.showToast('登录功能即将上线')
    },
    showWatchHistory() {
      this.showToast('观看历史功能即将上线')
    },
    showFavorites() {
      this.showToast('收藏功能即将上线')
    },
    showCoins() {
      this.showToast('金币商城即将上线')
    },
    openAdmin() {
      this.$router.push('/admin')
    },
    openSettings() {
      this.showToast('设置功能即将上线')
    },
    openHelp() {
      this.showToast('帮助中心即将上线')
    },
    clearCache() {
      // Clear API cache
      videoApi.clearCache()
      // Clear local storage cache
      window.localStorage.removeItem('watchHistory')
      window.localStorage.removeItem('favorites')
      
      this.stats = {
        watchCount: 0,
        favoriteCount: 0,
        coins: this.stats.coins
      }
      
      this.showToast('缓存已清除')
    },
    showToast(message) {
      this.toastMessage = message
      setTimeout(() => {
        this.toastMessage = ''
      }, 2000)
    }
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  padding: 20px;
  padding-bottom: 80px;
  max-width: 600px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  padding: 20px 0;
  margin-bottom: 20px;
}

.page-header h1 {
  font-size: 1.5em;
  margin-bottom: 5px;
  color: #fff;
}

.subtitle {
  color: #888;
  font-size: 0.85em;
}

.profile-card {
  display: flex;
  align-items: center;
  gap: 15px;
  background: rgba(255, 255, 255, 0.05);
  padding: 20px;
  border-radius: 15px;
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.profile-card:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-2px);
}

.profile-card:active {
  transform: translateY(0);
}

.profile-arrow {
  color: #888;
  font-size: 1.2em;
  transition: transform 0.3s;
}

.profile-card:hover .profile-arrow {
  transform: translateX(5px);
}

.avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(90deg, #00d4ff, #7c3aed);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8em;
  flex-shrink: 0;
}

.user-info {
  flex: 1;
}

.user-info h2 {
  font-size: 1.1em;
  margin-bottom: 5px;
  color: #fff;
}

.user-info p {
  font-size: 0.85em;
  color: #888;
}

/* Statistics Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 20px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 15px 10px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-card:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: #00d4ff;
  transform: translateY(-3px);
}

.stat-card:active {
  transform: translateY(0);
}

.stat-number {
  display: block;
  font-size: 1.5em;
  font-weight: 700;
  color: #00d4ff;
  margin-bottom: 5px;
}

.stat-label {
  display: block;
  font-size: 0.75em;
  color: #888;
}

.menu-list {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  overflow: hidden;
  list-style: none;
  margin: 0 0 20px 0;
  padding: 0;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: background 0.3s;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.menu-item:active {
  background: rgba(255, 255, 255, 0.08);
}

.menu-icon {
  font-size: 1.2em;
  margin-right: 15px;
}

.menu-text {
  flex: 1;
  color: #fff;
  font-size: 0.95em;
}

.menu-badge {
  background: rgba(0, 212, 255, 0.2);
  color: #00d4ff;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.75em;
  margin-right: 10px;
}

.menu-badge.coins {
  background: rgba(255, 215, 0, 0.2);
  color: #ffd700;
}

.menu-arrow {
  color: #888;
  font-size: 1em;
}

/* App Info */
.app-info {
  text-align: center;
  padding: 20px;
  color: #666;
  font-size: 0.8em;
}

.app-info .copyright {
  margin-top: 5px;
  color: #555;
}

/* Toast Message */
.toast-message {
  position: fixed;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.85);
  color: #fff;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 0.9em;
  z-index: 1000;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}

@media (max-width: 480px) {
  .page-header h1 {
    font-size: 1.3em;
  }
  
  .profile-card {
    padding: 15px;
  }
  
  .avatar {
    width: 50px;
    height: 50px;
    font-size: 1.5em;
  }
  
  .user-info h2 {
    font-size: 1em;
  }
  
  .stats-grid {
    gap: 8px;
  }
  
  .stat-card {
    padding: 12px 8px;
  }
  
  .stat-number {
    font-size: 1.3em;
  }
  
  .stat-label {
    font-size: 0.7em;
  }
  
  .menu-item {
    padding: 12px 15px;
  }
  
  .menu-text {
    font-size: 0.9em;
  }
  
  .toast-message {
    bottom: 80px;
    left: 20px;
    right: 20px;
    transform: none;
    text-align: center;
  }
  
  .toast-enter-from,
  .toast-leave-to {
    transform: translateY(20px);
  }
}
</style>
