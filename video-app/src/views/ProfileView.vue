<template>
  <div class="page-container">
    <div class="page-header">
      <h1>{{ title }}</h1>
      <p class="subtitle">{{ subtitle }}</p>
    </div>
    
    <div class="profile-card">
      <div class="avatar">
        <span>👤</span>
      </div>
      <div class="user-info">
        <h2>游客用户</h2>
        <p>点击登录获取更多功能</p>
      </div>
    </div>
    
    <div class="menu-list">
      <div class="menu-item">
        <span class="menu-icon">📜</span>
        <span class="menu-text">观看历史</span>
        <span class="menu-arrow">→</span>
      </div>
      <div class="menu-item">
        <span class="menu-icon">⭐</span>
        <span class="menu-text">我的收藏</span>
        <span class="menu-arrow">→</span>
      </div>
      <div class="menu-item">
        <span class="menu-icon">💰</span>
        <span class="menu-text">我的金币</span>
        <span class="menu-arrow">→</span>
      </div>
      <div class="menu-item">
        <span class="menu-icon">⚙️</span>
        <span class="menu-text">设置</span>
        <span class="menu-arrow">→</span>
      </div>
      <div class="menu-item">
        <span class="menu-icon">❓</span>
        <span class="menu-text">帮助与反馈</span>
        <span class="menu-arrow">→</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProfileView',
  data() {
    return {
      title: '个人中心',
      subtitle: '管理您的账户'
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
  transition: background 0.3s;
}

.profile-card:hover {
  background: rgba(255, 255, 255, 0.08);
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

.menu-list {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  overflow: hidden;
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

.menu-icon {
  font-size: 1.2em;
  margin-right: 15px;
}

.menu-text {
  flex: 1;
  color: #fff;
  font-size: 0.95em;
}

.menu-arrow {
  color: #888;
  font-size: 1em;
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
  
  .menu-item {
    padding: 12px 15px;
  }
  
  .menu-text {
    font-size: 0.9em;
  }
}
</style>
