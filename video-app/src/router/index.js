import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import PlayerView from '@/views/PlayerView.vue'
import { isScrollRestoring } from '@/utils/scrollManager'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { title: '视频首页' }
  },
  {
    path: '/player/:id',
    name: 'player',
    component: PlayerView,
    meta: { title: '视频播放' }
  },
  {
    path: '/category/:category',
    name: 'category',
    component: HomeView,
    meta: { title: '分类视频' }
  },
  {
    path: '/search',
    name: 'search',
    component: HomeView,
    meta: { title: '搜索结果' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // When returning from player to home/category/search, let the component handle scroll restoration
    // This works together with keep-alive's activated/deactivated hooks in HomeView
    // Return a Promise that never resolves to prevent browser default scroll behavior
    if (from.name === 'player' && (to.name === 'home' || to.name === 'category' || to.name === 'search')) {
      // Return a Promise that waits for our custom scroll restoration to complete
      // This prevents Vue Router from interfering with our scroll position
      return new Promise((resolve) => {
        // Check periodically if our restoration is complete
        const checkRestore = () => {
          if (!isScrollRestoring()) {
            // Don't resolve with a scroll position - let our handler keep the position
            resolve()
          } else {
            requestAnimationFrame(checkRestore)
          }
        }
        // Start checking after a short delay to let our restoration begin
        setTimeout(checkRestore, 50)
      })
    }
    
    // For new routes within home views, scroll to top for new content
    if ((from.name === 'home' || from.name === 'category' || from.name === 'search') && 
        (to.name === 'home' || to.name === 'category' || to.name === 'search')) {
      return { top: 0 }
    }
    
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 视频播放器` : '视频播放器'
  next()
})

export default router
