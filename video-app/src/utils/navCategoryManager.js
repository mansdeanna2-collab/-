/**
 * Navigation Category Manager
 * 导航分类管理工具
 * 
 * Manages the configuration of top navigation categories and their bound video subcategories.
 * Data is persisted in localStorage.
 */

// LocalStorage key for navigation categories
const STORAGE_KEY = 'admin_nav_categories'

// Default navigation categories configuration
// This matches the initial structure from HomeView.vue
const DEFAULT_NAV_CATEGORIES = [
  {
    key: 'recommend',
    label: '推荐',
    subcategories: ['热门推荐', '动作电影', '喜剧片', '科幻大片', '爱情电影', '恐怖惊悚', '纪录片', '动漫']
  },
  {
    key: 'japan',
    label: '日本',
    subcategories: ['日本AV', '无码高清', '制服诱惑', '人妻系列', '女优精选', '素人企划', '动漫资源', '经典作品']
  },
  {
    key: 'domestic',
    label: '国产',
    subcategories: ['国产自拍', '网红主播', '偷拍私拍', '情侣实录', '素人投稿', '制服诱惑', '熟女人妻', '精品短视频']
  },
  {
    key: 'anime',
    label: '动漫',
    subcategories: ['里番动漫', '3D动画', '同人作品', '触手系列', 'NTR剧情', '巨乳萝莉', '校园爱情', '经典番剧']
  },
  {
    key: 'welfare',
    label: '福利',
    subcategories: ['写真福利', '丝袜美腿', '性感模特', '大尺度写真', '韩国女团', '日本偶像', '网红热舞', 'ASMR']
  }
]

/**
 * Get all navigation categories from localStorage
 * @returns {Array} Navigation categories array
 */
export function getNavCategories() {
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY)
    if (stored) {
      const parsed = JSON.parse(stored)
      if (Array.isArray(parsed) && parsed.length > 0) {
        return parsed
      }
    }
  } catch (e) {
    console.error('Error loading nav categories:', e)
  }
  // Return default if nothing stored
  return [...DEFAULT_NAV_CATEGORIES]
}

/**
 * Save navigation categories to localStorage
 * @param {Array} categories - Navigation categories to save
 */
export function saveNavCategories(categories) {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(categories))
    return true
  } catch (e) {
    console.error('Error saving nav categories:', e)
    return false
  }
}

/**
 * Add a new navigation category
 * @param {Object} category - Category to add { key, label, subcategories }
 * @returns {boolean} Success status
 */
export function addNavCategory(category) {
  const categories = getNavCategories()
  
  // Check if key already exists
  if (categories.some(c => c.key === category.key)) {
    console.error('Category key already exists:', category.key)
    return false
  }
  
  categories.push({
    key: category.key,
    label: category.label,
    subcategories: category.subcategories || []
  })
  
  return saveNavCategories(categories)
}

/**
 * Update an existing navigation category
 * @param {string} key - Category key to update
 * @param {Object} updates - Updates to apply { label?, subcategories? }
 * @returns {boolean} Success status
 */
export function updateNavCategory(key, updates) {
  const categories = getNavCategories()
  const index = categories.findIndex(c => c.key === key)
  
  if (index === -1) {
    console.error('Category not found:', key)
    return false
  }
  
  categories[index] = {
    ...categories[index],
    ...updates
  }
  
  return saveNavCategories(categories)
}

/**
 * Delete a navigation category
 * @param {string} key - Category key to delete
 * @returns {boolean} Success status
 */
export function deleteNavCategory(key) {
  const categories = getNavCategories()
  const index = categories.findIndex(c => c.key === key)
  
  if (index === -1) {
    console.error('Category not found:', key)
    return false
  }
  
  categories.splice(index, 1)
  return saveNavCategories(categories)
}

/**
 * Get a single navigation category by key
 * @param {string} key - Category key
 * @returns {Object|null} Category object or null if not found
 */
export function getNavCategoryByKey(key) {
  const categories = getNavCategories()
  return categories.find(c => c.key === key) || null
}

/**
 * Update subcategories for a navigation category
 * @param {string} key - Category key
 * @param {Array} subcategories - New subcategories array
 * @returns {boolean} Success status
 */
export function updateSubcategories(key, subcategories) {
  return updateNavCategory(key, { subcategories })
}

/**
 * Reset navigation categories to default
 * @returns {boolean} Success status
 */
export function resetToDefault() {
  return saveNavCategories([...DEFAULT_NAV_CATEGORIES])
}

/**
 * Get the subcategory mapping object (for HomeView compatibility)
 * @returns {Object} Mapping of category key to subcategories array
 */
export function getSubcategoryMapping() {
  const categories = getNavCategories()
  const mapping = {}
  categories.forEach(cat => {
    mapping[cat.key] = cat.subcategories
  })
  return mapping
}

/**
 * Get main categories array (for HomeView compatibility)
 * @returns {Array} Array of { key, label } objects
 */
export function getMainCategories() {
  return getNavCategories().map(cat => ({
    key: cat.key,
    label: cat.label
  }))
}

export default {
  getNavCategories,
  saveNavCategories,
  addNavCategory,
  updateNavCategory,
  deleteNavCategory,
  getNavCategoryByKey,
  updateSubcategories,
  resetToDefault,
  getSubcategoryMapping,
  getMainCategories
}
