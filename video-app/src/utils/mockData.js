/**
 * Mock data for demo purposes when API is unavailable
 * 当API不可用时用于演示的模拟数据
 */

// Mock categories 模拟分类
export const mockCategories = [
  { video_category: '热门推荐', count: 100 },
  { video_category: '动作电影', count: 85 },
  { video_category: '喜剧片', count: 72 },
  { video_category: '科幻大片', count: 68 },
  { video_category: '爱情电影', count: 55 },
  { video_category: '恐怖惊悚', count: 45 },
  { video_category: '纪录片', count: 38 },
  { video_category: '动漫', count: 90 }
]

// Mock videos 模拟视频数据
export const mockVideos = [
  {
    video_id: 1,
    video_title: '流浪地球2 - 太阳即将毁灭人类面临末日危机',
    video_category: '科幻大片',
    video_image: '',
    video_duration: '2:53:00',
    play_count: 1250000,
    video_coins: 0,
    video_url: ''
  },
  {
    video_id: 2,
    video_title: '满江红 - 南宋绍兴年间精彩悬疑大片',
    video_category: '热门推荐',
    video_image: '',
    video_duration: '2:39:00',
    play_count: 980000,
    video_coins: 0,
    video_url: ''
  },
  {
    video_id: 3,
    video_title: '速度与激情10 - 极限飙车终极对决',
    video_category: '动作电影',
    video_image: '',
    video_duration: '2:21:00',
    play_count: 850000,
    video_coins: 0,
    video_url: ''
  },
  {
    video_id: 4,
    video_title: '消失的她 - 悬疑推理神作',
    video_category: '热门推荐',
    video_image: '',
    video_duration: '1:58:00',
    play_count: 720000,
    video_coins: 5,
    video_url: ''
  },
  {
    video_id: 5,
    video_title: '孤注一掷 - 缅北诈骗惊人内幕',
    video_category: '热门推荐',
    video_image: '',
    video_duration: '2:10:00',
    play_count: 650000,
    video_coins: 0,
    video_url: ''
  },
  {
    video_id: 6,
    video_title: '变形金刚7 - 超燃机甲战斗',
    video_category: '科幻大片',
    video_image: '',
    video_duration: '2:27:00',
    play_count: 580000,
    video_coins: 0,
    video_url: ''
  },
  {
    video_id: 7,
    video_title: '封神第一部 - 史诗级神话巨作',
    video_category: '动作电影',
    video_image: '',
    video_duration: '2:28:00',
    play_count: 520000,
    video_coins: 0,
    video_url: ''
  },
  {
    video_id: 8,
    video_title: '碟中谍7 - 阿汤哥极限挑战',
    video_category: '动作电影',
    video_image: '',
    video_duration: '2:43:00',
    play_count: 480000,
    video_coins: 0,
    video_url: ''
  },
  {
    video_id: 9,
    video_title: '你好李焕英 - 感人至深喜剧片',
    video_category: '喜剧片',
    video_image: '',
    video_duration: '2:08:00',
    play_count: 890000,
    video_coins: 0,
    video_url: ''
  },
  {
    video_id: 10,
    video_title: '唐人街探案3 - 爆笑推理冒险',
    video_category: '喜剧片',
    video_image: '',
    video_duration: '2:16:00',
    play_count: 760000,
    video_coins: 0,
    video_url: ''
  },
  {
    video_id: 11,
    video_title: '铃芽之旅 - 新海诚最新力作',
    video_category: '动漫',
    video_image: '',
    video_duration: '2:02:00',
    play_count: 680000,
    video_coins: 0,
    video_url: ''
  },
  {
    video_id: 12,
    video_title: '灌篮高手 - 青春热血动画',
    video_category: '动漫',
    video_image: '',
    video_duration: '2:04:00',
    play_count: 920000,
    video_coins: 0,
    video_url: ''
  },
  {
    video_id: 13,
    video_title: '鬼灭之刃 - 上弦决战篇',
    video_category: '动漫',
    video_image: '',
    video_duration: '1:45:00',
    play_count: 750000,
    video_coins: 0,
    video_url: ''
  },
  {
    video_id: 14,
    video_title: '蓝色星球 - BBC自然纪录片',
    video_category: '纪录片',
    video_image: '',
    video_duration: '1:30:00',
    play_count: 320000,
    video_coins: 0,
    video_url: ''
  },
  {
    video_id: 15,
    video_title: '想见你 - 穿越时空的爱恋',
    video_category: '爱情电影',
    video_image: '',
    video_duration: '1:52:00',
    play_count: 450000,
    video_coins: 0,
    video_url: ''
  }
]

/**
 * Get mock categories 获取模拟分类
 * @returns {Array} Mock categories
 */
export function getMockCategories() {
  return [...mockCategories]
}

/**
 * Get mock videos by category 按分类获取模拟视频
 * @param {string} category - Category name
 * @param {number} limit - Max number of videos
 * @returns {Array} Filtered mock videos
 */
export function getMockVideosByCategory(category, limit = 10) {
  if (!category) {
    return mockVideos.slice(0, limit)
  }
  return mockVideos
    .filter(v => v.video_category === category)
    .slice(0, limit)
}

/**
 * Get top mock videos 获取热门模拟视频
 * @param {number} limit - Max number of videos
 * @returns {Array} Top mock videos sorted by play count
 */
export function getMockTopVideos(limit = 5) {
  return [...mockVideos]
    .sort((a, b) => b.play_count - a.play_count)
    .slice(0, limit)
}

/**
 * Search mock videos 搜索模拟视频
 * @param {string} keyword - Search keyword
 * @param {number} limit - Max number of results
 * @returns {Array} Matching mock videos
 */
export function searchMockVideos(keyword, limit = 20) {
  if (!keyword) return []
  const lowerKeyword = keyword.toLowerCase()
  return mockVideos
    .filter(v => 
      v.video_title.toLowerCase().includes(lowerKeyword) ||
      v.video_category.toLowerCase().includes(lowerKeyword)
    )
    .slice(0, limit)
}

export default {
  mockCategories,
  mockVideos,
  getMockCategories,
  getMockVideosByCategory,
  getMockTopVideos,
  searchMockVideos
}
