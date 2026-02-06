import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../components/Layout.vue' // 主布局
import Login from '../views/Login.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login, // 登录页独立，不包裹在 Layout 中
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/',
    name: 'Home',
    component: Layout, // Layout 组件已经包含了 Main，不需要嵌套路由
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
import { useUserStore } from '@/stores/user'

router.beforeEach((to, from, next) => {
  console.log('[Router] 路由跳转:', { from: from.path, to: to.path, requiresAuth: to.meta.requiresAuth })

  const userStore = useUserStore()

  // 从 localStorage 恢复状态
  userStore.restoreState()

  console.log('[Router] 用户登录状态:', {
    isLoggedIn: userStore.isLoggedIn,
    userId: userStore.userId,
    hasToken: !!userStore.token
  })

  const requiresAuth = to.meta.requiresAuth !== false // 默认需要认证

  if (requiresAuth && !userStore.isLoggedIn) {
    // 需要认证但未登录，跳转到登录页
    console.log('[Router] 未登录，跳转到登录页')
    next('/login')
  } else if (to.path === '/login' && userStore.isLoggedIn) {
    // 已登录用户访问登录页，跳转到首页
    console.log('[Router] 已登录访问登录页，跳转到首页')
    next('/')
  } else {
    console.log('[Router] 正常放行')
    next()
  }
})

export default router