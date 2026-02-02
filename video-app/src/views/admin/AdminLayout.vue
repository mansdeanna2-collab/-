<template>
  <div class="admin-layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <h1 class="admin-logo">🎬 管理后台</h1>
      </div>
      
      <nav class="sidebar-nav">
        <router-link 
          v-for="item in menuItems" 
          :key="item.path"
          :to="item.path"
          class="nav-link"
          :class="{ active: isActive(item.path) }"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-text">{{ item.label }}</span>
        </router-link>
      </nav>
      
      <div class="sidebar-footer">
        <router-link to="/" class="back-to-site">
          <span class="nav-icon">🏠</span>
          <span class="nav-text">返回前台</span>
        </router-link>
      </div>
    </aside>
    
    <!-- Main Content -->
    <main class="main-content">
      <header class="content-header">
        <h2 class="page-title">{{ currentPageTitle }}</h2>
      </header>
      
      <div class="content-body">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'AdminLayout',
  data() {
    return {
      menuItems: [
        { path: '/admin/dashboard', icon: '📊', label: '仪表盘' },
        { path: '/admin/nav-categories', icon: '📁', label: '导航分类管理' }
      ]
    }
  },
  computed: {
    currentPageTitle() {
      const currentItem = this.menuItems.find(item => this.isActive(item.path))
      return currentItem ? currentItem.label : '管理后台'
    }
  },
  methods: {
    isActive(path) {
      return this.$route.path === path || this.$route.path.startsWith(path + '/')
    }
  }
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: #0f0f1a;
}

/* Sidebar */
.sidebar {
  width: 240px;
  background: linear-gradient(180deg, #1a1a2e 0%, #16162a 100%);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 100;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.admin-logo {
  font-size: 1.3em;
  font-weight: 700;
  background: linear-gradient(90deg, #00d4ff, #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
}

.sidebar-nav {
  flex: 1;
  padding: 15px 10px;
  overflow-y: auto;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 15px;
  color: #a0a0b0;
  text-decoration: none;
  border-radius: 8px;
  margin-bottom: 5px;
  transition: all 0.3s;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

.nav-link.active {
  background: linear-gradient(90deg, rgba(124, 58, 237, 0.2) 0%, rgba(0, 212, 255, 0.2) 100%);
  color: #00d4ff;
  border-left: 3px solid #00d4ff;
}

.nav-icon {
  font-size: 1.2em;
}

.nav-text {
  font-size: 0.95em;
  font-weight: 500;
}

.sidebar-footer {
  padding: 15px 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.back-to-site {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 15px;
  color: #7c3aed;
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.3s;
}

.back-to-site:hover {
  background: rgba(124, 58, 237, 0.1);
  color: #9f67ff;
}

/* Main Content */
.main-content {
  flex: 1;
  margin-left: 240px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.content-header {
  background: rgba(26, 26, 46, 0.95);
  padding: 20px 30px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: sticky;
  top: 0;
  z-index: 50;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.page-title {
  margin: 0;
  font-size: 1.4em;
  font-weight: 600;
  color: #fff;
}

.content-body {
  flex: 1;
  padding: 25px 30px;
  overflow-y: auto;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .sidebar {
    width: 200px;
  }
  
  .main-content {
    margin-left: 200px;
  }
  
  .content-header {
    padding: 15px 20px;
  }
  
  .page-title {
    font-size: 1.2em;
  }
  
  .content-body {
    padding: 20px;
  }
}

@media (max-width: 576px) {
  .admin-layout {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    position: relative;
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .sidebar-header {
    padding: 15px;
  }
  
  .sidebar-nav {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    padding: 10px;
  }
  
  .nav-link {
    padding: 8px 12px;
    margin-bottom: 0;
  }
  
  .sidebar-footer {
    display: none;
  }
  
  .main-content {
    margin-left: 0;
  }
  
  .content-header {
    padding: 12px 15px;
  }
  
  .content-body {
    padding: 15px;
  }
}
</style>
