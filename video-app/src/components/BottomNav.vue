<template>
  <nav class="bottom-nav" aria-label="Bottom navigation / 底部导航">
    <ul class="nav-items">
      <li v-for="item in navItems" :key="item.path" class="nav-item-wrapper">
        <router-link 
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </li>
    </ul>
  </nav>
</template>

<script>
export default {
  name: 'BottomNav',
  data() {
    return {
      navItems: [
        { path: '/', icon: '🏠', label: '首页' },
        { path: '/darkweb', icon: '🌐', label: '暗网' },
        { path: '/live', icon: '📺', label: '直播' },
        { path: '/games', icon: '🎮', label: '游戏' },
        { path: '/profile', icon: '👤', label: '我的' }
      ]
    }
  },
  methods: {
    isActive(path) {
      if (path === '/') {
        return this.$route.path === '/' || 
               this.$route.path.startsWith('/category') ||
               this.$route.path.startsWith('/search')
      }
      return this.$route.path.startsWith(path)
    }
  }
}
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(26, 26, 46, 0.98);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding: 8px 0;
  padding-bottom: calc(8px + env(safe-area-inset-bottom));
  z-index: 1000;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.nav-items {
  display: flex;
  justify-content: space-around;
  align-items: center;
  width: 100%;
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item-wrapper {
  flex: 1;
  display: flex;
  justify-content: center;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 5px 15px;
  color: #888;
  text-decoration: none;
  transition: all 0.3s;
  min-width: 60px;
}

.nav-item.active {
  color: #00d4ff;
}

.nav-item:hover {
  color: #00d4ff;
}

.nav-icon {
  font-size: 1.4em;
  margin-bottom: 3px;
}

.nav-label {
  font-size: 0.7em;
  font-weight: 500;
}

/* Mobile responsive */
@media (max-width: 480px) {
  .nav-item {
    padding: 4px 10px;
    min-width: 50px;
  }
  
  .nav-icon {
    font-size: 1.2em;
  }
  
  .nav-label {
    font-size: 0.65em;
  }
}

/* Large screens */
@media (min-width: 768px) {
  .bottom-nav {
    display: none;
  }
}
</style>
