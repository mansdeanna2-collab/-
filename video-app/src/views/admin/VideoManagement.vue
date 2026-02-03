<template>
  <div class="video-management-page">
    <!-- Tab Navigation -->
    <div class="tab-nav">
      <button 
        v-for="tab in tabs" 
        :key="tab.key"
        :class="['tab-btn', { active: activeTab === tab.key }]"
        @click="activeTab = tab.key"
      >
        <span class="tab-icon">{{ tab.icon }}</span>
        {{ tab.label }}
      </button>
    </div>

    <!-- Category Statistics Tab -->
    <div v-if="activeTab === 'stats'" class="tab-content">
      <div class="section-header">
        <h3>📊 分类视频统计</h3>
        <button class="btn btn-secondary btn-sm" @click="loadCategoryStats">
          🔄 刷新
        </button>
      </div>
      
      <div v-if="loadingStats" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
      
      <div v-else class="stats-grid">
        <div 
          v-for="cat in categoryStats" 
          :key="cat.video_category"
          class="stat-card"
        >
          <div class="stat-info">
            <span class="stat-category">{{ cat.video_category || '未分类' }}</span>
            <span class="stat-count">{{ cat.video_count }} 个视频</span>
          </div>
          <button 
            class="btn btn-primary btn-sm"
            @click="viewCategoryVideos(cat.video_category)"
          >
            查看
          </button>
        </div>
        
        <div v-if="categoryStats.length === 0" class="empty-state">
          <p>暂无分类数据</p>
        </div>
      </div>
    </div>

    <!-- Duplicate Detection Tab -->
    <div v-if="activeTab === 'duplicates'" class="tab-content">
      <div class="section-header">
        <h3>🔍 重复视频检测</h3>
        <div class="header-actions">
          <select v-model="duplicateType" class="select-input">
            <option value="title">按标题查重</option>
            <option value="image">按图片查重</option>
          </select>
          <button class="btn btn-primary btn-sm" @click="checkDuplicates">
            开始检测
          </button>
        </div>
      </div>
      
      <div v-if="loadingDuplicates" class="loading-state">
        <div class="loading-spinner"></div>
        <p>检测中...</p>
      </div>
      
      <div v-else-if="duplicateGroups.length > 0" class="duplicates-list">
        <div 
          v-for="(group, index) in duplicateGroups" 
          :key="index"
          class="duplicate-group"
        >
          <div class="group-header">
            <span class="group-title">
              {{ group.duplicate_type === 'title' ? '标题' : '图片' }}: 
              {{ truncateText(group.duplicate_value, 50) }}
            </span>
            <span class="group-count">{{ group.count }} 个重复</span>
          </div>
          <div class="group-videos">
            <div 
              v-for="video in group.videos" 
              :key="video.video_id"
              class="video-item"
            >
              <img 
                v-if="video.video_image" 
                :src="formatImageUrl(video.video_image)" 
                :alt="video.video_title"
                class="video-thumb"
                @error="handleImageError"
              />
              <div class="video-info">
                <span class="video-title">{{ video.video_title }}</span>
                <span class="video-meta">ID: {{ video.video_id }} | {{ video.video_category }}</span>
              </div>
              <button 
                class="btn btn-danger btn-sm"
                @click="confirmDeleteVideo(video)"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else class="empty-state">
        <p>{{ duplicateCheckDone ? '未发现重复视频' : '点击"开始检测"查找重复视频' }}</p>
      </div>
    </div>

    <!-- Video Management Tab -->
    <div v-if="activeTab === 'manage'" class="tab-content">
      <div class="section-header">
        <h3>🎬 视频管理</h3>
        <button class="btn btn-primary" @click="showAddVideoModal = true">
          ➕ 添加视频
        </button>
      </div>
      
      <div class="search-bar">
        <input 
          v-model="videoSearchKeyword" 
          type="text" 
          placeholder="搜索视频标题..."
          class="search-input"
          @keyup.enter="searchVideos"
        />
        <button class="btn btn-primary" @click="searchVideos">搜索</button>
      </div>
      
      <div v-if="loadingVideos" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
      
      <div v-else class="videos-list">
        <div 
          v-for="video in managedVideos" 
          :key="video.video_id"
          class="video-item"
        >
          <img 
            v-if="video.video_image" 
            :src="formatImageUrl(video.video_image)" 
            :alt="video.video_title"
            class="video-thumb"
            @error="handleImageError"
          />
          <div class="video-info">
            <span class="video-title">{{ video.video_title }}</span>
            <span class="video-meta">
              ID: {{ video.video_id }} | {{ video.video_category }} | 播放: {{ video.play_count || 0 }}
            </span>
          </div>
          <button 
            class="btn btn-danger btn-sm"
            @click="confirmDeleteVideo(video)"
          >
            删除
          </button>
        </div>
        
        <div v-if="managedVideos.length === 0" class="empty-state">
          <p>暂无视频数据</p>
        </div>
      </div>
    </div>

    <!-- Collection Status Tab -->
    <div v-if="activeTab === 'collection'" class="tab-content">
      <div class="section-header">
        <h3>📥 采集管理</h3>
        <div class="header-actions">
          <select v-model="collectionHours" class="select-input">
            <option value="24">24小时内</option>
            <option value="48">48小时内</option>
            <option value="72">72小时内</option>
            <option value="168">7天内</option>
          </select>
          <button class="btn btn-secondary btn-sm" @click="checkNewVideos">
            检查新视频
          </button>
        </div>
      </div>
      
      <!-- Collection Controls -->
      <div class="collection-controls">
        <h4>🚀 后台采集</h4>
        <div class="control-row">
          <div class="control-group">
            <label>采集分类</label>
            <select v-model="collectTypeId" class="select-input">
              <option value="">全部分类</option>
              <option v-for="cat in sourceCategories" :key="cat.type_id" :value="cat.type_id">
                {{ cat.type_name }}
              </option>
            </select>
          </div>
          <div class="control-group">
            <label>时间范围</label>
            <select v-model="collectHours" class="select-input">
              <option value="24">24小时内</option>
              <option value="48">48小时内</option>
              <option value="72">72小时内</option>
              <option value="168">7天内</option>
            </select>
          </div>
          <div class="control-group">
            <label>采集页数</label>
            <select v-model="collectMaxPages" class="select-input">
              <option value="1">1页</option>
              <option value="3">3页</option>
              <option value="5">5页</option>
              <option value="10">10页</option>
              <option value="20">20页</option>
            </select>
          </div>
          <div class="control-group checkbox-group">
            <label>
              <input type="checkbox" v-model="collectSkipDuplicates" />
              跳过已有视频
            </label>
          </div>
          <button 
            class="btn btn-primary" 
            @click="startCollection"
            :disabled="collectingVideos"
          >
            {{ collectingVideos ? '采集中...' : '开始采集' }}
          </button>
        </div>
        
        <div v-if="collectionResult" class="collection-result">
          <h5>采集结果</h5>
          <div class="result-summary">
            <span class="highlight">成功采集: {{ collectionResult.collected_count }} 个</span>
            <span>跳过无效: {{ collectionResult.skipped_count }} 个</span>
            <span>已存在: {{ collectionResult.duplicate_count }} 个</span>
            <span>处理页数: {{ collectionResult.pages_processed }} 页</span>
          </div>
        </div>
      </div>
      
      <div v-if="loadingCollection" class="loading-state">
        <div class="loading-spinner"></div>
        <p>检查中...</p>
      </div>
      
      <div v-else-if="collectionStatus" class="collection-info">
        <div class="status-cards">
          <div class="status-card">
            <span class="status-label">数据库总视频</span>
            <span class="status-value">{{ collectionStatus.total_videos || 0 }}</span>
          </div>
          <div class="status-card">
            <span class="status-label">总分类数</span>
            <span class="status-value">{{ collectionStatus.total_categories || 0 }}</span>
          </div>
          <div class="status-card">
            <span class="status-label">最新采集时间</span>
            <span class="status-value small">{{ collectionStatus.latest_collection_time || '无' }}</span>
          </div>
        </div>
        
        <div v-if="newVideosResult" class="new-videos-section">
          <h4>新视频检查结果</h4>
          <div class="result-summary">
            <span>源站可用: {{ newVideosResult.total_available }} 个</span>
            <span>本次检查: {{ newVideosResult.checked_count }} 个</span>
            <span class="highlight">新视频: {{ newVideosResult.new_count }} 个</span>
            <span>已采集: {{ newVideosResult.already_collected_count }} 个</span>
          </div>
          
          <div v-if="newVideosResult.new_videos && newVideosResult.new_videos.length > 0" class="new-videos-list">
            <h5>待采集视频预览 (前20个)</h5>
            <div 
              v-for="video in newVideosResult.new_videos" 
              :key="video.vod_id"
              class="video-item compact"
            >
              <img 
                v-if="video.vod_pic" 
                :src="formatImageUrl(video.vod_pic)" 
                :alt="video.vod_name"
                class="video-thumb small"
                @error="handleImageError"
              />
              <div class="video-info">
                <span class="video-title">{{ video.vod_name }}</span>
                <span class="video-meta">{{ video.type_name }} | {{ video.vod_time }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else class="empty-state">
        <p>点击"检查新视频"获取采集状态</p>
      </div>
    </div>

    <!-- Category Videos Modal -->
    <div v-if="showCategoryModal" class="modal-overlay" @click.self="closeCategoryModal">
      <div class="modal modal-large">
        <div class="modal-header">
          <h3>{{ viewingCategory || '未分类' }} - 视频列表</h3>
          <button class="close-btn" @click="closeCategoryModal">×</button>
        </div>
        <div class="modal-body">
          <div v-if="loadingCategoryVideos" class="loading-state">
            <div class="loading-spinner"></div>
            <p>加载中...</p>
          </div>
          <div v-else class="videos-grid">
            <div 
              v-for="video in categoryVideos" 
              :key="video.video_id"
              class="video-card"
            >
              <img 
                v-if="video.video_image" 
                :src="formatImageUrl(video.video_image)" 
                :alt="video.video_title"
                class="video-thumb"
                @error="handleImageError"
              />
              <div class="video-info">
                <span class="video-title">{{ video.video_title }}</span>
                <span class="video-meta">ID: {{ video.video_id }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeCategoryModal">关闭</button>
        </div>
      </div>
    </div>

    <!-- Add Video Modal -->
    <div v-if="showAddVideoModal" class="modal-overlay" @click.self="showAddVideoModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>添加视频</h3>
          <button class="close-btn" @click="showAddVideoModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>视频标题 *</label>
            <input v-model="newVideo.video_title" type="text" class="form-input" placeholder="输入视频标题" />
          </div>
          <div class="form-group">
            <label>视频URL *</label>
            <input v-model="newVideo.video_url" type="text" class="form-input" placeholder="输入视频播放地址" />
          </div>
          <div class="form-group">
            <label>封面图片URL</label>
            <input v-model="newVideo.video_image" type="text" class="form-input" placeholder="输入封面图片地址" />
          </div>
          <div class="form-group">
            <label>分类</label>
            <input v-model="newVideo.video_category" type="text" class="form-input" placeholder="输入视频分类" />
          </div>
          <div class="form-group">
            <label>时长</label>
            <input v-model="newVideo.video_duration" type="text" class="form-input" placeholder="例如: 01:30:00" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showAddVideoModal = false">取消</button>
          <button class="btn btn-primary" @click="addVideo">添加</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal modal-small">
        <div class="modal-header">
          <h3>确认删除</h3>
          <button class="close-btn" @click="showDeleteModal = false">×</button>
        </div>
        <div class="modal-body">
          <p>确定要删除视频"{{ deletingVideo?.video_title }}"吗？</p>
          <p class="warning-text">此操作不可恢复！</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showDeleteModal = false">取消</button>
          <button class="btn btn-danger" @click="deleteVideo">确认删除</button>
        </div>
      </div>
    </div>

    <!-- Toast Notification -->
    <transition name="toast">
      <div v-if="toastMessage" class="toast-message" :class="toastType">
        {{ toastMessage }}
      </div>
    </transition>
  </div>
</template>

<script>
import { videoApi } from '@/api'
import { extractArrayData } from '@/utils/apiUtils'
import { formatImageUrl } from '@/utils/imageUtils'

export default {
  name: 'VideoManagement',
  data() {
    return {
      activeTab: 'stats',
      tabs: [
        { key: 'stats', label: '分类统计', icon: '📊' },
        { key: 'duplicates', label: '重复检测', icon: '🔍' },
        { key: 'manage', label: '视频管理', icon: '🎬' },
        { key: 'collection', label: '采集状态', icon: '📥' }
      ],
      
      // Category Stats
      categoryStats: [],
      loadingStats: false,
      
      // Category Videos Modal
      showCategoryModal: false,
      viewingCategory: '',
      categoryVideos: [],
      loadingCategoryVideos: false,
      
      // Duplicate Detection
      duplicateType: 'title',
      duplicateGroups: [],
      loadingDuplicates: false,
      duplicateCheckDone: false,
      
      // Video Management
      managedVideos: [],
      loadingVideos: false,
      videoSearchKeyword: '',
      showAddVideoModal: false,
      newVideo: {
        video_title: '',
        video_url: '',
        video_image: '',
        video_category: '',
        video_duration: ''
      },
      
      // Delete confirmation
      showDeleteModal: false,
      deletingVideo: null,
      
      // Collection Status
      collectionHours: 24,
      collectionStatus: null,
      newVideosResult: null,
      loadingCollection: false,
      
      // Background Collection
      sourceCategories: [],
      collectTypeId: '',
      collectHours: 24,
      collectMaxPages: 1,
      collectSkipDuplicates: true,
      collectingVideos: false,
      collectionResult: null,
      
      // Toast
      toastMessage: '',
      toastType: ''
    }
  },
  mounted() {
    this.loadCategoryStats()
    this.loadSourceCategories()
  },
  methods: {
    // Category Statistics
    async loadCategoryStats() {
      this.loadingStats = true
      try {
        const result = await videoApi.getCategoryStats()
        this.categoryStats = extractArrayData(result)
      } catch (e) {
        console.error('Load category stats error:', e)
        this.showToast('加载分类统计失败', 'error')
      } finally {
        this.loadingStats = false
      }
    },
    
    async viewCategoryVideos(category) {
      this.viewingCategory = category
      this.showCategoryModal = true
      this.loadingCategoryVideos = true
      
      try {
        const result = await videoApi.getCategoryVideosAdmin(category, 50)
        this.categoryVideos = extractArrayData(result)
      } catch (e) {
        console.error('Load category videos error:', e)
        this.showToast('加载视频列表失败', 'error')
      } finally {
        this.loadingCategoryVideos = false
      }
    },
    
    closeCategoryModal() {
      this.showCategoryModal = false
      this.viewingCategory = ''
      this.categoryVideos = []
    },
    
    // Duplicate Detection
    async checkDuplicates() {
      this.loadingDuplicates = true
      this.duplicateCheckDone = false
      
      try {
        const result = await videoApi.getDuplicateVideos(this.duplicateType)
        this.duplicateGroups = extractArrayData(result)
        this.duplicateCheckDone = true
        
        if (this.duplicateGroups.length === 0) {
          this.showToast('未发现重复视频', 'success')
        } else {
          this.showToast(`发现 ${this.duplicateGroups.length} 组重复视频`, 'info')
        }
      } catch (e) {
        console.error('Check duplicates error:', e)
        this.showToast('检测重复视频失败', 'error')
      } finally {
        this.loadingDuplicates = false
      }
    },
    
    // Video Management
    async searchVideos() {
      this.loadingVideos = true
      
      try {
        let result
        if (this.videoSearchKeyword) {
          result = await videoApi.searchVideos(this.videoSearchKeyword, 50)
        } else {
          result = await videoApi.getVideos({ limit: 50 })
        }
        this.managedVideos = extractArrayData(result)
      } catch (e) {
        console.error('Search videos error:', e)
        this.showToast('搜索视频失败', 'error')
      } finally {
        this.loadingVideos = false
      }
    },
    
    async addVideo() {
      if (!this.newVideo.video_title || !this.newVideo.video_url) {
        this.showToast('请填写必填字段', 'error')
        return
      }
      
      try {
        await videoApi.addVideo(this.newVideo)
        this.showToast('视频添加成功', 'success')
        this.showAddVideoModal = false
        this.newVideo = {
          video_title: '',
          video_url: '',
          video_image: '',
          video_category: '',
          video_duration: ''
        }
        // Refresh stats and video list
        this.loadCategoryStats()
        if (this.activeTab === 'manage') {
          this.searchVideos()
        }
      } catch (e) {
        console.error('Add video error:', e)
        this.showToast('添加视频失败', 'error')
      }
    },
    
    confirmDeleteVideo(video) {
      this.deletingVideo = video
      this.showDeleteModal = true
    },
    
    async deleteVideo() {
      if (!this.deletingVideo) return
      
      try {
        await videoApi.deleteVideo(this.deletingVideo.video_id)
        this.showToast('视频删除成功', 'success')
        this.showDeleteModal = false
        this.deletingVideo = null
        
        // Refresh data
        this.loadCategoryStats()
        if (this.activeTab === 'duplicates') {
          this.checkDuplicates()
        }
        if (this.activeTab === 'manage') {
          this.searchVideos()
        }
      } catch (e) {
        console.error('Delete video error:', e)
        this.showToast('删除视频失败', 'error')
      }
    },
    
    // Collection Status
    async checkNewVideos() {
      this.loadingCollection = true
      
      try {
        // First get local collection status
        const statusResult = await videoApi.getCollectionStatus(this.collectionHours)
        this.collectionStatus = statusResult?.data || statusResult
        
        // Then check for new videos from source
        const newResult = await videoApi.checkNewVideos(this.collectionHours)
        this.newVideosResult = newResult?.data || newResult
        
        if (this.newVideosResult.new_count > 0) {
          this.showToast(`发现 ${this.newVideosResult.new_count} 个新视频可采集`, 'success')
        } else {
          this.showToast('暂无新视频', 'info')
        }
      } catch (e) {
        console.error('Check new videos error:', e)
        this.showToast('检查新视频失败', 'error')
      } finally {
        this.loadingCollection = false
      }
    },
    
    // Load source categories from collector API
    async loadSourceCategories() {
      try {
        const result = await videoApi.getSourceCategories()
        this.sourceCategories = extractArrayData(result)
      } catch (e) {
        console.error('Load source categories error:', e)
        // Silently fail - categories are optional for collection
      }
    },
    
    // Start background collection
    async startCollection() {
      if (this.collectingVideos) return
      
      this.collectingVideos = true
      this.collectionResult = null
      
      try {
        const result = await videoApi.collectVideos({
          type_id: this.collectTypeId || null,
          hours: parseInt(this.collectHours),
          max_pages: parseInt(this.collectMaxPages),
          skip_duplicates: this.collectSkipDuplicates
        })
        
        this.collectionResult = result?.data || result
        
        if (this.collectionResult.collected_count > 0) {
          this.showToast(`成功采集 ${this.collectionResult.collected_count} 个视频`, 'success')
          // Refresh stats after collection
          this.loadCategoryStats()
          this.checkNewVideos()
        } else {
          this.showToast('没有新视频可采集', 'info')
        }
      } catch (e) {
        console.error('Collection error:', e)
        this.showToast('采集失败: ' + (e.userMessage || e.message), 'error')
      } finally {
        this.collectingVideos = false
      }
    },
    
    // Utility methods
    truncateText(text, maxLength) {
      if (!text) return ''
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
    },
    
    // Format image URL to handle base64 and special URL formats
    formatImageUrl(url) {
      return formatImageUrl(url)
    },
    
    handleImageError(e) {
      // Use a transparent 1x1 pixel data URI instead of empty string to avoid browser loading current page
      e.target.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
      e.target.style.background = 'linear-gradient(135deg, #2a2a4a 0%, #1a1a3e 100%)'
    },
    
    showToast(message, type = 'info') {
      this.toastMessage = message
      this.toastType = type
      setTimeout(() => {
        this.toastMessage = ''
        this.toastType = ''
      }, 2500)
    }
  }
}
</script>

<style scoped>
.video-management-page {
  max-width: 1200px;
}

/* Tab Navigation */
.tab-nav {
  display: flex;
  gap: 10px;
  margin-bottom: 25px;
  flex-wrap: wrap;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #a0a0b0;
  font-size: 0.95em;
  cursor: pointer;
  transition: all 0.3s;
}

.tab-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.tab-btn.active {
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.2) 0%, rgba(0, 212, 255, 0.2) 100%);
  border-color: rgba(124, 58, 237, 0.5);
  color: #00d4ff;
}

.tab-icon {
  font-size: 1.2em;
}

/* Tab Content */
.tab-content {
  background: linear-gradient(135deg, #1a1a2e 0%, #16162a 100%);
  border-radius: 12px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Section Header */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  font-size: 1.2em;
  color: #fff;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 0.95em;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.85em;
}

.btn-primary {
  background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
  color: #fff;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #8b47f5 0%, #7c3aed 100%);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #a0a0b0;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

.btn-danger {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: #fff;
}

.btn-danger:hover {
  background: linear-gradient(135deg, #f87171 0%, #ef4444 100%);
}

/* Form inputs */
.select-input,
.search-input,
.form-input {
  padding: 10px 15px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #fff;
  font-size: 0.9em;
}

/* Fix dropdown options styling - ensure text is visible in browser's native dropdown */
.select-input option {
  background-color: #1a1a2e;
  color: #fff;
}

.select-input:focus,
.search-input:focus,
.form-input:focus {
  outline: none;
  border-color: #7c3aed;
}

.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
  max-width: 400px;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
}

.loading-state p {
  margin-top: 15px;
  color: #888;
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
  to { transform: rotate(360deg); }
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #888;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 15px;
}

.stat-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  transition: all 0.3s;
}

.stat-card:hover {
  border-color: rgba(124, 58, 237, 0.3);
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-category {
  font-weight: 600;
  color: #fff;
}

.stat-count {
  font-size: 0.85em;
  color: #00d4ff;
}

/* Duplicates List */
.duplicates-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.duplicate-group {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  overflow: hidden;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background: rgba(239, 68, 68, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.group-title {
  font-weight: 500;
  color: #fff;
  font-size: 0.9em;
}

.group-count {
  font-size: 0.85em;
  color: #ef4444;
  font-weight: 600;
}

.group-videos {
  padding: 10px;
}

/* Video Items */
.videos-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.video-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px 15px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.video-item.compact {
  padding: 8px 12px;
}

.video-thumb {
  width: 80px;
  height: 45px;
  object-fit: cover;
  border-radius: 4px;
  background: linear-gradient(135deg, #2a2a4a 0%, #1a1a3e 100%);
}

.video-thumb.small {
  width: 60px;
  height: 34px;
}

.video-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.video-title {
  font-weight: 500;
  color: #fff;
  font-size: 0.9em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.video-meta {
  font-size: 0.8em;
  color: #888;
}

/* Videos Grid */
.videos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.video-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  overflow: hidden;
}

.video-card .video-thumb {
  width: 100%;
  height: 120px;
  object-fit: cover;
  background: linear-gradient(135deg, #2a2a4a 0%, #1a1a3e 100%);
}

.video-card .video-info {
  padding: 10px;
}

/* Collection Status */
.collection-info {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

/* Collection Controls */
.collection-controls {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 25px;
}

.collection-controls h4 {
  margin: 0 0 15px 0;
  color: #fff;
  font-size: 1.1em;
}

.control-row {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: flex-end;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.control-group label {
  font-size: 0.85em;
  color: #a0a0b0;
}

.control-group.checkbox-group {
  flex-direction: row;
  align-items: center;
}

.control-group.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #fff;
  cursor: pointer;
}

.control-group.checkbox-group input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: #7c3aed;
}

.collection-result {
  margin-top: 20px;
  padding: 15px;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 8px;
}

.collection-result h5 {
  margin: 0 0 10px 0;
  color: #22c55e;
  font-size: 0.95em;
}

.status-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 15px;
}

.status-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  text-align: center;
}

.status-label {
  font-size: 0.85em;
  color: #a0a0b0;
}

.status-value {
  font-size: 1.8em;
  font-weight: 700;
  color: #00d4ff;
}

.status-value.small {
  font-size: 0.9em;
}

.new-videos-section h4 {
  margin: 0 0 15px 0;
  color: #fff;
  font-size: 1.1em;
}

.new-videos-section h5 {
  margin: 15px 0 10px 0;
  color: #a0a0b0;
  font-size: 0.95em;
}

.result-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  font-size: 0.9em;
  color: #a0a0b0;
}

.result-summary .highlight {
  color: #22c55e;
  font-weight: 600;
}

.new-videos-list {
  margin-top: 15px;
  max-height: 400px;
  overflow-y: auto;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal {
  background: #1a1a2e;
  border-radius: 12px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-large {
  max-width: 800px;
}

.modal-small {
  max-width: 400px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: rgba(0, 0, 0, 0.3);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.1em;
  color: #fff;
}

.close-btn {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: #888;
  font-size: 1.5em;
  cursor: pointer;
}

.close-btn:hover {
  color: #fff;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 15px 20px;
  background: rgba(0, 0, 0, 0.2);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* Form */
.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #fff;
  font-size: 0.9em;
}

.form-input {
  width: 100%;
}

.warning-text {
  color: #ef4444;
  font-size: 0.9em;
}

/* Toast */
.toast-message {
  position: fixed;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.9);
  color: #fff;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 0.9em;
  z-index: 2000;
}

.toast-message.success {
  background: rgba(34, 197, 94, 0.95);
}

.toast-message.error {
  background: rgba(239, 68, 68, 0.95);
}

.toast-message.info {
  background: rgba(59, 130, 246, 0.95);
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}

/* Mobile responsive */
@media (max-width: 768px) {
  .tab-nav {
    gap: 8px;
  }
  
  .tab-btn {
    padding: 10px 15px;
    font-size: 0.85em;
  }
  
  .tab-content {
    padding: 15px;
  }
  
  .section-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .video-item {
    flex-wrap: wrap;
  }
  
  .video-thumb {
    width: 60px;
    height: 34px;
  }
}
</style>
