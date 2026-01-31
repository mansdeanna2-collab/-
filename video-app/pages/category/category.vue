<template>
  <view class="category-page">
    <!-- Header -->
    <view class="header">
      <text class="title">{{ category }} 分类</text>
      <text class="count" v-if="videos.length > 0">
        已加载 {{ loadedCount }} 个视频
      </text>
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
            <text v-if="video.play_count" class="play-count">
              {{ formatPlayCount(video.play_count) }} 次播放
            </text>
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
import { formatPlayCount, showToast } from '@/utils'
import { PAGINATION_CONFIG } from '@/config'

export default {
  name: 'CategoryPage',
  data() {
    return {
      category: '',
      videos: [],
      loadedCount: 0,
      loading: true,
      loadingMore: false,
      error: false,
      errorMessage: '',
      page: 1,
      limit: PAGINATION_CONFIG.defaultPageSize,
      hasMore: true
    }
  },
  onLoad(options) {
    this.category = decodeURIComponent(options.category || '')
    if (!this.category) {
      this.error = true
      this.errorMessage = '无效的分类'
      this.loading = false
      return
    }
    uni.setNavigationBarTitle({
      title: `${this.category}`
    })
    this.loadVideos()
  },
  onPullDownRefresh() {
    this.loadVideos().finally(() => {
      uni.stopPullDownRefresh()
    })
  },
  onReachBottom() {
    if (this.hasMore && !this.loading && !this.loadingMore) {
      this.loadMore()
    }
  },
  methods: {
    // 使用工具函数
    formatPlayCount,
    async loadVideos() {
      if (!this.category) {
        this.error = true
        this.errorMessage = '无效的分类'
        return
      }
      
      this.loading = true
      this.error = false
      this.page = 1
      
      try {
        const result = await videoApi.getVideosByCategory(this.category, this.limit)
        this.videos = result.data || result || []
        this.loadedCount = this.videos.length
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
        const result = await videoApi.getVideosByCategory(this.category, this.limit, offset)
        const newVideos = result.data || result || []
        this.videos = [...this.videos, ...newVideos]
        this.loadedCount = this.videos.length
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
    }
  }
}
</script>

<style scoped>
.category-page {
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

.title {
  font-size: 36rpx;
  font-weight: bold;
  color: #00d4ff;
  display: block;
  margin-bottom: 10rpx;
}

.count {
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
  gap: 10rpx;
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
