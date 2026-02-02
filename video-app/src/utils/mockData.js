/**
 * Mock data for demo purposes when API is unavailable
 * 当API不可用时用于演示的模拟数据
 */

// Mock categories 模拟分类 - includes all main category subcategories
export const mockCategories = [
  // 推荐 (Recommend)
  { video_category: '热门推荐', count: 100 },
  { video_category: '动作电影', count: 85 },
  { video_category: '喜剧片', count: 72 },
  { video_category: '科幻大片', count: 68 },
  { video_category: '爱情电影', count: 55 },
  { video_category: '恐怖惊悚', count: 45 },
  { video_category: '纪录片', count: 38 },
  { video_category: '动漫', count: 90 },
  // 日本 (Japan)
  { video_category: '日本AV', count: 150 },
  { video_category: '无码高清', count: 120 },
  { video_category: '制服诱惑', count: 95 },
  { video_category: '人妻系列', count: 80 },
  // 国产 (Domestic)
  { video_category: '国产自拍', count: 200 },
  { video_category: '网红主播', count: 180 },
  { video_category: '偷拍私拍', count: 90 },
  { video_category: '情侣实录', count: 75 },
  // 动漫 (Anime)
  { video_category: '里番动漫', count: 130 },
  { video_category: '3D动画', count: 85 },
  { video_category: '同人作品', count: 60 },
  { video_category: 'NTR剧情', count: 45 },
  // 福利 (Welfare)
  { video_category: '写真福利', count: 170 },
  { video_category: '丝袜美腿', count: 140 },
  { video_category: '性感模特', count: 110 },
  { video_category: '大尺度写真', count: 95 }
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
  },
  // 日本 (Japan) category videos
  {
    video_id: 16,
    video_title: '日本AV精选合集 - 高清无删减',
    video_category: '日本AV',
    video_image: '',
    video_duration: '1:45:00',
    play_count: 1500000,
    video_coins: 10,
    video_url: ''
  },
  {
    video_id: 17,
    video_title: '无码高清系列 - 极致体验',
    video_category: '无码高清',
    video_image: '',
    video_duration: '1:30:00',
    play_count: 1200000,
    video_coins: 15,
    video_url: ''
  },
  {
    video_id: 18,
    video_title: '制服诱惑特辑 - 校园风采',
    video_category: '制服诱惑',
    video_image: '',
    video_duration: '1:20:00',
    play_count: 950000,
    video_coins: 8,
    video_url: ''
  },
  {
    video_id: 19,
    video_title: '人妻系列精选 - 成熟魅力',
    video_category: '人妻系列',
    video_image: '',
    video_duration: '1:35:00',
    play_count: 800000,
    video_coins: 10,
    video_url: ''
  },
  // 国产 (Domestic) category videos
  {
    video_id: 20,
    video_title: '国产自拍精选 - 真实记录',
    video_category: '国产自拍',
    video_image: '',
    video_duration: '0:45:00',
    play_count: 2000000,
    video_coins: 5,
    video_url: ''
  },
  {
    video_id: 21,
    video_title: '网红主播直播精华 - 热门合集',
    video_category: '网红主播',
    video_image: '',
    video_duration: '1:10:00',
    play_count: 1800000,
    video_coins: 8,
    video_url: ''
  },
  {
    video_id: 22,
    video_title: '偷拍私拍合集 - 独家首发',
    video_category: '偷拍私拍',
    video_image: '',
    video_duration: '0:55:00',
    play_count: 900000,
    video_coins: 12,
    video_url: ''
  },
  {
    video_id: 23,
    video_title: '情侣实录 - 真情流露',
    video_category: '情侣实录',
    video_image: '',
    video_duration: '0:40:00',
    play_count: 750000,
    video_coins: 6,
    video_url: ''
  },
  // 动漫 (Anime) category videos
  {
    video_id: 24,
    video_title: '里番动漫精选 - 经典推荐',
    video_category: '里番动漫',
    video_image: '',
    video_duration: '0:25:00',
    play_count: 1300000,
    video_coins: 5,
    video_url: ''
  },
  {
    video_id: 25,
    video_title: '3D动画大作 - 视觉盛宴',
    video_category: '3D动画',
    video_image: '',
    video_duration: '0:30:00',
    play_count: 850000,
    video_coins: 8,
    video_url: ''
  },
  {
    video_id: 26,
    video_title: '同人作品集 - 粉丝创作',
    video_category: '同人作品',
    video_image: '',
    video_duration: '0:20:00',
    play_count: 600000,
    video_coins: 3,
    video_url: ''
  },
  {
    video_id: 27,
    video_title: 'NTR剧情动漫 - 虐心故事',
    video_category: 'NTR剧情',
    video_image: '',
    video_duration: '0:28:00',
    play_count: 450000,
    video_coins: 5,
    video_url: ''
  },
  // 福利 (Welfare) category videos
  {
    video_id: 28,
    video_title: '写真福利特辑 - 高清大图',
    video_category: '写真福利',
    video_image: '',
    video_duration: '0:35:00',
    play_count: 1700000,
    video_coins: 0,
    video_url: ''
  },
  {
    video_id: 29,
    video_title: '丝袜美腿写真 - 极致诱惑',
    video_category: '丝袜美腿',
    video_image: '',
    video_duration: '0:28:00',
    play_count: 1400000,
    video_coins: 0,
    video_url: ''
  },
  {
    video_id: 30,
    video_title: '性感模特拍摄花絮',
    video_category: '性感模特',
    video_image: '',
    video_duration: '0:42:00',
    play_count: 1100000,
    video_coins: 5,
    video_url: ''
  },
  {
    video_id: 31,
    video_title: '大尺度写真精选集',
    video_category: '大尺度写真',
    video_image: '',
    video_duration: '0:38:00',
    play_count: 950000,
    video_coins: 8,
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
