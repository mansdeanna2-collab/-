<template>
  <div class="category-section">
    <div class="section-header">
      <h2 class="section-title">{{ title }}</h2>
    </div>
    
    <div class="videos-grid" v-if="videos.length > 0">
      <!-- Large video (first one) -->
      <div class="video-large" @click="$emit('play', videos[0])">
        <div class="video-thumbnail">
          <img 
            v-if="videos[0].video_image"
            ref="largeImg"
            :alt="videos[0].video_title"
            @error="handleImageError"
          />
          <div class="play-icon">
            <span class="play-arrow"></span>
          </div>
          <div class="video-duration" v-if="videos[0].video_duration">
            {{ videos[0].video_duration }}
          </div>
        </div>
        <div class="video-info">
          <h3 class="video-title">{{ videos[0].video_title }}</h3>
          <span class="play-count" v-if="videos[0].play_count">
            {{ formatPlayCount(videos[0].play_count) }}次播放
          </span>
        </div>
      </div>
      
      <!-- Small videos (2+2 grid) -->
      <div class="videos-small">
        <div 
          class="video-small"
          v-for="(video, index) in videos.slice(1, 5)"
          :key="video.video_id"
          @click="$emit('play', video)"
        >
          <div class="video-thumbnail">
            <img 
              v-if="video.video_image"
              :ref="el => setSmallImgRef(el, index)"
              :alt="video.video_title"
              @error="handleImageError"
            />
            <div class="play-icon">
              <span class="play-arrow"></span>
            </div>
            <div class="video-duration" v-if="video.video_duration">
              {{ video.video_duration }}
            </div>
          </div>
          <div class="video-info">
            <h3 class="video-title">{{ video.video_title }}</h3>
            <span class="play-count" v-if="video.play_count">
              {{ formatPlayCount(video.play_count) }}次播放
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Action buttons below videos -->
    <div class="section-actions" v-if="videos.length > 0">
      <button class="action-btn refresh-btn" @click="$emit('refresh')">
        <span class="refresh-icon">🔄</span>
        换一换
      </button>
      <button class="action-btn more-btn" @click="$emit('more')">
        查看更多
        <span class="arrow-icon">→</span>
      </button>
    </div>
    
    <!-- Empty state -->
    <div v-else class="empty-state">
      <p>暂无视频</p>
    </div>
  </div>
</template>

<script>
import { formatImageUrl, loadImageWithBase64Detection } from '@/utils/imageUtils'
import { formatPlayCount } from '@/utils/formatUtils'

export default {
  name: 'CategorySection',
  props: {
    title: {
      type: String,
      required: true
    },
    videos: {
      type: Array,
      default: () => []
    }
  },
  emits: ['play', 'refresh', 'more'],
  data() {
    return {
      smallImgRefs: {},
      loadedUrls: new Set()
    }
  },
  watch: {
    videos: {
      immediate: true,
      handler() {
        this.loadedUrls.clear()
        this.$nextTick(() => {
          this.loadAllImages()
        })
      }
    }
  },
  mounted() {
    this.loadAllImages()
  },
  methods: {
    formatImageUrl,
    formatPlayCount,
    setSmallImgRef(el, index) {
      if (el) {
        this.smallImgRefs[index] = el
      }
    },
    async loadAllImages() {
      const loadPromises = []
      
      // Load large video image
      if (this.videos.length > 0 && this.videos[0].video_image && this.$refs.largeImg) {
        const url = this.videos[0].video_image
        if (!this.loadedUrls.has(url)) {
          this.loadedUrls.add(url)
          loadPromises.push(loadImageWithBase64Detection(this.$refs.largeImg, url))
        }
      }
      
      // Load small video images in parallel
      const smallVideos = this.videos.slice(1, 5)
      for (let i = 0; i < smallVideos.length; i++) {
        const video = smallVideos[i]
        const imgUrl = video?.video_image
        if (imgUrl && this.smallImgRefs[i] && !this.loadedUrls.has(imgUrl)) {
          this.loadedUrls.add(imgUrl)
          loadPromises.push(loadImageWithBase64Detection(this.smallImgRefs[i], imgUrl))
        }
      }
      
      // Wait for all images to load
      await Promise.allSettled(loadPromises)
    },
    handleImageError(e) {
      e.target.src = ''
      e.target.closest('.video-thumbnail').classList.add('no-image')
    }
  }
}
</script>

<style scoped>
.category-section {
  margin-bottom: 25px;
}

.section-header {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin-bottom: 15px;
  padding: 0 5px;
}

.section-title {
  font-size: 1.2em;
  font-weight: 600;
  color: #fff;
}

.section-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 15px;
  padding: 10px 0;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  color: #aaa;
  font-size: 0.9em;
  cursor: pointer;
  transition: all 0.3s;
  min-width: 100px;
}

.action-btn:hover {
  color: #00d4ff;
  background: rgba(0, 212, 255, 0.15);
  border-color: rgba(0, 212, 255, 0.3);
}

.action-btn:active {
  transform: scale(0.98);
}

.refresh-icon {
  font-size: 0.9em;
}

.arrow-icon {
  font-size: 1em;
}

.videos-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.video-large {
  width: 100%;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.video-large:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.video-thumbnail {
  position: relative;
  width: 100%;
  padding-top: 56.25%;
  background: linear-gradient(135deg, #2a2a4a 0%, #1a1a3e 100%);
  overflow: hidden;
}

.video-thumbnail.no-image {
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-thumbnail img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.play-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 50px;
  height: 50px;
  background: rgba(0, 212, 255, 0.9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.video-large:hover .play-icon,
.video-small:hover .play-icon {
  opacity: 1;
}

.play-arrow {
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 8px 0 8px 14px;
  border-color: transparent transparent transparent #fff;
  margin-left: 4px;
}

.video-duration {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.8);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75em;
  color: #fff;
}

.video-info {
  padding: 12px;
}

.video-title {
  font-size: 0.95em;
  font-weight: 500;
  color: #fff;
  margin-bottom: 5px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
}

.play-count {
  font-size: 0.8em;
  color: #888;
}

.videos-small {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.video-small {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.video-small:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}

.video-small .video-thumbnail {
  padding-top: 56.25%;
}

.video-small .play-icon {
  width: 36px;
  height: 36px;
}

.video-small .play-arrow {
  border-width: 6px 0 6px 10px;
}

.video-small .video-info {
  padding: 10px;
}

.video-small .video-title {
  font-size: 0.85em;
  -webkit-line-clamp: 1;
}

.video-small .play-count {
  font-size: 0.75em;
}

.empty-state {
  padding: 30px;
  text-align: center;
  color: #888;
}

/* Mobile responsive */
@media (max-width: 480px) {
  .category-section {
    margin-bottom: 20px;
  }
  
  .section-header {
    margin-bottom: 10px;
  }
  
  .section-title {
    font-size: 1em;
  }
  
  .section-actions {
    gap: 12px;
    margin-top: 12px;
    padding: 8px 0;
  }
  
  .action-btn {
    padding: 8px 14px;
    font-size: 0.8em;
    min-width: 85px;
  }
  
  .video-large {
    border-radius: 10px;
  }
  
  .video-info {
    padding: 10px;
  }
  
  .video-title {
    font-size: 0.85em;
  }
  
  .videos-small {
    gap: 8px;
  }
  
  .video-small {
    border-radius: 8px;
  }
  
  .video-small .video-info {
    padding: 8px;
  }
  
  .video-small .video-title {
    font-size: 0.75em;
  }
  
  .play-icon {
    width: 40px;
    height: 40px;
  }
}
</style>
