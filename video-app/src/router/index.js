import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import PlayerView from '@/views/PlayerView.vue'
import CategoryView from '@/views/CategoryView.vue'
import DarkWebView from '@/views/DarkWebView.vue'
import LiveView from '@/views/LiveView.vue'
import GamesView from '@/views/GamesView.vue'
import ProfileView from '@/views/ProfileView.vue'
import AdminLayout from '@/views/admin/AdminLayout.vue'
import AdminDashboard from '@/views/admin/AdminDashboard.vue'
import NavCategoriesManager from '@/views/admin/NavCategoriesManager.vue'
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
    component: CategoryView,
    meta: { title: '分类视频' }
  },
  {
    path: '/search',
    name: 'search',
    component: HomeView,
    meta: { title: '搜索结果' }
  },
  {
    path: '/darkweb',
    name: 'darkweb',
    component: DarkWebView,
    meta: { title: '暗网专区' }
  },
  {
    path: '/live',
    name: 'live',
    component: LiveView,
    meta: { title: '直播中心' }
  },
  {
    path: '/games',
    name: 'games',
    component: GamesView,
    meta: { title: '游戏专区' }
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfileView,
    meta: { title: '个人中心' }
  },
  // Admin Routes
  {
    path: '/admin',
    component: AdminLayout,
    meta: { title: '管理后台' },
    children: [
      {
        path: '',
        redirect: '/admin/dashboard'
      },
      {
        path: 'dashboard',
        name: 'admin-dashboard',
        component: AdminDashboard,
        meta: { title: '仪表盘' }
      },
      {
        path: 'nav-categories',
        name: 'admin-nav-categories',
        component: NavCategoriesManager,
        meta: { title: '导航分类管理' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // When returning from player to home/search, let the component handle scroll restoration
    // This works together with keep-alive's activated/deactivated hooks in HomeView
    // Return a Promise that never resolves to prevent browser default scroll behavior
    if (from.name === 'player' && (to.name === 'home' || to.name === 'search')) {
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
    if ((from.name === 'home' || from.name === 'search') && 
        (to.name === 'home' || to.name === 'search')) {
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
  document.title = to.meta.title ? `${to.meta.title} - 悟空视频` : '悟空视频'
  next()
})

export default router
