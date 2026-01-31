<template>
  <view class="home">
    <!-- Header -->
    <view class="header">
      <text class="logo">🎬 视频播放器</text>
      <text class="stats" v-if="statistics.total_videos">
        共 {{ statistics.total_videos }} 个视频 | {{ statistics.total_plays }} 次播放
      </text>
    </view>

    <!-- Controls -->
    <view class="controls">
      <view class="search-box">
        <input
          v-model="searchKeyword"
          type="text"
          placeholder="搜索视频..."
          @confirm="handleSearch"
          class="search-input"
        />
        <button class="search-btn" @click="handleSearch">🔍</button>
      </view>
      
      <picker
        mode="selector"
        :range="categoryOptions"
        range-key="label"
        @change="handleCategoryChange"
      >
        <view class="category-picker">
          {{ selectedCategoryLabel || '全部分类' }}
        </view>
      </picker>
    </view>

    <!-- Loading State -->
    <view v-if="loading" class="loading-state">
      <view class="loading-spinner"></view>
      <text>加载中...</text>
    </view>

    <!-- Error State -->
    <view v-else-if="error" class="error-state">
      <text class="error-icon">⚠️</text>
      <text>{{ errorMessage }}</text>
      <button class="btn btn-primary" @click="loadVideos">重试</button>
    </view>

    <!-- Empty State -->
    <view v-else-if="videos.length === 0" class="empty-state">
      <text class="empty-icon">📭</text>
      <text>暂无视频</text>
    </view>

    <!-- Video Grid -->
    <view v-else class="video-grid">
      <view
        v-for="video in videos"
        :key="video.video_id"
        class="video-card"
        @click="playVideo(video)"
      >
        <view class="thumbnail">
          <image 
            v-if="video.video_image" 
            :src="video.video_image"
            mode="aspectFill"
            class="thumb-img"
            @error="handleImageError"
          />
          <view v-else class="placeholder">
            <text>🎬</text>
          </view>
          <view class="play-icon">
            <text>▶</text>
          </view>
          <text v-if="video.video_duration" class="duration">
            {{ video.video_duration }}
          </text>
        </view>
        <view class="info">
          <text class="title">{{ video.video_title }}</text>
          <view class="meta">
            <text v-if="video.video_category" class="category">
              {{ video.video_category }}
            </text>
            <text v-if="video.play_count" class="play-count">
              {{ formatPlayCount(video.play_count) }} 次播放
            </text>
          </view>
          <view v-if="video.video_coins > 0" class="coins">
            <text class="coin-icon">🪙</text>
            <text>{{ video.video_coins }} 金币</text>
          </view>
        </view>
      </view>
    </view>

    <!-- Load More -->
    <view v-if="hasMore && !loading" class="load-more">
      <button class="btn btn-secondary" @click="loadMore">
        加载更多
      </button>
    </view>
  </view>
</template>

<script>
import { videoApi } from '@/api'
import { formatPlayCount, debounce } from '@/utils'
import { PAGINATION_CONFIG } from '@/config'

export default {
  name: 'IndexPage',
  data() {
    return {
      videos: [],
      categories: [],
      statistics: {},
      searchKeyword: '',
      selectedCategory: '',
      selectedCategoryIndex: 0,
      loading: true,
      loadingMore: false,
      error: false,
      errorMessage: '',
      page: 1,
      limit: PAGINATION_CONFIG.defaultPageSize,
      hasMore: true,
      isRefreshing: false
    }
  },
  computed: {
    categoryOptions() {
      const options = [{ label: '全部分类', value: '' }]
      this.categories.forEach(cat => {
        options.push({
          label: `${cat.video_category} (${cat.video_count})`,
          value: cat.video_category
        })
      })
      return options
    },
    selectedCategoryLabel() {
      if (!this.selectedCategory) return '全部分类'
      const cat = this.categories.find(c => c.video_category === this.selectedCategory)
      return cat ? `${cat.video_category} (${cat.video_count})` : '全部分类'
    }
  },
  onLoad(options) {
    if (options.category) {
      this.selectedCategory = options.category
    }
    if (options.q) {
      this.searchKeyword = options.q
    }
    this.init()
  },
  onPullDownRefresh() {
    this.isRefreshing = true
    this.loadVideos().finally(() => {
      this.isRefreshing = false
      uni.stopPullDownRefresh()
    })
  },
  onReachBottom() {
    // 触底加载更多
    if (this.hasMore && !this.loading && !this.loadingMore) {
      this.loadMore()
    }
  },
  methods: {
    // 使用工具函数
    formatPlayCount,
    async init() {
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
      if (this.loading || this.loadingMore) return
      
      this.loadingMore = true
      this.page++
      const offset = (this.page - 1) * this.limit
      
      try {
        let result
        if (this.searchKeyword) {
          result = await videoApi.searchVideos(this.searchKeyword, this.limit, offset)
        } else if (this.selectedCategory) {
          result = await videoApi.getVideosByCategory(this.selectedCategory, this.limit, offset)
        } else {
          const params = { limit: this.limit, offset }
          result = await videoApi.getVideos(params)
        }
        const newVideos = result.data || result || []
        this.videos = [...this.videos, ...newVideos]
        this.hasMore = newVideos.length >= this.limit
      } catch (e) {
        console.error('Load more error:', e)
        uni.showToast({
          title: '加载失败，请重试',
          icon: 'none'
        })
        this.page-- // 回退页码
      } finally {
        this.loadingMore = false
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
    
    handleSearch: debounce(function() {
      if (this.searchKeyword.trim()) {
        uni.navigateTo({
          url: `/pages/search/search?q=${encodeURIComponent(this.searchKeyword)}`
        })
      } else {
        this.loadVideos()
      }
    }, 300),
    
    handleCategoryChange(e) {
      const index = e.detail.value
      const option = this.categoryOptions[index]
      this.selectedCategory = option.value
      this.selectedCategoryIndex = index
      if (this.selectedCategory) {
        uni.navigateTo({
          url: `/pages/category/category?category=${encodeURIComponent(this.selectedCategory)}`
        })
      } else {
        this.loadVideos()
      }
    },
    
    playVideo(video) {
      if (!video || !video.video_id) {
        uni.showToast({
          title: '无效的视频',
          icon: 'none'
        })
        return
      }
      uni.navigateTo({
        url: `/pages/player/player?id=${video.video_id}`
      })
    },
    
    handleImageError(e) {
      // Handle image loading error - 可以替换为默认图片
      console.log('Image load error:', e)
    }
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  padding: 20rpx;
  background: #0a0a1a;
}

.header {
  text-align: center;
  padding: 30rpx 0;
  border-bottom: 1rpx solid rgba(255, 255, 255, 0.1);
  margin-bottom: 30rpx;
}

.logo {
  font-size: 40rpx;
  font-weight: bold;
  color: #00d4ff;
  display: block;
  margin-bottom: 10rpx;
}

.stats {
  color: #8b8b8b;
  font-size: 24rpx;
}

.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
  margin-bottom: 30rpx;
  padding: 20rpx;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20rpx;
}

.search-box {
  flex: 1;
  min-width: 300rpx;
  display: flex;
  gap: 10rpx;
}

.search-input {
  flex: 1;
  padding: 20rpx 30rpx;
  border: 1rpx solid rgba(255, 255, 255, 0.2);
  border-radius: 12rpx;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  font-size: 28rpx;
}

.search-btn {
  padding: 20rpx 30rpx;
  background: linear-gradient(90deg, #00d4ff, #7c3aed);
  border: none;
  border-radius: 12rpx;
  color: #fff;
  font-size: 28rpx;
}

.category-picker {
  padding: 20rpx 30rpx;
  border: 1rpx solid rgba(255, 255, 255, 0.2);
  border-radius: 12rpx;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  font-size: 28rpx;
  min-width: 200rpx;
}

.video-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

.video-card {
  width: calc(50% - 10rpx);
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20rpx;
  overflow: hidden;
  border: 1rpx solid rgba(255, 255, 255, 0.1);
}

.thumbnail {
  position: relative;
  width: 100%;
  padding-top: 56.25%;
  background: linear-gradient(135deg, #2a2a4a 0%, #1a1a3e 100%);
  overflow: hidden;
}

.thumb-img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 60rpx;
  color: #888;
}

.play-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80rpx;
  height: 80rpx;
  background: rgba(0, 212, 255, 0.9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.play-icon text {
  color: #fff;
  font-size: 24rpx;
  margin-left: 6rpx;
}

.duration {
  position: absolute;
  bottom: 10rpx;
  right: 10rpx;
  background: rgba(0, 0, 0, 0.7);
  padding: 4rpx 12rpx;
  border-radius: 6rpx;
  font-size: 20rpx;
  color: #fff;
}

.info {
  padding: 20rpx;
}

.title {
  font-size: 26rpx;
  font-weight: 600;
  color: #fff;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
  margin-bottom: 10rpx;
}

.meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10rpx;
}

.category {
  background: rgba(0, 212, 255, 0.2);
  color: #00d4ff;
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
  font-size: 20rpx;
}

.play-count {
  color: #888;
  font-size: 22rpx;
}

.coins {
  margin-top: 10rpx;
  color: #ffd700;
  font-size: 24rpx;
  display: flex;
  align-items: center;
  gap: 6rpx;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 40rpx;
  text-align: center;
}

.loading-spinner {
  width: 60rpx;
  height: 60rpx;
  border: 4rpx solid rgba(0, 212, 255, 0.3);
  border-top-color: #00d4ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-icon,
.empty-icon {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.btn {
  padding: 20rpx 40rpx;
  border-radius: 12rpx;
  font-size: 28rpx;
  border: none;
}

.btn-primary {
  background: linear-gradient(90deg, #00d4ff, #7c3aed);
  color: #fff;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1rpx solid rgba(255, 255, 255, 0.2);
}

.load-more {
  text-align: center;
  padding: 40rpx;
}
</style>
