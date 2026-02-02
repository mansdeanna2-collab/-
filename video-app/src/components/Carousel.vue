<template>
  <div class="carousel" v-if="videos.length > 0">
    <div 
      class="carousel-container" 
      ref="container"
      @touchstart="onTouchStart"
      @touchmove="onTouchMove"
      @touchend="onTouchEnd"
    >
      <div 
        class="carousel-track"
        :style="trackStyle"
      >
        <div 
          class="carousel-slide"
          v-for="(video, index) in videos"
          :key="video.video_id || index"
          @click="handleSlideClick(video)"
        >
          <img 
            v-if="video.video_image"
            :ref="el => setImgRef(el, index)"
            :alt="video.video_title"
            class="slide-image"
            @error="handleImageError"
          />
          <div class="slide-overlay">
            <h3 class="slide-title">{{ video.video_title }}</h3>
            <div v-if="video.video_category" class="slide-category">
              {{ video.video_category }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Indicators -->
    <div class="carousel-indicators">
      <span 
        v-for="(_, index) in videos"
        :key="index"
        :class="['indicator', { active: index === currentIndex }]"
        @click="goToSlide(index)"
      ></span>
    </div>
  </div>
</template>

<script>
import { formatImageUrl, loadImageWithBase64Detection } from '@/utils/imageUtils'

export default {
  name: 'CarouselComponent',
  props: {
    videos: {
      type: Array,
      default: () => []
    },
    autoplay: {
      type: Boolean,
      default: true
    },
    interval: {
      type: Number,
      default: 4000
    }
  },
  emits: ['click'],
  data() {
    return {
      currentIndex: 0,
      timer: null,
      imgRefs: {},
      loadedUrls: new Set(),
      // Touch swipe support
      touchStartX: 0,
      touchStartY: 0,
      touchDeltaX: 0,
      isSwiping: false,
      swipeThreshold: 50
    }
  },
  computed: {
    trackStyle() {
      const baseTranslate = -this.currentIndex * 100
      const containerWidth = this.$refs.container?.offsetWidth || 1
      const swipeOffset = this.isSwiping ? (this.touchDeltaX / containerWidth) * 100 : 0
      return {
        transform: `translateX(calc(${baseTranslate}% + ${swipeOffset}%))`,
        transition: this.isSwiping ? 'none' : 'transform 0.5s ease'
      }
    }
  },
  watch: {
    videos: {
      immediate: true,
      handler() {
        this.currentIndex = 0
        this.loadedUrls.clear()
        this.startAutoplay()
        this.$nextTick(() => {
          this.loadAllImages()
        })
      }
    }
  },
  mounted() {
    this.startAutoplay()
    this.loadAllImages()
  },
  beforeUnmount() {
    this.stopAutoplay()
  },
  methods: {
    formatImageUrl,
    setImgRef(el, index) {
      if (el) {
        this.imgRefs[index] = el
      }
    },
    async loadAllImages() {
      // Load all images in parallel for better performance
      const loadPromises = this.videos.map((video, i) => {
        const imgUrl = video?.video_image
        if (imgUrl && this.imgRefs[i] && !this.loadedUrls.has(imgUrl)) {
          this.loadedUrls.add(imgUrl)
          return loadImageWithBase64Detection(this.imgRefs[i], imgUrl)
        }
        return Promise.resolve()
      })
      await Promise.allSettled(loadPromises)
    },
    handleImageError(e) {
      e.target.src = ''
      e.target.style.background = 'linear-gradient(135deg, #2a2a4a 0%, #1a1a3e 100%)'
    },
    handleSlideClick(video) {
      // Only emit click if not swiping
      if (!this.isSwiping && Math.abs(this.touchDeltaX) < 10) {
        this.$emit('click', video)
      }
    },
    goToSlide(index) {
      this.currentIndex = index
      this.startAutoplay()
    },
    nextSlide() {
      if (this.videos.length > 0) {
        this.currentIndex = (this.currentIndex + 1) % this.videos.length
      }
    },
    prevSlide() {
      if (this.videos.length > 0) {
        this.currentIndex = (this.currentIndex - 1 + this.videos.length) % this.videos.length
      }
    },
    startAutoplay() {
      this.stopAutoplay()
      if (this.autoplay && this.videos.length > 1) {
        this.timer = window.setInterval(() => {
          this.nextSlide()
        }, this.interval)
      }
    },
    stopAutoplay() {
      if (this.timer) {
        window.clearInterval(this.timer)
        this.timer = null
      }
    },
    // Touch event handlers for swipe support
    onTouchStart(e) {
      if (e.touches.length !== 1) return
      this.touchStartX = e.touches[0].clientX
      this.touchStartY = e.touches[0].clientY
      this.touchDeltaX = 0
      this.isSwiping = false
      this.stopAutoplay()
    },
    onTouchMove(e) {
      if (e.touches.length !== 1) return
      
      const deltaX = e.touches[0].clientX - this.touchStartX
      const deltaY = e.touches[0].clientY - this.touchStartY
      
      // Only consider horizontal swipes (ignore vertical scrolling)
      if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 10) {
        this.isSwiping = true
        this.touchDeltaX = deltaX
        // Prevent vertical scrolling while swiping
        e.preventDefault()
      }
    },
    onTouchEnd() {
      if (this.isSwiping) {
        if (this.touchDeltaX > this.swipeThreshold) {
          this.prevSlide()
        } else if (this.touchDeltaX < -this.swipeThreshold) {
          this.nextSlide()
        }
      }
      
      this.isSwiping = false
      this.touchDeltaX = 0
      this.startAutoplay()
    }
  }
}
</script>

<style scoped>
.carousel {
  position: relative;
  width: 100%;
  border-radius: 20px;
  overflow: hidden;
  margin-bottom: 20px;
  /* Purple border to distinguish from regular videos */
  border: 2px solid transparent;
  background: linear-gradient(#0f0f1a, #0f0f1a) padding-box,
              linear-gradient(135deg, #7c3aed, #a855f7, #7c3aed) border-box;
}

.carousel-container {
  width: 100%;
  overflow: hidden;
}

.carousel-track {
  display: flex;
  transition: transform 0.5s ease;
}

.carousel-slide {
  flex: 0 0 100%;
  position: relative;
  aspect-ratio: 2.5/1;
  cursor: pointer;
  background: linear-gradient(135deg, #2a2a4a 0%, #1a1a3e 100%);
}

.slide-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.slide-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.85));
}

.slide-title {
  color: #fff;
  font-size: 1.2em;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 0;
}

.slide-category {
  display: inline-block;
  margin-top: 8px;
  padding: 3px 10px;
  background: rgba(124, 58, 237, 0.2);
  border: 1px solid rgba(124, 58, 237, 0.4);
  border-radius: 12px;
  font-size: 0.75em;
  color: #a855f7;
}

.carousel-indicators {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
  z-index: 10;
}

.indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid rgba(124, 58, 237, 0.3);
}

.indicator.active {
  background: linear-gradient(135deg, #7c3aed, #a855f7);
  width: 24px;
  border-radius: 4px;
  border-color: #7c3aed;
}

@media (max-width: 480px) {
  .carousel {
    border-radius: 16px;
    margin-bottom: 15px;
  }
  
  .slide-overlay {
    padding: 12px;
  }
  
  .slide-title {
    font-size: 1em;
  }
  
  .slide-category {
    font-size: 0.65em;
    margin-top: 6px;
  }
  
  .indicator {
    width: 6px;
    height: 6px;
  }
  
  .indicator.active {
    width: 18px;
  }
}
</style>
