<template>
  <view class="search-page">
    <!-- Search Header -->
    <view class="search-header">
      <view class="search-box">
        <input
          v-model="keyword"
          type="text"
          placeholder="搜索视频..."
          @confirm="handleSearch"
          class="search-input"
          focus
        />
        <button class="search-btn" @click="handleSearch">🔍</button>
      </view>
    </view>

    <!-- Result Header -->
    <view v-if="searched" class="result-header">
      <text class="result-title">
        搜索 "{{ displayKeyword }}" 的结果
      </text>
      <text v-if="videos.length > 0" class="result-count">
        找到 {{ videos.length }} 个视频
      </text>
    </view>

    <!-- Loading State -->
    <view v-if="loading" class="loading-state">
      <view class="loading-spinner"></view>
      <text>搜索中...</text>
    </view>

    <!-- Error State -->
    <view v-else-if="error" class="error-state">
      <text class="error-icon">⚠️</text>
      <text>{{ errorMessage }}</text>
      <button class="btn btn-primary" @click="handleSearch">重试</button>
    </view>

    <!-- Empty State -->
    <view v-else-if="searched && videos.length === 0" class="empty-state">
      <text class="empty-icon">🔍</text>
      <text>没有找到相关视频</text>
      <text class="empty-hint">换个关键词试试吧</text>
    </view>

    <!-- Video Grid -->
    <view v-else-if="videos.length > 0" class="video-grid">
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
          />
          <view v-else class="placeholder">
            <text>🎬</text>
          </view>
          <view class="play-icon">
            <text>▶</text>
          </view>
        </view>
        <view class="info">
          <text class="video-title">{{ video.video_title }}</text>
          <view class="meta">
            <text v-if="video.video_category" class="category">
              {{ video.video_category }}
            </text>
            <text v-if="video.play_count" class="play-count">
              {{ formatPlayCount(video.play_count) }} 次播放
            </text>
          </view>
        </view>
      </view>
    </view>

    <!-- Load More -->
    <view v-if="hasMore && !loading && videos.length > 0" class="load-more">
      <button class="btn btn-secondary" @click="loadMore">
        加载更多
      </button>
    </view>
  </view>
</template>

<script>
import { videoApi } from '@/api'
import { formatPlayCount, debounce, showToast, storage } from '@/utils'
import { PAGINATION_CONFIG, CACHE_CONFIG } from '@/config'

export default {
  name: 'SearchPage',
  data() {
    return {
      keyword: '',
      displayKeyword: '',
      videos: [],
      searchHistory: [],
      loading: false,
      loadingMore: false,
      error: false,
      errorMessage: '',
      searched: false,
      page: 1,
      limit: PAGINATION_CONFIG.defaultPageSize,
      hasMore: true
    }
  },
  onLoad(options) {
    // 加载搜索历史
    this.loadSearchHistory()
    
    if (options.q) {
      this.keyword = decodeURIComponent(options.q)
      this.handleSearch()
    }
  },
  onReachBottom() {
    if (this.hasMore && !this.loading && !this.loadingMore && this.searched) {
      this.loadMore()
    }
  },
  methods: {
    // 使用工具函数
    formatPlayCount,
    async handleSearch() {
      if (!this.keyword.trim()) {
        showToast('请输入搜索关键词')
        return
      }
      
      this.displayKeyword = this.keyword.trim()
      this.loading = true
      this.error = false
      this.searched = true
      this.page = 1
      
      // 保存搜索历史
      this.saveSearchHistory(this.displayKeyword)
      
      try {
        const result = await videoApi.searchVideos(this.keyword.trim(), this.limit)
        this.videos = result.data || result || []
        this.hasMore = this.videos.length >= this.limit
      } catch (e) {
        this.error = true
        this.errorMessage = e.message || '搜索失败，请稍后重试'
        console.error('Search error:', e)
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
        const result = await videoApi.searchVideos(this.keyword.trim(), this.limit, offset)
        const newVideos = result.data || result || []
        this.videos = [...this.videos, ...newVideos]
        this.hasMore = newVideos.length >= this.limit
      } catch (e) {
        console.error('Load more error:', e)
        showToast('加载失败，请重试')
        this.page-- // 回退页码
      } finally {
        this.loadingMore = false
      }
    },
    
    playVideo(video) {
      if (!video || !video.video_id) {
        showToast('无效的视频')
        return
      }
      uni.navigateTo({
        url: `/pages/player/player?id=${video.video_id}`
      })
    },
    
    /**
     * 加载搜索历史
     */
    loadSearchHistory() {
      const history = storage.get(CACHE_CONFIG.searchHistory.key, [])
      this.searchHistory = Array.isArray(history) ? history : []
    },
    
    /**
     * 保存搜索历史
     */
    saveSearchHistory(keyword) {
      if (!keyword) return
      
      // 移除重复项
      let history = this.searchHistory.filter(item => item !== keyword)
      
      // 添加到开头
      history.unshift(keyword)
      
      // 限制数量
      if (history.length > CACHE_CONFIG.searchHistory.maxItems) {
        history = history.slice(0, CACHE_CONFIG.searchHistory.maxItems)
      }
      
      this.searchHistory = history
      storage.set(CACHE_CONFIG.searchHistory.key, history)
    },
    
    /**
     * 清空搜索历史
     */
    clearSearchHistory() {
      this.searchHistory = []
      storage.remove(CACHE_CONFIG.searchHistory.key)
      showToast('已清空搜索历史')
    },
    
    /**
     * 使用历史关键词搜索
     */
    searchFromHistory(keyword) {
      this.keyword = keyword
      this.handleSearch()
    }
  }
}
</script>

<style scoped>
.search-page {
  min-height: 100vh;
  padding: 20rpx;
  background: #0a0a1a;
}

.search-header {
  padding: 20rpx 0;
  margin-bottom: 20rpx;
}

.search-box {
  display: flex;
  gap: 15rpx;
}

.search-input {
  flex: 1;
  padding: 24rpx 30rpx;
  border: 1rpx solid rgba(255, 255, 255, 0.2);
  border-radius: 12rpx;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  font-size: 28rpx;
}

.search-btn {
  padding: 24rpx 40rpx;
  background: linear-gradient(90deg, #00d4ff, #7c3aed);
  border: none;
  border-radius: 12rpx;
  color: #fff;
  font-size: 28rpx;
}

.result-header {
  padding: 20rpx 0;
  margin-bottom: 20rpx;
  border-bottom: 1rpx solid rgba(255, 255, 255, 0.1);
}

.result-title {
  display: block;
  font-size: 30rpx;
  font-weight: 500;
  color: #fff;
  margin-bottom: 8rpx;
}

.result-count {
  color: #8b8b8b;
  font-size: 24rpx;
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

.info {
  padding: 20rpx;
}

.video-title {
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

.empty-hint {
  color: #666;
  font-size: 24rpx;
  margin-top: 10rpx;
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
