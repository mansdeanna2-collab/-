<template>
  <div class="category-view">
    <!-- Category Header -->
    <header class="category-header">
      <button class="back-btn" @click="goBack">
        <span class="back-icon">←</span>
      </button>
      <h1 class="category-title">{{ categoryName }}</h1>
      <div class="header-spacer"></div>
    </header>

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

    <!-- Videos Grid -->
    <div v-else class="main-content">
      <div class="videos-grid" v-if="videos.length > 0">
        <VideoCard
          v-for="video in videos"
          :key="video.video_id"
          :video="video"
          @click="playVideo"
        />
      </div>

      <!-- Empty State -->
      <div v-if="videos.length === 0 && !loading" class="empty-state">
        <div class="empty-icon">📹</div>
        <p>该分类暂无视频</p>
        <button class="btn btn-primary" @click="goBack">返回首页</button>
      </div>

      <!-- Load More -->
      <div v-if="hasMore || loadingMore" class="load-more">
        <button 
          class="btn btn-secondary" 
          @click="loadMore"
          :disabled="loadingMore"
        >
          <span v-if="loadingMore" class="loading-spinner small"></span>
          {{ loadingMore ? '加载中...' : '加载更多' }}
        </button>
      </div>
    </div>

    <!-- Bottom spacing for nav bar -->
    <div class="bottom-spacer"></div>
  </div>
</template>

<script>
import VideoCard from '@/components/VideoCard.vue'
import { videoApi } from '@/api'
import { extractArrayData } from '@/utils/apiUtils'

export default {
  name: 'CategoryView',
  components: {
    VideoCard
  },
  data() {
    return {
      videos: [],
      loading: true,
      loadingMore: false,
      error: false,
      errorMessage: '',
      page: 1,
      limit: 20,
      hasMore: true
    }
  },
  computed: {
    categoryName() {
      return this.$route.params.category || '分类'
    }
  },
  watch: {
    '$route.params.category': {
      handler(newCategory) {
        if (newCategory) {
          this.loadVideos()
        }
      }
    }
  },
  mounted() {
    this.loadVideos()
  },
  methods: {
    goBack() {
      this.$router.push({ name: 'home' })
    },
    
    async loadVideos() {
      this.loading = true
      this.error = false
      this.page = 1
      this.videos = []
      
      try {
        const result = await videoApi.getVideosByCategory(this.categoryName, this.limit)
        const videos = extractArrayData(result)
        // Use actual API results - empty array is valid
        this.videos = videos
        this.hasMore = this.videos.length >= this.limit
      } catch (e) {
        console.error('Load category videos error:', e)
        this.error = true
        this.errorMessage = e.userMessage || '加载失败，请重试'
        this.hasMore = false
      } finally {
        this.loading = false
      }
    },
    
    async loadMore() {
      if (this.loading || this.loadingMore) return
      
      this.loadingMore = true
      this.page++
      const offset = (this.page - 1) * this.limit
      
      try {
        const result = await videoApi.getVideosByCategory(this.categoryName, this.limit, offset)
        const newVideos = extractArrayData(result)
        this.videos = [...this.videos, ...newVideos]
        this.hasMore = newVideos.length >= this.limit
      } catch (e) {
        console.error('Load more error:', e)
      } finally {
        this.loadingMore = false
      }
    },
    
    playVideo(video) {
      this.$router.push({ name: 'player', params: { id: video.video_id } })
    }
  }
}
</script>

<style scoped>
.category-view {
  min-height: 100vh;
  padding: 0 15px;
  max-width: 1400px;
  margin: 0 auto;
}

/* Category Header */
.category-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 15px;
  background: rgba(26, 26, 46, 0.98);
  z-index: 100;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  color: #fff;
  font-size: 1.2em;
  cursor: pointer;
  transition: all 0.3s;
}

.back-btn:hover {
  background: rgba(0, 212, 255, 0.2);
  color: #00d4ff;
}

.back-icon {
  font-size: 1.2em;
}

.category-title {
  flex: 1;
  text-align: center;
  font-size: 1.2em;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.header-spacer {
  width: 40px;
}

/* Main Content */
.main-content {
  padding-top: 80px;
  padding-bottom: 20px;
}

/* Videos Grid */
.videos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

/* States */
.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120px 20px;
  text-align: center;
}

.loading-state p,
.error-state p {
  margin-top: 15px;
  color: #888;
}

.error-icon {
  font-size: 4em;
}

.error-state .btn {
  margin-top: 20px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-state .empty-icon {
  font-size: 4em;
  margin-bottom: 15px;
}

.empty-state p {
  color: #888;
  margin-bottom: 20px;
}

/* Load More */
.load-more {
  text-align: center;
  padding: 20px;
}

.load-more .btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.loading-spinner {
  width: 30px;
  height: 30px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #00d4ff;
  animation: spin 1s ease-in-out infinite;
}

.loading-spinner.small {
  width: 16px;
  height: 16px;
  border-width: 2px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Button styles */
.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 25px;
  font-size: 1em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: linear-gradient(90deg, #00d4ff, #7c3aed);
  color: #fff;
}

.btn-primary:hover {
  filter: brightness(1.1);
  transform: translateY(-2px);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Bottom spacer for nav bar */
.bottom-spacer {
  height: 70px;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .category-view {
    padding: 0 12px;
  }
  
  .category-header {
    padding: 10px 12px;
  }
  
  .back-btn {
    width: 36px;
    height: 36px;
    font-size: 1em;
  }
  
  .category-title {
    font-size: 1.1em;
  }
  
  .header-spacer {
    width: 36px;
  }
  
  .main-content {
    padding-top: 70px;
  }
  
  .videos-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }
}

/* Small mobile devices */
@media (max-width: 480px) {
  .category-view {
    padding: 0 10px;
  }
  
  .category-header {
    padding: 10px;
  }
  
  .back-btn {
    width: 32px;
    height: 32px;
  }
  
  .category-title {
    font-size: 1em;
  }
  
  .header-spacer {
    width: 32px;
  }
  
  .main-content {
    padding-top: 65px;
  }
  
  .videos-grid {
    gap: 10px;
  }
  
  .bottom-spacer {
    height: 60px;
  }
}

/* Large desktops */
@media (min-width: 1400px) {
  .category-view {
    max-width: 1600px;
    padding: 0 30px;
  }
  
  .category-header {
    padding: 15px 30px;
  }
  
  .category-title {
    font-size: 1.4em;
  }
}
</style>
