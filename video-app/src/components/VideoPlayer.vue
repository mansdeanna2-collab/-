<template>
  <div class="video-player" ref="playerContainer" :class="{ 'is-fullscreen': isFullscreen }">
    <div 
      class="player-wrapper"
      @touchstart="onTouchStart"
      @touchmove="onTouchMove"
      @touchend="onTouchEnd"
      @dblclick="onDoubleClick"
    >
      <video
        ref="videoElement"
        :src="safeEncodeURI(currentSrc)"
        :poster="computedPoster"
        controls
        playsinline
        webkit-playsinline
        x5-video-player-type="h5"
        x5-video-player-fullscreen="true"
        preload="metadata"
        @play="onPlay"
        @pause="onPause"
        @ended="onEnded"
        @error="onError"
        @loadedmetadata="onLoadedMetadata"
        @timeupdate="onTimeUpdate"
        @waiting="onWaiting"
        @canplay="onCanPlay"
        @loadstart="onLoadStart"
        @progress="onProgress"
        @stalled="onStalled"
      >
        您的浏览器不支持视频播放
      </video>
      
      <!-- Loading overlay with slow loading warning -->
      <div v-if="loading || buffering" class="loading-overlay">
        <div class="loading-spinner"></div>
        <p>{{ buffering ? '缓冲中...' : '加载中...' }}</p>
        <p v-if="slowLoadingWarning" class="slow-loading-warning">
          加载较慢，请耐心等待或尝试刷新
        </p>
      </div>
      
      <!-- Error overlay -->
      <div v-if="error" class="error-overlay">
        <div class="error-icon">⚠️</div>
        <p>{{ errorMessage }}</p>
        <p v-if="retryCount > 0" class="retry-info">已重试 {{ retryCount }} 次</p>
        <button class="btn btn-primary" @click="retry">重试</button>
      </div>
      
      <!-- Gesture feedback overlay -->
      <div v-if="gestureText" class="gesture-overlay">
        <span class="gesture-text">{{ gestureText }}</span>
      </div>
    </div>
    
    <!-- Custom control bar -->
    <div class="control-bar">
      <div class="control-row">
        <!-- Playback speed -->
        <div class="control-group">
          <label>倍速</label>
          <select v-model="playbackRate" @change="changePlaybackRate" class="speed-select">
            <option value="0.5">0.5x</option>
            <option value="0.75">0.75x</option>
            <option value="1">1x</option>
            <option value="1.25">1.25x</option>
            <option value="1.5">1.5x</option>
            <option value="2">2x</option>
          </select>
        </div>
        
        <!-- Fullscreen button -->
        <button class="control-btn fullscreen-btn" @click="toggleFullscreen" :title="isFullscreen ? '退出全屏' : '全屏'">
          <span v-if="!isFullscreen">⛶</span>
          <span v-else>⮌</span>
        </button>
      </div>
    </div>
    
    <!-- Episode selector if multiple sources -->
    <div v-if="episodes.length > 1" class="episode-list">
      <h4>选集</h4>
      <div class="episodes">
        <button
          v-for="(episode, index) in episodes"
          :key="index"
          :class="['episode-btn', { active: currentEpisode === index }]"
          @click="selectEpisode(index)"
        >
          {{ episode.name || `第${index + 1}集` }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { formatImageUrl, safeEncodeURI, loadImageWithBase64Detection } from '@/utils/imageUtils'

export default {
  name: 'VideoPlayer',
  props: {
    src: {
      type: String,
      default: ''
    },
    poster: {
      type: String,
      default: ''
    },
    autoplay: {
      type: Boolean,
      default: false
    }
  },
  emits: ['play', 'pause', 'ended', 'error', 'time-update'],
  data() {
    return {
      loading: true,
      buffering: false,
      error: false,
      errorMessage: '',
      episodes: [],
      currentEpisode: 0,
      currentSrc: '',
      playbackRate: '1',
      isFullscreen: false,
      // Computed poster URL after base64 detection
      computedPoster: '',
      // Gesture support
      touchStartX: 0,
      touchStartY: 0,
      touchStartTime: 0,
      isSeeking: false,
      gestureText: '',
      gestureTimeout: null,
      // Track if initial autoplay has been triggered
      hasAutoplayTriggered: false,
      // Video loading performance tracking
      loadStartTime: null,
      slowLoadingWarning: false,
      slowLoadingTimeout: null,
      retryCount: 0,
      maxRetries: 3,
      // Slow loading threshold in milliseconds (5 seconds)
      slowLoadingThreshold: 5000,
      // Track source for retry validation (prevent retrying wrong source)
      retrySourceUrl: '',
      // Retry timeout for cleanup
      retryTimeout: null
    }
  },
  watch: {
    src: {
      immediate: true,
      handler(newSrc) {
        this.parseSource(newSrc)
      }
    },
    poster: {
      immediate: true,
      handler(newPoster) {
        this.loadPoster(newPoster)
      }
    }
  },
  mounted() {
    // Listen for fullscreen changes
    document.addEventListener('fullscreenchange', this.handleFullscreenChange)
    document.addEventListener('webkitfullscreenchange', this.handleFullscreenChange)
  },
  beforeUnmount() {
    document.removeEventListener('fullscreenchange', this.handleFullscreenChange)
    document.removeEventListener('webkitfullscreenchange', this.handleFullscreenChange)
    if (this.gestureTimeout) {
      clearTimeout(this.gestureTimeout)
    }
    // Clear slow loading timeout
    this.clearSlowLoadingTimeout()
    // Clear retry timeout to prevent memory leak
    if (this.retryTimeout) {
      clearTimeout(this.retryTimeout)
      this.retryTimeout = null
    }
  },
  methods: {
    // Clear slow loading detection timeout
    clearSlowLoadingTimeout() {
      if (this.slowLoadingTimeout) {
        clearTimeout(this.slowLoadingTimeout)
        this.slowLoadingTimeout = null
      }
    },
    
    // Start slow loading detection
    startSlowLoadingDetection() {
      this.loadStartTime = Date.now()
      this.slowLoadingWarning = false
      this.clearSlowLoadingTimeout()
      
      this.slowLoadingTimeout = setTimeout(() => {
        if (this.loading || this.buffering) {
          this.slowLoadingWarning = true
        }
      }, this.slowLoadingThreshold)
    },
    
    // Stop slow loading detection and reset state
    stopSlowLoadingDetection() {
      this.clearSlowLoadingTimeout()
      this.slowLoadingWarning = false
    },
    
    parseSource(src) {
      // Reset autoplay flag when source changes
      this.hasAutoplayTriggered = false
      
      if (!src) {
        this.currentSrc = ''
        this.episodes = []
        return
      }
      
      // Parse multiple episodes format: name1$url1#name2$url2
      if (src.includes('#')) {
        const parts = src.split('#')
        this.episodes = parts.map(part => {
          if (part.includes('$')) {
            const [name, url] = part.split('$')
            return { name, url }
          }
          return { name: '', url: part }
        })
        this.selectEpisode(0)
      } else if (src.includes('$')) {
        const [name, url] = src.split('$')
        this.episodes = [{ name, url }]
        this.currentSrc = url
      } else {
        this.episodes = [{ name: '', url: src }]
        this.currentSrc = src
      }
    },
    
    selectEpisode(index) {
      this.currentEpisode = index
      if (this.episodes[index]) {
        this.currentSrc = this.episodes[index].url
        this.loading = true
        this.error = false
        // Reset autoplay flag for new episode
        this.hasAutoplayTriggered = false
        // Reset retry count for new episode
        this.retryCount = 0
        // Start slow loading detection
        this.startSlowLoadingDetection()
        
        this.$nextTick(() => {
          if (this.$refs.videoElement) {
            this.$refs.videoElement.load()
            // Autoplay is now handled in onCanPlay() for consistency
          }
        })
      }
    },
    
    onPlay() {
      this.loading = false
      this.buffering = false
      // Stop slow loading detection on successful play
      this.stopSlowLoadingDetection()
      this.$emit('play')
    },
    
    onPause() {
      this.$emit('pause')
    },
    
    onEnded() {
      this.$emit('ended')
      // Auto play next episode
      if (this.currentEpisode < this.episodes.length - 1) {
        this.selectEpisode(this.currentEpisode + 1)
      }
    },
    
    onError(e) {
      this.loading = false
      this.buffering = false
      this.stopSlowLoadingDetection()
      
      // Determine specific error message based on video element error code
      const video = this.$refs.videoElement
      let errorMsg = '视频加载失败，请稍后重试'
      let isNetworkError = false
      
      if (video && video.error) {
        // Use numeric codes for cross-browser compatibility
        // MediaError constants may not be defined in all browsers
        const errorCode = video.error.code
        switch (errorCode) {
          case 1: // MEDIA_ERR_ABORTED
            errorMsg = '视频加载被中断'
            break
          case 2: // MEDIA_ERR_NETWORK
            errorMsg = '网络错误，视频加载失败'
            isNetworkError = true
            break
          case 3: // MEDIA_ERR_DECODE
            errorMsg = '视频格式不支持或解码错误'
            break
          case 4: // MEDIA_ERR_SRC_NOT_SUPPORTED
            errorMsg = '不支持的视频格式或无效链接'
            break
        }
      }
      
      // Store the source URL for retry validation
      this.retrySourceUrl = this.currentSrc
      
      // Auto-retry for network errors if retries remaining
      if (this.retryCount < this.maxRetries && isNetworkError) {
        this.retryCount++
        // Show error state briefly so user knows retry is happening
        this.error = true
        this.errorMessage = `${errorMsg}，正在重试...`
        
        // Retry with exponential backoff (1s, 2s, 4s)
        const delay = Math.pow(2, this.retryCount - 1) * 1000
        const srcAtError = this.currentSrc
        
        // Clear any existing retry timeout
        if (this.retryTimeout) {
          clearTimeout(this.retryTimeout)
        }
        
        this.retryTimeout = setTimeout(() => {
          // Skip if source changed (user loaded different video)
          if (this.currentSrc !== srcAtError) return
          
          this.loading = true
          this.error = false
          this.startSlowLoadingDetection()
          if (this.$refs.videoElement) {
            this.$refs.videoElement.load()
          }
        }, delay)
        return
      }
      
      this.error = true
      this.errorMessage = errorMsg
      this.$emit('error', e)
    },
    
    onLoadedMetadata() {
      this.loading = false
      // Stop slow loading detection - metadata loaded successfully
      this.stopSlowLoadingDetection()
    },
    
    onWaiting() {
      this.buffering = true
      // Only start slow loading detection if not already running
      // (avoid multiple overlapping timers)
      if (!this.slowLoadingTimeout) {
        this.startSlowLoadingDetection()
      }
    },
    
    onCanPlay() {
      this.buffering = false
      // Stop slow loading detection - video is ready to play
      this.stopSlowLoadingDetection()
      // Auto-play when video is ready and autoplay is enabled (only trigger once per video load)
      if (this.autoplay && !this.hasAutoplayTriggered && this.$refs.videoElement && this.$refs.videoElement.paused) {
        this.hasAutoplayTriggered = true
        this.$refs.videoElement.play().catch(err => {
          console.log('Auto-play blocked:', err)
        })
      }
    },
    
    // Video load start event - start tracking load time
    onLoadStart() {
      this.loading = true
      this.startSlowLoadingDetection()
    },
    
    // Video progress event - data is being downloaded
    onProgress() {
      // Reset slow loading warning when progress is being made
      // regardless of buffering state (indicates data is flowing)
      if (this.slowLoadingWarning) {
        this.slowLoadingWarning = false
      }
    },
    
    // Video stalled event - browser is trying to fetch but no data is coming
    onStalled() {
      // Only show warning if we're still loading or buffering
      if (this.loading || this.buffering) {
        this.slowLoadingWarning = true
      }
    },
    
    onTimeUpdate() {
      const video = this.$refs.videoElement
      if (video) {
        this.$emit('time-update', {
          currentTime: video.currentTime,
          duration: video.duration
        })
      }
    },
    
    // Manual retry - reset counter for fresh start
    retry() {
      this.error = false
      this.loading = true
      // Reset retry count for manual retry (gives user full set of auto-retries again)
      this.retryCount = 0
      this.startSlowLoadingDetection()
      if (this.$refs.videoElement) {
        this.$refs.videoElement.load()
      }
    },
    
    // Playback rate control
    changePlaybackRate() {
      if (this.$refs.videoElement) {
        this.$refs.videoElement.playbackRate = parseFloat(this.playbackRate)
      }
    },
    
    // Fullscreen control
    async toggleFullscreen() {
      const container = this.$refs.playerContainer
      
      try {
        if (!this.isFullscreen) {
          if (container.requestFullscreen) {
            await container.requestFullscreen()
          } else if (container.webkitRequestFullscreen) {
            await container.webkitRequestFullscreen()
          } else if (this.$refs.videoElement.webkitEnterFullscreen) {
            // iOS Safari
            await this.$refs.videoElement.webkitEnterFullscreen()
          }
        } else {
          if (document.exitFullscreen) {
            await document.exitFullscreen()
          } else if (document.webkitExitFullscreen) {
            await document.webkitExitFullscreen()
          }
        }
      } catch (err) {
        console.error('Fullscreen error:', err)
      }
    },
    
    handleFullscreenChange() {
      this.isFullscreen = !!(document.fullscreenElement || document.webkitFullscreenElement)
    },
    
    // Touch gesture handlers
    onTouchStart(e) {
      if (e.touches.length === 1) {
        this.touchStartX = e.touches[0].clientX
        this.touchStartY = e.touches[0].clientY
        this.touchStartTime = this.$refs.videoElement?.currentTime || 0
        this.isSeeking = false
      }
    },
    
    onTouchMove(e) {
      if (e.touches.length !== 1) return
      
      const deltaX = e.touches[0].clientX - this.touchStartX
      const deltaY = e.touches[0].clientY - this.touchStartY
      
      // Horizontal swipe for seeking (more than 30px and more horizontal than vertical)
      if (Math.abs(deltaX) > 30 && Math.abs(deltaX) > Math.abs(deltaY) * 2) {
        this.isSeeking = true
        const video = this.$refs.videoElement
        if (video && video.duration) {
          // Calculate seek time: 100px = 10 seconds
          const seekTime = (deltaX / 100) * 10
          const diff = seekTime >= 0 ? `+${Math.round(seekTime)}s` : `${Math.round(seekTime)}s`
          this.showGestureText(diff)
        }
      }
    },
    
    onTouchEnd(e) {
      if (this.isSeeking) {
        const video = this.$refs.videoElement
        if (video && video.duration) {
          const deltaX = e.changedTouches[0].clientX - this.touchStartX
          const seekTime = (deltaX / 100) * 10
          const newTime = Math.max(0, Math.min(video.duration, this.touchStartTime + seekTime))
          video.currentTime = newTime
        }
        this.isSeeking = false
      }
    },
    
    onDoubleClick(e) {
      // On desktop, double-click toggles fullscreen
      // (Different from mobile touch where we use zones for seek)
      if (!('ontouchstart' in window)) {
        // Desktop: toggle fullscreen
        this.toggleFullscreen()
        return
      }
      
      // Mobile: use zone-based behavior
      const container = this.$refs.playerContainer
      const rect = container.getBoundingClientRect()
      const x = e.clientX - rect.left
      const width = rect.width
      
      const video = this.$refs.videoElement
      if (!video) return
      
      // Double tap on left side: rewind 10s
      // Double tap on right side: forward 10s
      // Double tap in center: toggle play/pause
      if (x < width / 3) {
        video.currentTime = Math.max(0, video.currentTime - 10)
        this.showGestureText('-10s')
      } else if (x > width * 2 / 3) {
        video.currentTime = Math.min(video.duration || 0, video.currentTime + 10)
        this.showGestureText('+10s')
      } else {
        if (video.paused) {
          video.play()
        } else {
          video.pause()
        }
      }
    },
    
    showGestureText(text) {
      this.gestureText = text
      if (this.gestureTimeout) {
        clearTimeout(this.gestureTimeout)
      }
      this.gestureTimeout = setTimeout(() => {
        this.gestureText = ''
      }, 800)
    },
    
    // Public methods
    play() {
      if (this.$refs.videoElement) {
        this.$refs.videoElement.play()
      }
    },
    
    pause() {
      if (this.$refs.videoElement) {
        this.$refs.videoElement.pause()
      }
    },
    
    seek(time) {
      if (this.$refs.videoElement) {
        this.$refs.videoElement.currentTime = time
      }
    },
    
    setPlaybackRate(rate) {
      this.playbackRate = String(rate)
      this.changePlaybackRate()
    },
    
    // Load poster image with base64 detection
    async loadPoster(posterUrl) {
      if (!posterUrl) {
        this.computedPoster = ''
        return
      }
      
      // Create a temporary image element to use with loadImageWithBase64Detection
      const tempImg = new Image()
      await loadImageWithBase64Detection(tempImg, posterUrl)
      this.computedPoster = tempImg.src || ''
    },
    
    // Use shared utilities for image and URL formatting
    formatImageUrl,
    safeEncodeURI
  }
}
</script>

<style scoped>
.video-player {
  width: 100%;
  background: #000;
  border-radius: 12px;
  overflow: hidden;
}

.video-player.is-fullscreen {
  border-radius: 0;
}

.player-wrapper {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 aspect ratio */
  touch-action: pan-y; /* Allow vertical scrolling but handle horizontal */
}

.player-wrapper video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #000;
}

.loading-overlay,
.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.8);
  color: #fff;
  pointer-events: none;
  z-index: 10;
}

.error-overlay {
  pointer-events: auto;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #00d4ff;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-overlay p,
.error-overlay p {
  margin-top: 15px;
  color: #888;
}

.slow-loading-warning {
  color: #ffa500;
  font-size: 0.85em;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 1; }
}

.retry-info {
  color: #aaa;
  font-size: 0.8em;
}

.error-icon {
  font-size: 3em;
  margin-bottom: 10px;
}

.error-overlay .btn {
  margin-top: 15px;
}

/* Gesture feedback overlay */
.gesture-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 20;
  pointer-events: none;
}

.gesture-text {
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 1.2em;
  font-weight: bold;
}

/* Control bar */
.control-bar {
  padding: 10px 15px;
  background: rgba(255, 255, 255, 0.05);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.control-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.control-group label {
  color: #888;
  font-size: 0.85em;
}

.speed-select {
  padding: 6px 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  outline: none;
}

.speed-select option {
  background: #1a1a2e;
  color: #fff;
}

.control-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s;
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: #00d4ff;
}

.episode-list {
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
}

.episode-list h4 {
  margin-bottom: 10px;
  color: #fff;
  font-size: 1em;
}

.episodes {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.episode-btn {
  padding: 8px 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.episode-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: #00d4ff;
}

.episode-btn.active {
  background: linear-gradient(90deg, #00d4ff, #7c3aed);
  border-color: transparent;
}

/* Mobile responsive */
@media (max-width: 480px) {
  .control-bar {
    padding: 8px 10px;
  }
  
  .control-group label {
    display: none;
  }
  
  .speed-select {
    padding: 5px 8px;
    font-size: 12px;
  }
  
  .control-btn {
    width: 32px;
    height: 32px;
    font-size: 16px;
  }
  
  .episode-list {
    padding: 10px;
  }
  
  .episode-btn {
    padding: 6px 12px;
    font-size: 12px;
  }
}

/* Tablet */
@media (min-width: 481px) and (max-width: 768px) {
  .episodes {
    max-height: 120px;
    overflow-y: auto;
  }
}

/* Fullscreen mode adjustments */
.is-fullscreen .control-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
  padding: 20px 15px 15px;
  z-index: 30;
}

.is-fullscreen .episode-list {
  position: absolute;
  bottom: 60px;
  left: 0;
  right: 0;
  max-height: 150px;
  overflow-y: auto;
  z-index: 25;
}
</style>
