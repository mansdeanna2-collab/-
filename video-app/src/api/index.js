import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// Video API endpoints
export const videoApi = {
  // Get all videos with pagination
  getVideos(params = {}) {
    return api.get('/videos', { params })
  },

  // Get video by ID
  getVideo(videoId) {
    return api.get(`/videos/${videoId}`)
  },

  // Search videos by keyword
  searchVideos(keyword, limit = 20, offset = 0) {
    return api.get('/videos/search', { params: { keyword, limit, offset } })
  },

  // Get videos by category
  getVideosByCategory(category, limit = 20, offset = 0) {
    return api.get('/videos/category', { params: { category, limit, offset } })
  },

  // Get all categories
  getCategories() {
    return api.get('/categories')
  },

  // Get top videos by play count
  getTopVideos(limit = 10) {
    return api.get('/videos/top', { params: { limit } })
  },

  // Update play count
  updatePlayCount(videoId) {
    return api.post(`/videos/${videoId}/play`)
  },

  // Get database statistics
  getStatistics() {
    return api.get('/statistics')
  }
}

export default api
