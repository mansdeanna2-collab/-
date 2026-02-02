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
          <button class="search-btn" @click="handleSearch">搜索</button>
        </div>
        <div class="header-spacer"></div>
      </div>
    </header>

    <!-- Main Category Tabs (大分类) -->
    <div class="category-tabs">
      <button
        v-for="(cat, index) in mainCategories"
        :key="index"
        :class="['tab-btn', { active: activeMainCategory === cat.key }]"
        @click="handleMainCategoryClick(cat.key)"
      >
        {{ cat.label }}
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
    <div v-else class="main-content" ref="mainContent">
      <!-- Carousel Banner -->
      <Carousel 
        v-if="carouselVideos.length > 0"
        :videos="carouselVideos"
        @click="playVideo"
      />

      <!-- Category Sections (Home View) - Load first 4, then more on scroll -->
      <CategorySection
        v-for="cat in visibleCategorySections"
        :key="cat.category"
        :title="cat.category"
        :videos="cat.videos"
        @play="playVideo"
        @refresh="refreshCategory(cat.category)"
        @more="viewMoreCategory(cat.category)"
      />
      
      <!-- Load More Categories Trigger -->
      <div 
        v-if="!isFilteredView && hasMoreCategories" 
        ref="loadMoreTrigger"
        class="load-more-categories"
      >
        <div v-if="loadingMoreCategories" class="loading-spinner"></div>
        <span v-else>向上滑动加载更多分类...</span>
      </div>
      
      <!-- No More Content Message -->
      <div 
        v-if="!isFilteredView && !hasMoreCategories && visibleCategorySections.length > 0" 
        class="no-more-content"
      >
        <span>暂无更多内容</span>
      </div>

      <!-- Filtered Videos Grid (Search View) -->
      <div v-if="isFilteredView && filteredVideos.length > 0" class="filtered-view">
        <div class="filtered-header">
          <h2 class="filtered-title">
            "{{ searchKeyword }}" 的搜索结果
          </h2>
        </div>
        <div class="videos-grid">
          <VideoCard
            v-for="video in filteredVideos"
            :key="video.video_id"
            :video="video"
            @click="playVideo"
          />
        </div>
      </div>

      <!-- Empty State for Filtered View -->
      <div v-if="isFilteredView && filteredVideos.length === 0 && !loading" class="empty-filtered">
        <div class="empty-icon">🔍</div>
        <p>未找到相关视频</p>
        <button class="btn btn-primary" @click="goHome">返回首页</button>
      </div>

      <!-- Load More (for search results) -->
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
import VideoCard from '@/components/VideoCard.vue'
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
    CategorySection,
    VideoCard
  },
  // Constants
  MAX_REFRESH_OFFSET: 20,
  VIDEOS_PER_CATEGORY: 5,
  INITIAL_CATEGORIES_COUNT: 4,
  MAX_CATEGORIES_COUNT: 8,
  LOAD_MORE_DELAY: 300, // ms delay for smooth UX when loading more categories
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
      loading: true,
      loadingMore: false,
      loadingMoreCategories: false,
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
      usingMockData: false,
      // Main category tabs (大分类)
      mainCategories: [
        { key: 'recommend', label: '推荐' },
        { key: 'japan', label: '日本' },
        { key: 'domestic', label: '国产' },
        { key: 'anime', label: '动漫' },
        { key: 'welfare', label: '福利' }
      ],
      // Subcategory mappings for each main category (每个大分类对应的子分类)
      mainCategorySubcategories: {
        recommend: ['热门推荐', '动作电影', '喜剧片', '科幻大片', '爱情电影', '恐怖惊悚', '纪录片', '动漫'],
        japan: ['日本AV', '无码高清', '制服诱惑', '人妻系列', '女优精选', '素人企划', '动漫资源', '经典作品'],
        domestic: ['国产自拍', '网红主播', '偷拍私拍', '情侣实录', '素人投稿', '制服诱惑', '熟女人妻', '精品短视频'],
        anime: ['里番动漫', '3D动画', '同人作品', '触手系列', 'NTR剧情', '巨乳萝莉', '校园爱情', '经典番剧'],
        welfare: ['写真福利', '丝袜美腿', '性感模特', '大尺度写真', '韩国女团', '日本偶像', '网红热舞', 'ASMR']
      },
      activeMainCategory: 'recommend',
      // Visible categories count for lazy loading
      visibleCategoriesCount: 4,
      // Intersection observer for lazy loading
      intersectionObserver: null
    }
  },
  computed: {
    // Get current subcategories based on active main category
    // Use actual API categories instead of hardcoded subcategory mappings
    currentSubcategories() {
      // Extract category names from API categories
      // API response format: [{ video_category: 'name', video_count: N }, ...]
      // Handle different possible response structures for robustness
      const apiCategoryNames = this.categories.map(cat => 
        cat.video_category || cat.name || cat
      ).filter(Boolean)
      
      // If we have API categories, use them; otherwise fall back to hardcoded mappings
      if (apiCategoryNames.length > 0) {
        // All tabs now show the same API categories since the database
        // contains the actual video categories, not the hardcoded subcategories
        return apiCategoryNames.slice(0, this.$options.MAX_CATEGORIES_COUNT)
      }
      
      // Fallback to hardcoded mappings if API categories not available
      return this.mainCategorySubcategories[this.activeMainCategory] || []
    },
    // All category sections for home view (show max 8 subcategories based on main category)
    categorySections() {
      if (this.isFilteredView) {
        return []
      }
      const subcategories = this.currentSubcategories
      // Filter to show only subcategories that have videos, maintaining the order from subcategories list
      return subcategories
        .filter(cat => this.categoryVideos[cat]?.length > 0)
        .slice(0, this.$options.MAX_CATEGORIES_COUNT)
        .map(cat => ({
          category: cat,
          videos: this.categoryVideos[cat] || []
        }))
    },
    // Visible category sections (lazy loading - first 4, then 4 more on scroll)
    visibleCategorySections() {
      return this.categorySections.slice(0, this.visibleCategoriesCount)
    },
    // Check if there are more categories to load
    hasMoreCategories() {
      return this.visibleCategoriesCount < this.categorySections.length
    },
    // Check if we're in filtered view (search only now, category is separate view)
    isFilteredView() {
      return this.searchKeyword.trim() !== ''
    }
  },
  watch: {
    '$route'(to, from) {
      if (from.name === 'player' && (to.name === 'home' || to.name === 'search')) {
        this.shouldRestoreScroll = true
        return
      }
      
      if (to.name === 'search') {
        this.searchKeyword = to.query.q || ''
        this.handleSearch()
      } else if (to.name === 'home') {
        this.searchKeyword = ''
        // Clear filtered videos only if it has data to avoid unnecessary re-renders
        if (this.filteredVideos.length > 0) {
          this.filteredVideos = []
        }
        // Reset visible categories count
        this.visibleCategoriesCount = this.$options.INITIAL_CATEGORIES_COUNT
        // Reload home data to show all categories
        this.loadHomeData()
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
    // Re-setup observer when activated
    this.$nextTick(() => {
      this.setupIntersectionObserver()
    })
  },
  deactivated() {
    const routePath = this.$route.fullPath
    const scrollY = getCurrentScrollPosition()
    saveScrollPosition(routePath, scrollY)
    // Cleanup observer
    this.cleanupIntersectionObserver()
  },
  beforeUnmount() {
    if (this.searchDebounceTimer) {
      clearTimeout(this.searchDebounceTimer)
    }
    this.cleanupIntersectionObserver()
  },
  methods: {
    // Setup intersection observer for lazy loading more categories
    setupIntersectionObserver() {
      if (this.$refs.loadMoreTrigger && !this.intersectionObserver) {
        this.intersectionObserver = new IntersectionObserver(
          (entries) => {
            entries.forEach((entry) => {
              if (entry.isIntersecting && this.hasMoreCategories && !this.loadingMoreCategories) {
                this.loadMoreCategories()
              }
            })
          },
          { threshold: 0.1 }
        )
        this.intersectionObserver.observe(this.$refs.loadMoreTrigger)
      }
    },
    
    // Cleanup intersection observer
    cleanupIntersectionObserver() {
      if (this.intersectionObserver) {
        this.intersectionObserver.disconnect()
        this.intersectionObserver = null
      }
    },
    
    // Load more categories on scroll
    loadMoreCategories() {
      if (this.loadingMoreCategories || !this.hasMoreCategories) return
      
      this.loadingMoreCategories = true
      
      // Small delay for smooth UX transition
      setTimeout(() => {
        this.visibleCategoriesCount = this.$options.MAX_CATEGORIES_COUNT
        this.loadingMoreCategories = false
      }, this.$options.LOAD_MORE_DELAY)
    },
    
    // Handle main category tab click
    handleMainCategoryClick(categoryKey) {
      // If clicking the same category, do nothing
      if (this.activeMainCategory === categoryKey) {
        return
      }
      
      this.activeMainCategory = categoryKey
      
      // Scroll to top when switching main categories
      window.scrollTo({ top: 0, behavior: 'smooth' })
      
      // Reset visible categories count and reload data for the selected main category
      this.visibleCategoriesCount = this.$options.INITIAL_CATEGORIES_COUNT
      
      // Show loading state while fetching new category data
      this.loading = true
      this.loadHomeData().finally(() => {
        this.loading = false
      })
    },
    
    async init() {
      // Check route params (only search now, category is separate view)
      if (this.$route.name === 'search') {
        this.searchKeyword = this.$route.query.q || ''
      }
      
      this.loading = true
      this.error = false
      this.usingMockData = false
      // Reset visible categories count
      this.visibleCategoriesCount = this.$options.INITIAL_CATEGORIES_COUNT
      
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
        // Fallback to mock data on error with better error message
        console.log('Error loading data, falling back to mock data:', e.userMessage || e.message)
        this.usingMockData = true
        this.categories = getMockCategories()
        await this.loadHomeDataWithMock()
      } finally {
        this.loading = false
        // Setup intersection observer after loading completes
        this.$nextTick(() => {
          this.setupIntersectionObserver()
        })
      }
    },
    
    async loadCategories() {
      try {
        const result = await videoApi.getCategories()
        this.categories = extractArrayData(result)
      } catch (e) {
        console.error('Load categories error:', e.userMessage || e.message)
        // Don't throw, let init handle fallback
      }
    },
    
    async loadHomeDataWithMock() {
      const videosPerCategory = this.$options.VIDEOS_PER_CATEGORY
      
      // Load mock carousel videos
      this.carouselVideos = getMockTopVideos(videosPerCategory)
      
      // Get current subcategories based on active main category
      const subcategories = this.currentSubcategories
      
      // Build category videos in a temporary object to avoid flickering
      const newCategoryVideos = {}
      subcategories.forEach(cat => {
        newCategoryVideos[cat] = getMockVideosByCategory(cat, videosPerCategory)
      })
      // Assign once to avoid multiple re-renders
      this.categoryVideos = newCategoryVideos
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
        // Only fallback to mock if in mock mode
        if (this.carouselVideos.length === 0 && this.usingMockData) {
          this.carouselVideos = getMockTopVideos(videosPerCategory)
        }
      } catch (e) {
        console.error('Load top videos error:', e)
        // Only fallback to mock if in mock mode
        if (this.usingMockData) {
          this.carouselVideos = getMockTopVideos(videosPerCategory)
        }
      }
      
      // Get current subcategories based on active main category
      const subcategories = this.currentSubcategories
      // Store the active category at the start to detect race conditions
      const currentMainCategory = this.activeMainCategory
      
      // Clear category videos before loading new data for this main category
      this.categoryVideos = {}
      
      // First, load only the first 4 categories (visible categories)
      const firstBatchCategories = subcategories.slice(0, this.$options.INITIAL_CATEGORIES_COUNT)
      await this.loadCategoriesData(firstBatchCategories, videosPerCategory, currentMainCategory)
      
      // Then, load remaining categories in background (lazy loading)
      const remainingCategories = subcategories.slice(this.$options.INITIAL_CATEGORIES_COUNT, this.$options.MAX_CATEGORIES_COUNT)
      if (remainingCategories.length > 0) {
        // Load remaining categories asynchronously without blocking UI
        this.loadCategoriesData(remainingCategories, videosPerCategory, currentMainCategory)
      }
    },
    
    // Helper method to load videos for specific categories
    async loadCategoriesData(categoryList, videosPerCategory, expectedMainCategory) {
      const categoryPromises = categoryList.map(async (cat) => {
        try {
          const result = await videoApi.getVideosByCategory(cat, videosPerCategory)
          const videos = extractArrayData(result)
          // Return actual API data - empty array is valid if no videos exist for this category
          return { category: cat, videos }
        } catch (e) {
          console.error(`Load category ${cat} error:`, e)
          // Only fallback to mock data if we're in mock data mode
          if (this.usingMockData) {
            return { category: cat, videos: getMockVideosByCategory(cat, videosPerCategory) }
          }
          return { category: cat, videos: [] }
        }
      })
      
      const results = await Promise.all(categoryPromises)
      
      // Check if the active main category has changed during loading
      // If so, discard the results to avoid race condition
      if (expectedMainCategory !== this.activeMainCategory) {
        console.log('Discarding stale category data - main category changed')
        return
      }
      
      // Update category videos by creating new object to ensure reactivity
      const newCategoryVideos = { ...this.categoryVideos }
      results.forEach(({ category, videos }) => {
        newCategoryVideos[category] = videos
      })
      this.categoryVideos = newCategoryVideos
    },
    
    async loadFilteredVideos() {
      this.loading = true
      this.page = 1
      
      try {
        let result
        let videos = []
        
        if (this.usingMockData) {
          // Use mock data for search
          if (this.searchKeyword) {
            videos = searchMockVideos(this.searchKeyword, this.limit)
          }
        } else {
          // Try API first for search
          if (this.searchKeyword) {
            result = await videoApi.searchVideos(this.searchKeyword, this.limit)
            videos = extractArrayData(result)
            // Don't fallback to mock data - show actual API results
          }
        }
        
        this.filteredVideos = videos
        this.hasMore = this.filteredVideos.length >= this.limit
      } catch (e) {
        console.error('Load filtered videos error:', e)
        // Only fallback to mock data if in mock mode
        if (this.usingMockData && this.searchKeyword) {
          this.filteredVideos = searchMockVideos(this.searchKeyword, this.limit)
        } else {
          this.filteredVideos = []
        }
        this.hasMore = false
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
        }
        
        if (result) {
          const newVideos = extractArrayData(result)
          this.filteredVideos = [...this.filteredVideos, ...newVideos]
          this.hasMore = newVideos.length >= this.limit
        }
      } catch (e) {
        console.error('Load more error:', e)
      } finally {
        this.loadingMore = false
      }
    },
    
    handleCategoryClick(category) {
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
    
    goHome() {
      this.searchKeyword = ''
      this.$router.push({ name: 'home' })
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
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: linear-gradient(180deg, rgba(26, 26, 46, 0.98) 0%, rgba(26, 26, 46, 0.95) 100%);
  padding: 12px 15px;
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
  max-width: 280px;
  margin: 0 auto;
}

.search-box input {
  flex: 1;
  padding: 6px 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px 0 0 16px;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  font-size: 13px;
  outline: none;
  transition: all 0.3s;
}

.search-box input:focus {
  border-color: #7c3aed;
  box-shadow: 0 0 10px rgba(124, 58, 237, 0.3);
}

.search-box input::placeholder {
  color: #888;
}

.search-btn {
  padding: 6px 14px;
  background: #7c3aed;
  border: none;
  border-radius: 0 16px 16px 0;
  color: #fff;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.search-btn:hover {
  background: #6d28d9;
}

.header-spacer {
  width: 80px;
}

/* Category Tabs */
.category-tabs {
  position: fixed;
  top: 56px;
  left: 0;
  right: 0;
  display: flex;
  gap: 8px;
  padding: 12px 15px;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  background: linear-gradient(180deg, rgba(26, 26, 46, 0.98) 0%, rgba(26, 26, 46, 0.95) 100%);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  z-index: 99;
}

.category-tabs::-webkit-scrollbar {
  display: none;
}

.tab-btn {
  padding: 8px 16px;
  background: transparent;
  border: none;
  color: #fff;
  font-size: 1.1em;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.3s;
  white-space: nowrap;
  flex-shrink: 0;
}

.tab-btn:hover {
  color: #00d4ff;
}

.tab-btn.active {
  color: #ff8c00;
}

/* Main Content */
.main-content {
  padding-top: 110px;
  padding-bottom: 10px;
}

/* States */
.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  padding-top: 150px;
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

.loading-spinner {
  width: 30px;
  height: 30px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #00d4ff;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-spinner.small {
  width: 16px;
  height: 16px;
  border-width: 2px;
}

/* Load More Categories */
.load-more-categories {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  color: #888;
  font-size: 0.9em;
}

/* No More Content Message */
.no-more-content {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 25px 20px;
  color: #666;
  font-size: 0.9em;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin-top: 10px;
}

/* Filtered View Styles */
.filtered-view {
  margin-top: 15px;
}

.filtered-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding: 0 5px;
}

.filtered-title {
  font-size: 1.2em;
  font-weight: 600;
  color: #fff;
}

.filtered-count {
  font-size: 0.9em;
  color: #888;
}

.videos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.empty-filtered {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-filtered .empty-icon {
  font-size: 4em;
  margin-bottom: 15px;
}

.empty-filtered p {
  color: #888;
  margin-bottom: 20px;
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
    padding: 10px 12px;
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
    max-width: 200px;
  }
  
  .search-box input {
    padding: 5px 10px;
    font-size: 12px;
  }
  
  .search-btn {
    padding: 5px 10px;
    font-size: 12px;
  }
  
  .category-tabs {
    gap: 6px;
    padding: 10px 12px;
    top: 50px;
  }
  
  .main-content {
    padding-top: 100px;
  }
  
  .tab-btn {
    padding: 6px 12px;
    font-size: 1em;
  }
  
  .videos-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }
  
  .filtered-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .filtered-title {
    font-size: 1.1em;
  }
}

/* Small mobile devices */
@media (max-width: 480px) {
  .home {
    padding: 0 10px;
  }
  
  .header {
    padding: 10px;
  }
  
  .logo {
    font-size: 0.9em;
  }
  
  .category-tabs {
    padding: 10px;
    top: 46px;
  }
  
  .main-content {
    padding-top: 95px;
  }
  
  .tab-btn {
    padding: 5px 10px;
    font-size: 0.95em;
  }
  
  .videos-grid {
    gap: 10px;
  }
  
  .filtered-title {
    font-size: 1em;
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
    padding: 15px 30px;
  }
  
  .category-tabs {
    padding: 12px 30px;
  }
  
  .logo {
    font-size: 1.4em;
  }
}
</style>
