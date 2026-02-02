<template>
  <div class="home">
    <!-- Header with App Name and Search -->
    <header class="header">
      <div class="header-content">
        <h1 class="logo">🎬 悟空视频</h1>
        <div class="search-box">
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="搜索视频..."
            @input="onSearchInput"
            @keyup.enter="handleSearch"
          />
          <button class="search-btn" @click="handleSearch">🔍</button>
        </div>
        <div class="header-spacer"></div>
      </div>
    </header>

    <!-- Category Tabs -->
    <div class="category-tabs">
      <button
        v-for="(cat, index) in displayCategories"
        :key="cat.video_category || index"
        :class="['tab-btn', { active: selectedCategory === cat.video_category }]"
        @click="handleCategoryClick(cat.video_category)"
      >
        {{ cat.label || cat.video_category }}
      </button>
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
      <button class="btn btn-primary" @click="init">重试</button>
    </div>

    <!-- Main Content -->
    <div v-else class="main-content">
      <!-- Carousel Banner -->
      <Carousel 
        v-if="carouselVideos.length > 0"
        :videos="carouselVideos"
        @click="playVideo"
      />

      <!-- Category Sections -->
      <CategorySection
        v-for="cat in categorySections"
        :key="cat.category"
        :title="cat.category"
        :videos="cat.videos"
        @play="playVideo"
        @refresh="refreshCategory(cat.category)"
        @more="viewMoreCategory(cat.category)"
      />

      <!-- Load More (for when viewing a single category or search results) -->
      <div v-if="isFilteredView && (hasMore || loadingMore)" class="load-more">
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
import Carousel from '@/components/Carousel.vue'
import CategorySection from '@/components/CategorySection.vue'
import { videoApi } from '@/api'
import { 
  saveScrollPosition, 
  restoreScrollPosition, 
  getCurrentScrollPosition,
  hasScrollPosition
} from '@/utils/scrollManager'
import { extractArrayData } from '@/utils/apiUtils'
import { 
  getMockCategories, 
  getMockVideosByCategory, 
  getMockTopVideos,
  searchMockVideos
} from '@/utils/mockData'

export default {
  name: 'HomeView',
  components: {
    Carousel,
    CategorySection
  },
  // Constants
  MAX_REFRESH_OFFSET: 20,
  VIDEOS_PER_CATEGORY: 5,
  beforeRouteLeave(to, from, next) {
    if (to.name === 'player') {
      const routePath = from.fullPath
      const scrollY = getCurrentScrollPosition()
      saveScrollPosition(routePath, scrollY)
    }
    next()
  },
  data() {
    return {
      categories: [],
      categoryVideos: {}, // { category: videos[] }
      carouselVideos: [],
      searchKeyword: '',
      selectedCategory: '',
      loading: true,
      loadingMore: false,
      error: false,
      errorMessage: '',
      page: 1,
      limit: 20,
      hasMore: true,
      shouldRestoreScroll: false,
      searchDebounceTimer: null,
      // For filtered view (search or single category)
      filteredVideos: [],
      // Flag to indicate using mock data
      usingMockData: false
    }
  },
  computed: {
    // Get display categories (first 5 including "推荐")
    displayCategories() {
      const tabs = [{ video_category: '', label: '推荐' }]
      const catList = this.categories.slice(0, 4).map(c => ({
        video_category: c.video_category,
        label: c.video_category
      }))
      return [...tabs, ...catList]
    },
    // Category sections for home view
    categorySections() {
      if (this.isFilteredView) {
        return []
      }
      return this.categories
        .filter(cat => this.categoryVideos[cat.video_category]?.length > 0)
        .map(cat => ({
          category: cat.video_category,
          videos: this.categoryVideos[cat.video_category] || []
        }))
    },
    // Check if we're in filtered view (search or specific category)
    isFilteredView() {
      return this.searchKeyword.trim() !== '' || this.selectedCategory !== ''
    }
  },
  watch: {
    '$route'(to, from) {
      if (from.name === 'player' && (to.name === 'home' || to.name === 'category' || to.name === 'search')) {
        this.shouldRestoreScroll = true
        if (to.name === 'category') {
          this.selectedCategory = to.params.category || ''
        }
        return
      }
      
      if (to.name === 'category') {
        this.selectedCategory = to.params.category || ''
        this.loadFilteredVideos()
      } else if (to.name === 'search') {
        this.searchKeyword = to.query.q || ''
        this.handleSearch()
      } else if (to.name === 'home') {
        this.selectedCategory = ''
        this.searchKeyword = ''
        // Only reload if no data exists (keep-alive should preserve data)
        if (this.categories.length === 0) {
          this.init()
        }
      }
    }
  },
  mounted() {
    this.init()
  },
  activated() {
    if (this.shouldRestoreScroll) {
      this.shouldRestoreScroll = false
      const routePath = this.$route.fullPath
      
      if (hasScrollPosition(routePath)) {
        this.$nextTick(() => {
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
    const routePath = this.$route.fullPath
    const scrollY = getCurrentScrollPosition()
    saveScrollPosition(routePath, scrollY)
  },
  beforeUnmount() {
    if (this.searchDebounceTimer) {
      clearTimeout(this.searchDebounceTimer)
    }
  },
  methods: {
    async init() {
      // Check route params
      if (this.$route.name === 'category') {
        this.selectedCategory = this.$route.params.category || ''
      } else if (this.$route.name === 'search') {
        this.searchKeyword = this.$route.query.q || ''
      }
      
      this.loading = true
      this.error = false
      this.usingMockData = false
      
      try {
        await this.loadCategories()
        
        // If no categories loaded from API, use mock data
        if (this.categories.length === 0) {
          console.log('API unavailable, using mock data')
          this.usingMockData = true
          this.categories = getMockCategories()
        }
        
        if (this.isFilteredView) {
          await this.loadFilteredVideos()
        } else {
          await this.loadHomeData()
        }
      } catch (e) {
        // Fallback to mock data on error
        console.log('Error loading data, falling back to mock data:', e)
        this.usingMockData = true
        this.categories = getMockCategories()
        await this.loadHomeDataWithMock()
      } finally {
        this.loading = false
      }
    },
    
    async loadCategories() {
      try {
        const result = await videoApi.getCategories()
        this.categories = extractArrayData(result)
      } catch (e) {
        console.error('Load categories error:', e)
        // Don't throw, let init handle fallback
      }
    },
    
    async loadHomeDataWithMock() {
      const videosPerCategory = this.$options.VIDEOS_PER_CATEGORY
      
      // Load mock carousel videos
      this.carouselVideos = getMockTopVideos(videosPerCategory)
      
      // Load mock videos for each category
      const categoriesToLoad = this.categories.slice(0, videosPerCategory)
      categoriesToLoad.forEach(cat => {
        this.categoryVideos[cat.video_category] = getMockVideosByCategory(cat.video_category, videosPerCategory)
      })
    },
    
    async loadHomeData() {
      const videosPerCategory = this.$options.VIDEOS_PER_CATEGORY
      
      // If using mock data, use mock method
      if (this.usingMockData) {
        await this.loadHomeDataWithMock()
        return
      }
      
      // Load carousel videos (top videos)
      try {
        const topResult = await videoApi.getTopVideos(videosPerCategory)
        this.carouselVideos = extractArrayData(topResult)
        // If no videos returned, use mock data
        if (this.carouselVideos.length === 0) {
          this.carouselVideos = getMockTopVideos(videosPerCategory)
        }
      } catch (e) {
        console.error('Load top videos error:', e)
        this.carouselVideos = getMockTopVideos(videosPerCategory)
      }
      
      // Load videos for each category in parallel (first 5 categories)
      const categoriesToLoad = this.categories.slice(0, videosPerCategory)
      
      const categoryPromises = categoriesToLoad.map(async (cat) => {
        try {
          const result = await videoApi.getVideosByCategory(cat.video_category, videosPerCategory)
          const videos = extractArrayData(result)
          // If no videos returned, use mock data for this category
          if (videos.length === 0) {
            return { category: cat.video_category, videos: getMockVideosByCategory(cat.video_category, videosPerCategory) }
          }
          return { category: cat.video_category, videos }
        } catch (e) {
          console.error(`Load category ${cat.video_category} error:`, e)
          return { category: cat.video_category, videos: getMockVideosByCategory(cat.video_category, videosPerCategory) }
        }
      })
      
      const results = await Promise.all(categoryPromises)
      results.forEach(({ category, videos }) => {
        this.categoryVideos[category] = videos
      })
    },
    
    async loadFilteredVideos() {
      this.loading = true
      this.page = 1
      
      try {
        let result
        let videos = []
        
        if (this.usingMockData) {
          // Use mock data
          if (this.searchKeyword) {
            videos = searchMockVideos(this.searchKeyword, this.limit)
          } else if (this.selectedCategory) {
            videos = getMockVideosByCategory(this.selectedCategory, this.limit)
          }
        } else {
          // Try API first
          if (this.searchKeyword) {
            result = await videoApi.searchVideos(this.searchKeyword, this.limit)
          } else if (this.selectedCategory) {
            result = await videoApi.getVideosByCategory(this.selectedCategory, this.limit)
          }
          videos = extractArrayData(result)
          
          // Fallback to mock if no results
          if (videos.length === 0) {
            if (this.searchKeyword) {
              videos = searchMockVideos(this.searchKeyword, this.limit)
            } else if (this.selectedCategory) {
              videos = getMockVideosByCategory(this.selectedCategory, this.limit)
            }
          }
        }
        
        this.filteredVideos = videos
        this.hasMore = this.filteredVideos.length >= this.limit
        
        // Update category sections to show filtered results
        if (this.selectedCategory) {
          this.categoryVideos = { [this.selectedCategory]: this.filteredVideos }
        }
      } catch (e) {
        console.error('Load filtered videos error:', e)
        // Fallback to mock data
        if (this.searchKeyword) {
          this.filteredVideos = searchMockVideos(this.searchKeyword, this.limit)
        } else if (this.selectedCategory) {
          this.filteredVideos = getMockVideosByCategory(this.selectedCategory, this.limit)
        }
        this.hasMore = false
        if (this.selectedCategory) {
          this.categoryVideos = { [this.selectedCategory]: this.filteredVideos }
        }
      } finally {
        this.loading = false
      }
    },
    
    async loadMore() {
      if (this.loading || this.loadingMore) return
      
      // Mock data doesn't support pagination
      if (this.usingMockData) {
        this.hasMore = false
        return
      }
      
      this.loadingMore = true
      this.page++
      const offset = (this.page - 1) * this.limit
      
      try {
        let result
        if (this.searchKeyword) {
          result = await videoApi.searchVideos(this.searchKeyword, this.limit, offset)
        } else if (this.selectedCategory) {
          result = await videoApi.getVideosByCategory(this.selectedCategory, this.limit, offset)
        }
        
        const newVideos = extractArrayData(result)
        this.filteredVideos = [...this.filteredVideos, ...newVideos]
        this.hasMore = newVideos.length >= this.limit
        
        if (this.selectedCategory) {
          this.categoryVideos[this.selectedCategory] = this.filteredVideos
        }
      } catch (e) {
        console.error('Load more error:', e)
      } finally {
        this.loadingMore = false
      }
    },
    
    handleCategoryClick(category) {
      this.selectedCategory = category
      this.searchKeyword = ''
      
      if (category) {
        this.$router.push({ name: 'category', params: { category } })
      } else {
        this.$router.push({ name: 'home' })
      }
    },
    
    handleSearch() {
      if (this.searchKeyword.trim()) {
        this.$router.push({ name: 'search', query: { q: this.searchKeyword } })
        this.loadFilteredVideos()
      }
    },
    
    onSearchInput() {
      if (this.searchDebounceTimer) {
        clearTimeout(this.searchDebounceTimer)
      }
      
      if (this.searchKeyword.trim()) {
        this.searchDebounceTimer = setTimeout(() => {
          this.handleSearch()
        }, 500)
      } else {
        this.searchDebounceTimer = setTimeout(() => {
          if (!this.searchKeyword.trim()) {
            if (this.$route.name === 'search') {
              this.$router.push({ name: 'home' })
            }
          }
        }, 500)
      }
    },
    
    async refreshCategory(category) {
      try {
        // Get random offset for variety
        const randomOffset = Math.floor(Math.random() * this.$options.MAX_REFRESH_OFFSET)
        const result = await videoApi.getVideosByCategory(category, this.$options.VIDEOS_PER_CATEGORY, randomOffset)
        this.categoryVideos[category] = extractArrayData(result)
      } catch (e) {
        console.error(`Refresh category ${category} error:`, e)
      }
    },
    
    viewMoreCategory(category) {
      this.$router.push({ name: 'category', params: { category } })
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
  padding: 0 15px;
  max-width: 1400px;
  margin: 0 auto;
}

/* Header */
.header {
  position: sticky;
  top: 0;
  background: linear-gradient(180deg, rgba(26, 26, 46, 0.98) 0%, rgba(26, 26, 46, 0.95) 100%);
  padding: 12px 0;
  margin: 0 -15px;
  padding-left: 15px;
  padding-right: 15px;
  z-index: 100;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo {
  font-size: 1.2em;
  font-weight: 700;
  background: linear-gradient(90deg, #00d4ff, #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  white-space: nowrap;
}

.search-box {
  flex: 1;
  display: flex;
  max-width: 400px;
  margin: 0 auto;
}

.search-box input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px 0 0 20px;
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
  padding: 10px 15px;
  background: linear-gradient(90deg, #00d4ff, #7c3aed);
  border: none;
  border-radius: 0 20px 20px 0;
  color: #fff;
  cursor: pointer;
  transition: all 0.3s;
}

.search-btn:hover {
  filter: brightness(1.1);
}

.header-spacer {
  width: 80px;
}

/* Category Tabs */
.category-tabs {
  display: flex;
  gap: 8px;
  padding: 12px 0;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.category-tabs::-webkit-scrollbar {
  display: none;
}

.tab-btn {
  padding: 8px 18px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  color: #aaa;
  font-size: 0.9em;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
}

.tab-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

.tab-btn.active {
  background: linear-gradient(90deg, #00d4ff, #7c3aed);
  border-color: transparent;
  color: #fff;
}

/* Main Content */
.main-content {
  padding: 10px 0;
}

/* States */
.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
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

.loading-spinner.small {
  width: 16px;
  height: 16px;
  border-width: 2px;
}

/* Bottom spacer for nav bar */
.bottom-spacer {
  height: 70px;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .home {
    padding: 0 12px;
  }
  
  .header {
    margin: 0 -12px;
    padding-left: 12px;
    padding-right: 12px;
  }
  
  .header-content {
    gap: 10px;
  }
  
  .logo {
    font-size: 1em;
  }
  
  .header-spacer {
    display: none;
  }
  
  .search-box {
    flex: 1;
    max-width: none;
  }
  
  .search-box input {
    padding: 8px 12px;
    font-size: 13px;
  }
  
  .search-btn {
    padding: 8px 12px;
  }
  
  .category-tabs {
    gap: 6px;
    padding: 10px 0;
  }
  
  .tab-btn {
    padding: 6px 14px;
    font-size: 0.8em;
  }
}

/* Small mobile devices */
@media (max-width: 480px) {
  .home {
    padding: 0 10px;
  }
  
  .header {
    margin: 0 -10px;
    padding: 10px;
  }
  
  .logo {
    font-size: 0.9em;
  }
  
  .tab-btn {
    padding: 5px 12px;
    font-size: 0.75em;
  }
  
  .bottom-spacer {
    height: 60px;
  }
}

/* Large desktops */
@media (min-width: 1400px) {
  .home {
    max-width: 1600px;
    padding: 0 30px;
  }
  
  .header {
    margin: 0 -30px;
    padding-left: 30px;
    padding-right: 30px;
  }
  
  .logo {
    font-size: 1.4em;
  }
}
</style>
