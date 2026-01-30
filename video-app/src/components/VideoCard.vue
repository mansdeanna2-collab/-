<template>
  <div class="video-card" @click="handleClick">
    <div class="thumbnail">
      <img 
        v-if="video.video_image" 
        :src="formatImageUrl(video.video_image)" 
        :alt="video.video_title"
        @error="handleImageError"
        loading="lazy"
      />
      <div v-else class="placeholder">
        <span>🎬</span>
      </div>
      <div class="play-icon">
        <span class="play-arrow"></span>
      </div>
      <div v-if="video.video_duration" class="duration">
        {{ video.video_duration }}
      </div>
    </div>
    <div class="info">
      <h3 class="title">{{ video.video_title }}</h3>
      <div class="meta">
        <span v-if="video.video_category" class="category">
          {{ video.video_category }}
        </span>
        <span v-if="video.play_count" class="play-count">
          {{ formatPlayCount(video.play_count) }} 次播放
        </span>
      </div>
      <div v-if="video.video_coins > 0" class="coins">
        <span class="coin-icon">🪙</span>
        {{ video.video_coins }} 金币
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VideoCard',
  props: {
    video: {
      type: Object,
      required: true
    }
  },
  emits: ['click'],
  methods: {
    handleClick() {
      this.$emit('click', this.video)
    },
    handleImageError(e) {
      e.target.style.display = 'none'
      e.target.parentElement.querySelector('.placeholder')?.style.setProperty('display', 'flex')
    },
    formatPlayCount(count) {
      if (count >= 10000) {
        return (count / 10000).toFixed(1) + '万'
      }
      return count.toString()
    },
    // Format image URL - handles base64 content, data URLs, and regular URLs
    formatImageUrl(url) {
      if (!url) return ''
      
      // If already a data URL, return as-is
      if (url.startsWith('data:')) {
        return url
      }
      
      // If already a valid URL (http/https), encode and return
      if (url.startsWith('http://') || url.startsWith('https://')) {
        try {
          const decoded = decodeURI(url)
          if (decoded !== url) {
            return url // Already encoded
          }
          return encodeURI(url)
        } catch (e) {
          return url
        }
      }
      
      // Check for known base64 image headers first
      // /9j/ is the base64 encoding of JPEG file signature (FFD8FF)
      if (url.startsWith('/9j/')) {
        return 'data:image/jpeg;base64,' + url
      }
      // iVBOR is the base64 encoding of PNG file signature
      if (url.startsWith('iVBOR')) {
        return 'data:image/png;base64,' + url
      }
      // R0lGOD is the base64 encoding of GIF file signature
      if (url.startsWith('R0lGOD')) {
        return 'data:image/gif;base64,' + url
      }
      
      // For other potential base64 content: must be long and contain only base64 characters
      // This is a conservative check to avoid false positives
      if (url.length > 100 && /^[A-Za-z0-9+/]+=*$/.test(url.replace(/\s/g, ''))) {
        // Default to PNG for unknown base64 content
        return 'data:image/png;base64,' + url
      }
      
      // Otherwise, treat as regular URL and encode
      try {
        return encodeURI(url)
      } catch (e) {
        return url
      }
    }
  }
}
</script>

<style scoped>
.video-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.video-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  border-color: #00d4ff;
}

/* Touch device support - show play icon on touch */
.video-card:active .play-icon {
  opacity: 1;
}

.thumbnail {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 aspect ratio */
  background: linear-gradient(135deg, #2a2a4a 0%, #1a1a3e 100%);
  overflow: hidden;
}

.thumbnail img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
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
  font-size: 3em;
  color: #888;
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
  transition: all 0.3s;
}

.video-card:hover .play-icon {
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

.duration {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.7);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.info {
  padding: 15px;
}

.title {
  font-size: 1em;
  font-weight: 600;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
}

.meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 5px;
  font-size: 0.85em;
  color: #8b8b8b;
}

.category {
  background: rgba(0, 212, 255, 0.2);
  color: #00d4ff;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75em;
}

.play-count {
  color: #888;
  font-size: 0.8em;
}

.coins {
  margin-top: 8px;
  color: #ffd700;
  font-size: 0.85em;
  display: flex;
  align-items: center;
  gap: 4px;
}

.coin-icon {
  font-size: 1em;
}

/* Small mobile devices */
@media (max-width: 480px) {
  .video-card {
    border-radius: 10px;
  }
  
  .info {
    padding: 10px;
  }
  
  .title {
    font-size: 0.9em;
    margin-bottom: 5px;
  }
  
  .meta {
    font-size: 0.75em;
  }
  
  .category {
    padding: 2px 8px;
    font-size: 0.7em;
  }
  
  .play-icon {
    width: 40px;
    height: 40px;
  }
  
  .play-arrow {
    border-width: 6px 0 6px 10px;
  }
}

/* Tablet and small desktops */
@media (min-width: 481px) and (max-width: 1024px) {
  .info {
    padding: 12px;
  }
}

/* Large desktops */
@media (min-width: 1400px) {
  .info {
    padding: 18px;
  }
  
  .title {
    font-size: 1.1em;
  }
}
</style>
