<template>
  <div class="nav-categories-page">
    <!-- Action Bar -->
    <div class="action-bar">
      <button class="btn btn-primary" @click="showAddModal = true">
        <span class="btn-icon">➕</span>
        添加导航分类
      </button>
      <button class="btn btn-secondary" @click="resetCategories">
        <span class="btn-icon">🔄</span>
        恢复默认
      </button>
    </div>
    
    <!-- Categories List (show even when loading API categories) -->
    <div class="categories-list">
      <div 
        v-for="(navCat, index) in navCategories"
        :key="navCat.key"
        class="category-card"
      >
        <div class="card-header">
          <div class="card-title-section">
            <span class="category-index">{{ index + 1 }}</span>
            <div class="title-content">
              <h3 class="category-label">{{ navCat.label }}</h3>
              <span class="category-key">key: {{ navCat.key }}</span>
            </div>
          </div>
          <div class="card-actions">
            <button class="action-btn edit-btn" @click="editCategory(navCat)" title="编辑">
              ✏️
            </button>
            <button class="action-btn delete-btn" @click="confirmDelete(navCat)" title="删除">
              🗑️
            </button>
          </div>
        </div>
        
        <div class="card-body">
          <div class="subcategories-section">
            <div class="section-header">
              <span class="section-label">绑定的视频分类 ({{ navCat.subcategories.length }})</span>
              <button class="btn-small" @click="editSubcategories(navCat)">
                编辑绑定
              </button>
            </div>
            <div class="subcategory-list" v-if="navCat.subcategories.length > 0">
              <span 
                v-for="sub in navCat.subcategories"
                :key="sub"
                class="subcategory-tag"
              >
                {{ sub }}
                <span 
                  class="remove-tag"
                  @click.stop="removeSubcategory(navCat.key, sub)"
                >×</span>
              </span>
            </div>
            <div v-else class="empty-subcategories">
              暂无绑定分类，点击"编辑绑定"添加
            </div>
          </div>
        </div>
      </div>
      
      <!-- Empty State -->
      <div v-if="navCategories.length === 0" class="empty-state">
        <div class="empty-icon">📁</div>
        <p>暂无导航分类</p>
        <button class="btn btn-primary" @click="showAddModal = true">
          添加第一个分类
        </button>
      </div>
    </div>
    
    <!-- Add/Edit Category Modal -->
    <div v-if="showAddModal || showEditModal" class="modal-overlay" @click.self="closeModals">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ showEditModal ? '编辑导航分类' : '添加导航分类' }}</h3>
          <button class="close-btn" @click="closeModals">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>分类名称</label>
            <input 
              v-model="formData.label"
              type="text"
              placeholder="例如：推荐"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>分类标识 (key)</label>
            <input 
              v-model="formData.key"
              type="text"
              placeholder="例如：recommend"
              class="form-input"
              :disabled="showEditModal"
            />
            <span class="form-hint">用于系统识别，创建后不可修改</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeModals">取消</button>
          <button class="btn btn-primary" @click="saveCategory">保存</button>
        </div>
      </div>
    </div>
    
    <!-- Subcategories Binding Modal -->
    <div v-if="showSubcategoriesModal" class="modal-overlay" @click.self="closeSubcategoriesModal">
      <div class="modal modal-large">
        <div class="modal-header">
          <h3>编辑绑定分类 - {{ editingNav?.label }}</h3>
          <button class="close-btn" @click="closeSubcategoriesModal">×</button>
        </div>
        <div class="modal-body">
          <p class="modal-desc">
            选择要绑定到"{{ editingNav?.label }}"的视频分类。选中的分类将在前台导航中显示相应的视频内容。
          </p>
          
          <!-- Selected Subcategories -->
          <div class="selected-section">
            <h4>已选择的分类 ({{ selectedSubcategories.length }})</h4>
            <div class="selected-tags" v-if="selectedSubcategories.length > 0">
              <span 
                v-for="sub in selectedSubcategories"
                :key="sub"
                class="selected-tag"
              >
                {{ sub }}
                <span class="remove-tag" @click="toggleSubcategory(sub)">×</span>
              </span>
            </div>
            <p v-else class="empty-selected">尚未选择任何分类</p>
          </div>
          
          <!-- Available Subcategories -->
          <div class="available-section">
            <h4>可选视频分类</h4>
            <div v-if="loadingCategories" class="loading-small">
              <div class="loading-spinner small"></div>
              <span>加载中...</span>
            </div>
            <div v-else class="available-grid">
              <button 
                v-for="cat in availableCategories"
                :key="cat.name"
                :class="['category-btn', { selected: selectedSubcategories.includes(cat.name) }]"
                @click="toggleSubcategory(cat.name)"
              >
                <span class="cat-name">{{ cat.name }}</span>
                <span class="cat-count">({{ cat.count }})</span>
              </button>
            </div>
            <p v-if="availableCategories.length === 0 && !loadingCategories" class="empty-categories">
              无法获取视频分类，请检查API连接
            </p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeSubcategoriesModal">取消</button>
          <button class="btn btn-primary" @click="saveSubcategories">保存绑定</button>
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
          <p>确定要删除导航分类"{{ deletingNav?.label }}"吗？</p>
          <p class="warning-text">此操作不可恢复！</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showDeleteModal = false">取消</button>
          <button class="btn btn-danger" @click="doDelete">确认删除</button>
        </div>
      </div>
    </div>
    
    <!-- Reset Confirmation Modal -->
    <div v-if="showResetModal" class="modal-overlay" @click.self="showResetModal = false">
      <div class="modal modal-small">
        <div class="modal-header">
          <h3>确认恢复默认</h3>
          <button class="close-btn" @click="showResetModal = false">×</button>
        </div>
        <div class="modal-body">
          <p>确定要恢复默认导航分类配置吗？</p>
          <p class="warning-text">当前配置将会丢失！</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showResetModal = false">取消</button>
          <button class="btn btn-danger" @click="doReset">确认恢复</button>
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
import {
  getNavCategories,
  fetchNavCategories,
  addNavCategory,
  updateNavCategory,
  deleteNavCategory,
  updateSubcategories,
  resetToDefault
} from '@/utils/navCategoryManager'

export default {
  name: 'NavCategoriesManager',
  data() {
    return {
      navCategories: [],
      availableCategories: [],
      loadingCategories: false,
      savingData: false,
      
      // Modals
      showAddModal: false,
      showEditModal: false,
      showSubcategoriesModal: false,
      showDeleteModal: false,
      showResetModal: false,
      
      // Form data
      formData: {
        key: '',
        label: ''
      },
      
      // Editing states
      editingNav: null,
      deletingNav: null,
      selectedSubcategories: [],
      
      // Toast notification
      toastMessage: '',
      toastType: ''
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    async loadData() {
      // Load nav categories from API (global settings from database)
      try {
        this.navCategories = await fetchNavCategories()
      } catch (e) {
        console.error('Error loading nav categories:', e)
        // Fallback to cached/default
        this.navCategories = getNavCategories()
      }
      
      // Load available categories from API
      await this.loadAvailableCategories()
    },
    
    async loadAvailableCategories() {
      this.loadingCategories = true
      try {
        const result = await videoApi.getCategories()
        const categories = extractArrayData(result)
        this.availableCategories = categories.map(cat => ({
          name: cat.category || cat.video_category || cat.name || cat,
          count: cat.count || cat.video_count || 0
        }))
      } catch (e) {
        console.error('Load categories error:', e)
        this.availableCategories = []
      } finally {
        this.loadingCategories = false
      }
    },
    
    // Add/Edit Category
    editCategory(navCat) {
      this.formData = {
        key: navCat.key,
        label: navCat.label
      }
      this.showEditModal = true
    },
    
    async saveCategory() {
      if (!this.formData.key || !this.formData.label) {
        this.showToast('请填写完整信息', 'error')
        return
      }
      
      this.savingData = true
      try {
        if (this.showEditModal) {
          // Update existing
          const success = await updateNavCategory(this.formData.key, {
            label: this.formData.label
          })
          if (success) {
            this.showToast('分类已更新（已保存到数据库）', 'success')
          } else {
            this.showToast('保存失败', 'error')
            return
          }
        } else {
          // Add new
          const success = await addNavCategory({
            key: this.formData.key,
            label: this.formData.label,
            subcategories: []
          })
          if (!success) {
            this.showToast('分类标识已存在或保存失败', 'error')
            return
          }
          this.showToast('分类已添加（已保存到数据库）', 'success')
        }
        
        this.navCategories = getNavCategories()
        this.closeModals()
      } finally {
        this.savingData = false
      }
    },
    
    closeModals() {
      this.showAddModal = false
      this.showEditModal = false
      this.formData = { key: '', label: '' }
    },
    
    // Delete Category
    confirmDelete(navCat) {
      this.deletingNav = navCat
      this.showDeleteModal = true
    },
    
    async doDelete() {
      if (this.deletingNav) {
        this.savingData = true
        try {
          await deleteNavCategory(this.deletingNav.key)
          this.navCategories = getNavCategories()
          this.showToast('分类已删除（已保存到数据库）', 'success')
        } finally {
          this.savingData = false
        }
      }
      this.showDeleteModal = false
      this.deletingNav = null
    },
    
    // Subcategories Management
    editSubcategories(navCat) {
      this.editingNav = navCat
      this.selectedSubcategories = [...navCat.subcategories]
      this.showSubcategoriesModal = true
    },
    
    toggleSubcategory(name) {
      const index = this.selectedSubcategories.indexOf(name)
      if (index === -1) {
        this.selectedSubcategories.push(name)
      } else {
        this.selectedSubcategories.splice(index, 1)
      }
    },
    
    async removeSubcategory(navKey, subName) {
      const navCat = this.navCategories.find(n => n.key === navKey)
      if (navCat) {
        const newSubs = navCat.subcategories.filter(s => s !== subName)
        await updateSubcategories(navKey, newSubs)
        this.navCategories = getNavCategories()
      }
    },
    
    async saveSubcategories() {
      if (this.editingNav) {
        this.savingData = true
        try {
          await updateSubcategories(this.editingNav.key, this.selectedSubcategories)
          this.navCategories = getNavCategories()
          this.showToast('绑定已保存（已保存到数据库）', 'success')
        } finally {
          this.savingData = false
        }
      }
      this.closeSubcategoriesModal()
    },
    
    closeSubcategoriesModal() {
      this.showSubcategoriesModal = false
      this.editingNav = null
      this.selectedSubcategories = []
    },
    
    // Reset to default - show confirmation modal
    resetCategories() {
      this.showResetModal = true
    },
    
    // Perform reset after confirmation
    async doReset() {
      this.savingData = true
      try {
        await resetToDefault()
        this.navCategories = getNavCategories()
        this.showToast('已恢复默认配置（已保存到数据库）', 'success')
      } finally {
        this.savingData = false
      }
      this.showResetModal = false
    },
    
    // Toast notification
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
.nav-categories-page {
  max-width: 1000px;
}

/* Action Bar */
.action-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 25px;
}

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

.btn-primary {
  background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
  color: #fff;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #8b47f5 0%, #7c3aed 100%);
  transform: translateY(-1px);
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

.btn-icon {
  font-size: 1em;
}

.btn-small {
  padding: 5px 12px;
  background: rgba(0, 212, 255, 0.15);
  border: 1px solid rgba(0, 212, 255, 0.3);
  color: #00d4ff;
  border-radius: 5px;
  font-size: 0.8em;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-small:hover {
  background: rgba(0, 212, 255, 0.25);
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 50px 20px;
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

.loading-spinner.small {
  width: 20px;
  height: 20px;
  border-width: 2px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Categories List */
.categories-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.category-card {
  background: linear-gradient(135deg, #1a1a2e 0%, #16162a 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s;
}

.category-card:hover {
  border-color: rgba(124, 58, 237, 0.3);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.card-title-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.category-index {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #7c3aed 0%, #00d4ff 100%);
  border-radius: 50%;
  font-weight: 600;
  font-size: 0.85em;
  color: #fff;
}

.title-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.category-label {
  margin: 0;
  font-size: 1.1em;
  font-weight: 600;
  color: #fff;
}

.category-key {
  font-size: 0.8em;
  color: #888;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 1em;
}

.edit-btn {
  background: rgba(59, 130, 246, 0.15);
}

.edit-btn:hover {
  background: rgba(59, 130, 246, 0.3);
}

.delete-btn {
  background: rgba(239, 68, 68, 0.15);
}

.delete-btn:hover {
  background: rgba(239, 68, 68, 0.3);
}

.card-body {
  padding: 15px 20px;
}

.subcategories-section {
  width: 100%;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-label {
  font-size: 0.9em;
  color: #a0a0b0;
  font-weight: 500;
}

.subcategory-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.subcategory-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 15px;
  font-size: 0.85em;
  color: #00d4ff;
}

.remove-tag {
  font-size: 1.1em;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.remove-tag:hover {
  opacity: 1;
}

.empty-subcategories {
  color: #666;
  font-size: 0.9em;
  font-style: italic;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 4em;
  margin-bottom: 15px;
}

.empty-state p {
  color: #888;
  margin-bottom: 20px;
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
  max-width: 700px;
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
  transition: color 0.2s;
}

.close-btn:hover {
  color: #fff;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.modal-desc {
  color: #a0a0b0;
  margin-bottom: 20px;
  font-size: 0.9em;
  line-height: 1.5;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #fff;
}

.form-input {
  width: 100%;
  padding: 12px 15px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #fff;
  font-size: 0.95em;
  transition: all 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: #7c3aed;
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.2);
}

.form-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-input::placeholder {
  color: #666;
}

.form-hint {
  display: block;
  margin-top: 5px;
  font-size: 0.8em;
  color: #888;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 15px 20px;
  background: rgba(0, 0, 0, 0.2);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* Subcategories Modal */
.selected-section {
  margin-bottom: 25px;
}

.selected-section h4,
.available-section h4 {
  margin: 0 0 12px 0;
  font-size: 0.95em;
  color: #a0a0b0;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.selected-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.2) 0%, rgba(0, 212, 255, 0.2) 100%);
  border: 1px solid rgba(124, 58, 237, 0.4);
  border-radius: 15px;
  font-size: 0.85em;
  color: #fff;
}

.empty-selected {
  color: #666;
  font-size: 0.85em;
  font-style: italic;
}

.available-section {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 20px;
}

.loading-small {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #888;
  font-size: 0.9em;
}

.available-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 8px;
}

.category-btn {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.category-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.category-btn.selected {
  background: rgba(0, 212, 255, 0.15);
  border-color: rgba(0, 212, 255, 0.5);
}

.cat-name {
  font-size: 0.9em;
  color: #fff;
  font-weight: 500;
}

.cat-count {
  font-size: 0.75em;
  color: #888;
  margin-top: 2px;
}

.empty-categories {
  color: #888;
  font-size: 0.9em;
  text-align: center;
  padding: 20px;
}

.warning-text {
  color: #ef4444;
  font-size: 0.9em;
}

/* Toast Notification */
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
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.toast-message.success {
  background: rgba(34, 197, 94, 0.95);
  border-color: rgba(34, 197, 94, 0.5);
}

.toast-message.error {
  background: rgba(239, 68, 68, 0.95);
  border-color: rgba(239, 68, 68, 0.5);
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
@media (max-width: 576px) {
  .action-bar {
    flex-direction: column;
  }
  
  .btn {
    justify-content: center;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .card-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .modal {
    margin: 10px;
    max-height: 85vh;
  }
  
  .available-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
