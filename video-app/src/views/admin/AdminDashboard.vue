<template>
  <div class="dashboard">
    <!-- Statistics Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">📹</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.total_videos || 0 }}</div>
          <div class="stat-label">视频总数</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">📁</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.total_categories || 0 }}</div>
          <div class="stat-label">视频分类</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">🔗</div>
        <div class="stat-content">
          <div class="stat-value">{{ navCategories.length }}</div>
          <div class="stat-label">导航分类</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">🎬</div>
        <div class="stat-content">
          <div class="stat-value">{{ totalBoundCategories }}</div>
          <div class="stat-label">已绑定分类</div>
        </div>
      </div>
    </div>
    
    <!-- Quick Links -->
    <div class="quick-links">
      <h3 class="section-title">快捷操作</h3>
      <div class="links-grid">
        <router-link to="/admin/nav-categories" class="quick-link">
          <span class="link-icon">📁</span>
          <span class="link-text">管理导航分类</span>
        </router-link>
        <router-link to="/" class="quick-link">
          <span class="link-icon">🌐</span>
          <span class="link-text">查看前台效果</span>
        </router-link>
      </div>
    </div>
    
    <!-- Navigation Categories Overview -->
    <div class="nav-overview">
      <h3 class="section-title">导航分类概览</h3>
      <div class="nav-cards">
        <div 
          v-for="navCat in navCategories" 
          :key="navCat.key"
          class="nav-card"
        >
          <div class="nav-card-header">
            <span class="nav-name">{{ navCat.label }}</span>
            <span class="nav-count">{{ navCat.subcategories.length }} 个分类</span>
          </div>
          <div class="nav-card-body">
            <div class="subcategory-tags">
              <span 
                v-for="sub in navCat.subcategories.slice(0, 4)" 
                :key="sub"
                class="subcategory-tag"
              >
                {{ sub }}
              </span>
              <span 
                v-if="navCat.subcategories.length > 4"
                class="subcategory-more"
              >
                +{{ navCat.subcategories.length - 4 }} 更多
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { videoApi } from '@/api'
import { getNavCategories } from '@/utils/navCategoryManager'

export default {
  name: 'AdminDashboard',
  data() {
    return {
      stats: {},
      navCategories: [],
      loading: true
    }
  },
  computed: {
    totalBoundCategories() {
      return this.navCategories.reduce((sum, nav) => sum + nav.subcategories.length, 0)
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    async loadData() {
      this.loading = true
      try {
        // Load statistics from API
        const statsResult = await videoApi.getStatistics()
        if (statsResult && statsResult.data) {
          this.stats = statsResult.data
        }
      } catch (e) {
        console.error('Load statistics error:', e)
      }
      
      // Load navigation categories from local storage
      this.navCategories = getNavCategories()
      this.loading = false
    }
  }
}
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
}

/* Statistics Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: linear-gradient(135deg, #1a1a2e 0%, #16162a 100%);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.stat-icon {
  font-size: 2.5em;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(124, 58, 237, 0.15);
  border-radius: 12px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 1.8em;
  font-weight: 700;
  color: #fff;
  line-height: 1.2;
}

.stat-label {
  font-size: 0.9em;
  color: #a0a0b0;
  margin-top: 5px;
}

/* Section Title */
.section-title {
  font-size: 1.1em;
  font-weight: 600;
  color: #fff;
  margin: 0 0 15px 0;
  padding-left: 10px;
  border-left: 3px solid #00d4ff;
}

/* Quick Links */
.quick-links {
  margin-bottom: 30px;
}

.links-grid {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.quick-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px 20px;
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.15) 0%, rgba(0, 212, 255, 0.15) 100%);
  border: 1px solid rgba(124, 58, 237, 0.3);
  border-radius: 10px;
  color: #fff;
  text-decoration: none;
  transition: all 0.3s;
}

.quick-link:hover {
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.25) 0%, rgba(0, 212, 255, 0.25) 100%);
  transform: translateY(-2px);
}

.link-icon {
  font-size: 1.3em;
}

.link-text {
  font-weight: 500;
}

/* Navigation Categories Overview */
.nav-overview {
  margin-bottom: 30px;
}

.nav-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 15px;
}

.nav-card {
  background: rgba(26, 26, 46, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 15px;
  transition: all 0.3s;
}

.nav-card:hover {
  border-color: rgba(0, 212, 255, 0.3);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.nav-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-name {
  font-weight: 600;
  color: #fff;
  font-size: 1.05em;
}

.nav-count {
  font-size: 0.85em;
  color: #7c3aed;
}

.nav-card-body {
  min-height: 50px;
}

.subcategory-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.subcategory-tag {
  padding: 4px 10px;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 15px;
  font-size: 0.8em;
  color: #00d4ff;
}

.subcategory-more {
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  font-size: 0.8em;
  color: #888;
}

/* Mobile responsive */
@media (max-width: 576px) {
  .stats-grid {
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
  
  .stat-card {
    padding: 15px;
    flex-direction: column;
    text-align: center;
    gap: 10px;
  }
  
  .stat-icon {
    font-size: 2em;
    width: 50px;
    height: 50px;
  }
  
  .stat-value {
    font-size: 1.5em;
  }
  
  .links-grid {
    flex-direction: column;
  }
  
  .nav-cards {
    grid-template-columns: 1fr;
  }
}
</style>
