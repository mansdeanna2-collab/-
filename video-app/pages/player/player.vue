<template>
  <view class="player-view">
    <!-- Back button -->
    <view class="nav-bar">
      <button class="back-btn" @click="goBack">
        ← 返回
      </button>
      <text class="title">{{ video.video_title || '视频播放' }}</text>
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
      <button class="btn btn-primary" @click="loadVideo">重试</button>
    </view>

    <!-- Video Player -->
    <view v-else class="player-container">
      <video
        id="myVideo"
        :src="video.video_url"
        :poster="video.video_image"
        controls
        class="video-player"
        @play="onPlay"
        @ended="onEnded"
        @error="onVideoError"
      ></video>
      
      <!-- Video Info -->
      <view class="video-info">
        <text class="video-title">{{ video.video_title }}</text>
        
        <view class="video-meta">
          <text v-if="video.video_category" class="category">
            {{ video.video_category }}
          </text>
          <text v-if="video.play_count" class="play-count">
            {{ formatPlayCount(video.play_count) }} 次播放
          </text>
          <text v-if="video.upload_time" class="upload-time">
            {{ video.upload_time }}
          </text>
        </view>
        
        <view v-if="video.video_coins > 0" class="coins-info">
          <text class="coin-icon">🪙</text>
          <text>需要 {{ video.video_coins }} 金币观看</text>
        </view>
      </view>

      <!-- Related Videos -->
      <view v-if="relatedVideos.length > 0" class="related-section">
        <text class="section-title">相关视频</text>
        <view class="related-grid">
          <view
            v-for="rv in relatedVideos"
            :key="rv.video_id"
            class="related-card"
            @click="playRelated(rv)"
          >
            <view class="related-thumbnail">
              <image 
                :src="rv.video_image"
                mode="aspectFill"
                class="related-img"
              />
              <view class="play-icon-small">
                <text>▶</text>
              </view>
            </view>
            <text class="related-title">{{ rv.video_title }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { videoApi } from '@/api'
import { formatPlayCount, showToast } from '@/utils'

export default {
  name: 'PlayerPage',
  data() {
    return {
      video: {},
      relatedVideos: [],
      loading: true,
      error: false,
      errorMessage: '',
      videoId: '',
      isPlaying: false,
      hasPlayed: false
    }
  },
  onLoad(options) {
    this.videoId = options.id
    if (!this.videoId) {
      this.error = true
      this.errorMessage = '无效的视频ID'
      this.loading = false
      return
    }
    this.loadVideo()
  },
  onShareAppMessage() {
    // 分享配置
    return {
      title: this.video.video_title || '精彩视频',
      path: `/pages/player/player?id=${this.videoId}`
    }
  },
  methods: {
    // 使用工具函数
    formatPlayCount,
    async loadVideo() {
      if (!this.videoId) {
        this.error = true
        this.errorMessage = '无效的视频ID'
        return
      }
      
      this.loading = true
      this.error = false
      
      try {
        const result = await videoApi.getVideo(this.videoId)
        this.video = result.data || result || {}
        
        if (!this.video.video_id) {
          this.error = true
          this.errorMessage = '视频不存在'
          return
        }
        
        // Update navigation bar title
        uni.setNavigationBarTitle({
          title: this.video.video_title || '视频播放'
        })
        
        // Load related videos
        if (this.video.video_category) {
          this.loadRelatedVideos()
        }
      } catch (e) {
        this.error = true
        this.errorMessage = '加载视频失败'
        console.error('Load video error:', e)
      } finally {
        this.loading = false
      }
    },
    
    async loadRelatedVideos() {
      try {
        const result = await videoApi.getVideosByCategory(this.video.video_category, 6)
        const videos = result.data || result || []
        // Filter out current video
        this.relatedVideos = videos.filter(v => v.video_id !== this.video.video_id).slice(0, 4)
      } catch (e) {
        console.error('Load related videos error:', e)
      }
    },
    
    async onPlay() {
      this.isPlaying = true
      
      // 只在第一次播放时更新播放次数
      if (!this.hasPlayed) {
        this.hasPlayed = true
        try {
          await videoApi.updatePlayCount(this.video.video_id)
          if (this.video.play_count !== undefined) {
            this.video.play_count++
          }
        } catch (e) {
          console.error('Update play count error:', e)
        }
      }
    },
    
    onPause() {
      this.isPlaying = false
    },
    
    onEnded() {
      this.isPlaying = false
      // 可以在这里实现自动播放下一个视频
      if (this.relatedVideos.length > 0) {
        uni.showModal({
          title: '播放完成',
          content: '是否播放相关视频？',
          confirmText: '播放',
          cancelText: '取消',
          success: (res) => {
            if (res.confirm) {
              this.playRelated(this.relatedVideos[0])
            }
          }
        })
      }
    },
    
    onVideoError(e) {
      console.error('Video playback error:', e)
      this.isPlaying = false
      showToast('视频播放失败，请稍后重试')
    },
    
    playRelated(video) {
      if (!video || !video.video_id) return
      
      this.videoId = video.video_id
      this.hasPlayed = false
      this.isPlaying = false
      this.loadVideo()
      
      // Scroll to top
      uni.pageScrollTo({
        scrollTop: 0,
        duration: 300
      })
    },
    
    goBack() {
      const pages = getCurrentPages()
      if (pages.length > 1) {
        uni.navigateBack()
      } else {
        uni.switchTab({
          url: '/pages/index/index'
        })
      }
    }
  }
}
</script>

<style scoped>
.player-view {
  min-height: 100vh;
  background: #0a0a1a;
}

.nav-bar {
  display: flex;
  align-items: center;
  padding: 20rpx 30rpx;
  background: rgba(0, 0, 0, 0.5);
  position: sticky;
  top: 0;
  z-index: 100;
}

.back-btn {
  padding: 12rpx 24rpx;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 10rpx;
  color: #fff;
  font-size: 26rpx;
}

.nav-bar .title {
  flex: 1;
  text-align: center;
  font-size: 30rpx;
  font-weight: 500;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin: 0 20rpx;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 200rpx 40rpx;
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

.error-icon {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.btn {
  padding: 20rpx 40rpx;
  border-radius: 12rpx;
  font-size: 28rpx;
  border: none;
  margin-top: 30rpx;
}

.btn-primary {
  background: linear-gradient(90deg, #00d4ff, #7c3aed);
  color: #fff;
}

.player-container {
  max-width: 100%;
}

.video-player {
  width: 100%;
  height: 420rpx;
  background: #000;
}

.video-info {
  padding: 30rpx;
}

.video-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #fff;
  display: block;
  margin-bottom: 20rpx;
}

.video-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
  font-size: 24rpx;
  color: #8b8b8b;
}

.category {
  background: rgba(0, 212, 255, 0.2);
  color: #00d4ff;
  padding: 8rpx 20rpx;
  border-radius: 30rpx;
}

.coins-info {
  margin-top: 20rpx;
  padding: 20rpx;
  background: rgba(255, 215, 0, 0.1);
  border: 1rpx solid rgba(255, 215, 0, 0.3);
  border-radius: 12rpx;
  color: #ffd700;
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.coin-icon {
  font-size: 32rpx;
}

.related-section {
  padding: 30rpx;
  border-top: 1rpx solid rgba(255, 255, 255, 0.1);
}

.section-title {
  display: block;
  margin-bottom: 20rpx;
  color: #fff;
  font-size: 30rpx;
  font-weight: 500;
}

.related-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

.related-card {
  width: calc(50% - 10rpx);
}

.related-thumbnail {
  position: relative;
  width: 100%;
  padding-top: 56.25%;
  background: linear-gradient(135deg, #2a2a4a 0%, #1a1a3e 100%);
  border-radius: 12rpx;
  overflow: hidden;
}

.related-img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.play-icon-small {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60rpx;
  height: 60rpx;
  background: rgba(0, 212, 255, 0.9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.play-icon-small text {
  color: #fff;
  font-size: 20rpx;
  margin-left: 4rpx;
}

.related-title {
  display: block;
  margin-top: 10rpx;
  font-size: 24rpx;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
