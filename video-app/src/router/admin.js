import { createRouter, createWebHistory } from 'vue-router'
import AdminLayout from '@/views/admin/AdminLayout.vue'
import AdminDashboard from '@/views/admin/AdminDashboard.vue'
import NavCategoriesManager from '@/views/admin/NavCategoriesManager.vue'
import VideoManagement from '@/views/admin/VideoManagement.vue'

const routes = [
  {
    path: '/',
    component: AdminLayout,
    meta: { title: '管理后台' },
    children: [
      {
        path: '',
        redirect: '/dashboard'
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
      },
      {
        path: 'video-management',
        name: 'admin-video-management',
        component: VideoManagement,
        meta: { title: '视频管理' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 悟空视频管理后台` : '悟空视频管理后台'
  next()
})

export default router
