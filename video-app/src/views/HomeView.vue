<template>
  <div class="home">
    <!-- Header -->
    <header class="header">
      <h1 class="logo">🎬 视频播放器</h1>
      <p class="stats" v-if="statistics.total_videos">
        共 {{ statistics.total_videos }} 个视频 | {{ statistics.total_plays }} 次播放
      </p>
    </header>

    <!-- Controls -->
    <div class="controls">
      <div class="search-box">
        <input
          v-model="searchKeyword"
          type="text"
          placeholder="搜索视频..."
          @keyup.enter="handleSearch"
        />
        <button class="search-btn" @click="handleSearch">🔍</button>
      </div>
      
      <select v-model="selectedCategory" @change="handleCategoryChange">
        <option value="">全部分类</option>
        <option v-for="cat in categories" :key="cat.video_category" :value="cat.video_category">
          {{ cat.video_category }} ({{ cat.video_count }})
        </option>
      </select>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <p>{{ errorMessage }}</p>
      <button class="btn btn-primary" @click="loadVideos">重试</button>
    </div>

    <!-- Empty State -->
    <div v-else-if="videos.length === 0" class="empty-state">
      <div class="empty-icon">📭</div>
      <p>暂无视频</p>
    </div>

    <!-- Video Grid -->
    <div v-else class="video-grid">
      <VideoCard
        v-for="video in videos"
        :key="video.video_id"
        :video="video"
        @click="playVideo"
      />
    </div>

    <!-- Load More -->
    <div v-if="hasMore && !loading" class="load-more">
      <button class="btn btn-secondary" @click="loadMore">
        加载更多
      </button>
    </div>
  </div>
</template>

<script>
import VideoCard from '@/components/VideoCard.vue'
import { videoApi } from '@/api'
import { 
  saveScrollPosition, 
  restoreScrollPosition, 
  getCurrentScrollPosition,
  hasScrollPosition
} from '@/utils/scrollManager'

export default {
  name: 'HomeView',
  components: {
    VideoCard
  },
  data() {
    return {
      videos: [],
      categories: [],
      statistics: {},
      searchKeyword: '',
      selectedCategory: '',
      loading: true,
      error: false,
      errorMessage: '',
      page: 1,
      limit: 20,
      hasMore: true,
      // Flag to track if we should restore scroll position
      shouldRestoreScroll: false
    }
  },
  watch: {
    '$route'(to, from) {
      // Mark that we should restore scroll when returning from player
      if (from.name === 'player' && (to.name === 'home' || to.name === 'category' || to.name === 'search')) {
        this.shouldRestoreScroll = true
      }
      
      if (to.name === 'category') {
        this.selectedCategory = to.params.category || ''
        this.loadVideos()
      } else if (to.name === 'search') {
        this.searchKeyword = to.query.q || ''
        this.handleSearch()
      }
    }
  },
  mounted() {
    this.init()
  },
  activated() {
    // Restore scroll position when component is activated (from keep-alive cache)
    // Use robust restoration with multiple attempts for app environments
    if (this.shouldRestoreScroll) {
      this.shouldRestoreScroll = false
      // Get the route path to use as key
      const routePath = this.$route.fullPath
      
      // Only restore if we have a saved position for this route
      if (hasScrollPosition(routePath)) {
        // Use nextTick to ensure DOM is ready, then restore with retry mechanism
        // The initialDelay and extra attempts help with mobile browsers and WebViews
        // where rendering may be delayed after keep-alive reactivation
        this.$nextTick(() => {
          // Use requestAnimationFrame for better timing with browser paint cycle
          requestAnimationFrame(() => {
            restoreScrollPosition(routePath, { 
              initialDelay: 0, 
              maxAttempts: 8 
            })
          })
        })
      }
    }
  },
  deactivated() {
    // Save scroll position when component is deactivated (before navigating away)
    const routePath = this.$route.fullPath
    const scrollY = getCurrentScrollPosition()
    saveScrollPosition(routePath, scrollY)
  },
  beforeRouteLeave(to, from, next) {
    // Also save scroll position when leaving via router navigation
    // This ensures position is saved even in scenarios where deactivated isn't called first
    if (to.name === 'player') {
      const routePath = from.fullPath
      const scrollY = getCurrentScrollPosition()
      saveScrollPosition(routePath, scrollY)
    }
    next()
  },
  methods: {
    async init() {
      // Check route params
      if (this.$route.name === 'category') {
        this.selectedCategory = this.$route.params.category || ''
      } else if (this.$route.name === 'search') {
        this.searchKeyword = this.$route.query.q || ''
      }
      
      await Promise.all([
        this.loadVideos(),
        this.loadCategories(),
        this.loadStatistics()
      ])
    },
    
    async loadVideos() {
      this.loading = true
      this.error = false
      this.page = 1
      
      try {
        const params = {
          limit: this.limit,
          offset: 0
        }
        
        let result
        if (this.searchKeyword) {
          result = await videoApi.searchVideos(this.searchKeyword, this.limit)
        } else if (this.selectedCategory) {
          result = await videoApi.getVideosByCategory(this.selectedCategory, this.limit)
        } else {
          result = await videoApi.getVideos(params)
        }
        
        this.videos = result.data || result || []
        this.hasMore = this.videos.length >= this.limit
      } catch (e) {
        this.error = true
        this.errorMessage = '加载视频失败，请稍后重试'
        console.error('Load videos error:', e)
      } finally {
        this.loading = false
      }
    },
    
    async loadMore() {
      if (this.loading) return
      
      this.page++
      const offset = (this.page - 1) * this.limit
      
      try {
        let result
        if (this.searchKeyword) {
          // Use offset pagination for search
          result = await videoApi.searchVideos(this.searchKeyword, this.limit, offset)
          const newVideos = result.data || result || []
          this.videos = [...this.videos, ...newVideos]
          this.hasMore = newVideos.length >= this.limit
        } else if (this.selectedCategory) {
          // Use offset pagination for category
          result = await videoApi.getVideosByCategory(this.selectedCategory, this.limit, offset)
          const newVideos = result.data || result || []
          this.videos = [...this.videos, ...newVideos]
          this.hasMore = newVideos.length >= this.limit
        } else {
          const params = {
            limit: this.limit,
            offset: offset
          }
          result = await videoApi.getVideos(params)
          const newVideos = result.data || result || []
          this.videos = [...this.videos, ...newVideos]
          this.hasMore = newVideos.length >= this.limit
        }
      } catch (e) {
        console.error('Load more error:', e)
      }
    },
    
    async loadCategories() {
      try {
        const result = await videoApi.getCategories()
        this.categories = result.data || result || []
      } catch (e) {
        console.error('Load categories error:', e)
      }
    },
    
    async loadStatistics() {
      try {
        const result = await videoApi.getStatistics()
        this.statistics = result.data || result || {}
      } catch (e) {
        console.error('Load statistics error:', e)
      }
    },
    
    handleSearch() {
      if (this.searchKeyword.trim()) {
        this.$router.push({ name: 'search', query: { q: this.searchKeyword } })
      }
      this.loadVideos()
    },
    
    handleCategoryChange() {
      if (this.selectedCategory) {
        this.$router.push({ name: 'category', params: { category: this.selectedCategory } })
      } else {
        this.$router.push({ name: 'home' })
      }
      this.loadVideos()
    },
    
    playVideo(video) {
      this.$router.push({ name: 'player', params: { id: video.video_id } })
    }
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  text-align: center;
  padding: 30px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 30px;
}

.logo {
  font-size: 2em;
  margin-bottom: 10px;
  background: linear-gradient(90deg, #00d4ff, #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stats {
  color: #8b8b8b;
  font-size: 0.9em;
}

.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 30px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
}

.search-box {
  flex: 1;
  min-width: 200px;
  display: flex;
  gap: 10px;
}

.search-box input {
  flex: 1;
  padding: 12px 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  font-size: 14px;
  outline: none;
  transition: all 0.3s;
}

.search-box input:focus {
  border-color: #00d4ff;
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
}

.search-box input::placeholder {
  color: #888;
}

.search-btn {
  padding: 12px 20px;
  background: linear-gradient(90deg, #00d4ff, #7c3aed);
  border: none;
  border-radius: 8px;
  color: #fff;
  cursor: pointer;
  transition: all 0.3s;
}

.search-btn:hover {
  transform: translateY(-2px);
}

.controls select {
  padding: 12px 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  font-size: 14px;
  outline: none;
  cursor: pointer;
  min-width: 150px;
}

.controls select option {
  background: #1a1a2e;
  color: #fff;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.loading-state p,
.error-state p,
.empty-state p {
  margin-top: 15px;
  color: #888;
}

.error-icon,
.empty-icon {
  font-size: 4em;
}

.error-state .btn {
  margin-top: 20px;
}

.load-more {
  text-align: center;
  padding: 30px;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .home {
    padding: 15px;
  }
  
  .logo {
    font-size: 1.5em;
  }
  
  .controls {
    padding: 15px;
  }
  
  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 15px;
  }
}

/* Small mobile devices */
@media (max-width: 480px) {
  .home {
    padding: 10px;
  }
  
  .header {
    padding: 20px 0;
    margin-bottom: 20px;
  }
  
  .logo {
    font-size: 1.3em;
  }
  
  .stats {
    font-size: 0.8em;
  }
  
  .controls {
    padding: 12px;
    gap: 10px;
  }
  
  .search-box {
    min-width: 100%;
  }
  
  .search-box input {
    padding: 10px 15px;
    font-size: 13px;
  }
  
  .search-btn {
    padding: 10px 15px;
  }
  
  .controls select {
    padding: 10px 15px;
    font-size: 13px;
    min-width: 100%;
  }
  
  .video-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
  
  .loading-state,
  .error-state,
  .empty-state {
    padding: 40px 15px;
  }
  
  .error-icon,
  .empty-icon {
    font-size: 3em;
  }
  
  .load-more {
    padding: 20px;
  }
}

/* Large tablets and small desktops */
@media (min-width: 769px) and (max-width: 1024px) {
  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 20px;
  }
}

/* Large desktops */
@media (min-width: 1400px) {
  .home {
    max-width: 1600px;
    padding: 30px;
  }
  
  .header {
    padding: 40px 0;
  }
  
  .logo {
    font-size: 2.5em;
  }
  
  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 30px;
  }
}
</style>
