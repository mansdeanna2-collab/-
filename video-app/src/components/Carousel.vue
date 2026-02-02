<template>
  <div class="carousel" v-if="videos.length > 0">
    <div class="carousel-container" ref="container">
      <div 
        class="carousel-track"
        :style="{ transform: `translateX(-${currentIndex * 100}%)` }"
      >
        <div 
          class="carousel-slide"
          v-for="(video, index) in videos"
          :key="video.video_id || index"
          @click="$emit('click', video)"
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
      loadedUrls: new Set()
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
    goToSlide(index) {
      this.currentIndex = index
      this.startAutoplay()
    },
    nextSlide() {
      if (this.videos.length > 0) {
        this.currentIndex = (this.currentIndex + 1) % this.videos.length
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
    }
  }
}
</script>

<style scoped>
.carousel {
  position: relative;
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 20px;
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
  aspect-ratio: 16/9;
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
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
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
}

.carousel-indicators {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
}

.indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.3s;
}

.indicator.active {
  background: #00d4ff;
  width: 20px;
  border-radius: 4px;
}

@media (max-width: 480px) {
  .carousel {
    border-radius: 8px;
    margin-bottom: 15px;
  }
  
  .slide-overlay {
    padding: 12px;
  }
  
  .slide-title {
    font-size: 1em;
  }
  
  .indicator {
    width: 6px;
    height: 6px;
  }
  
  .indicator.active {
    width: 16px;
  }
}
</style>
