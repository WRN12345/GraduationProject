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
    component: Layout, // 主布局包裹所有需要认证的页面
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('../components/Main.vue')
      },
      {
        path: 'communities',
        name: 'CommunityManage',
        component: () => import('../views/CommunityManage.vue'),
        meta: { title: '社区管理' }
      },
      {
        path: 'create-post',
        name: 'CreatePost',
        component: () => import('../views/CreatePost.vue'),
        meta: { title: '创建帖子' }
      },
      {
        path: 'create-community',
        name: 'CreateCommunity',
        component: () => import('../views/CreateCommunity.vue'),
        meta: { title: '创建社区' }
      },
      {
        path: 'all-communities',
        name: 'AllCommunities',
        component: () => import('../views/AllCommunities.vue'),
        meta: { title: '全部社区' }
      },
      {
        path: 'post/:id',
        name: 'PostDetail',
        component: () => import('../views/PostDetail.vue'),
        meta: { title: '帖子详情' }
      },
      {
        path: 'post/:id/edit',
        name: 'EditPost',
        component: () => import('../views/EditPost.vue'),
        meta: { title: '编辑帖子' }
      },
      {
        path: 'my-communities',
        name: 'MyCommunities',
        component: () => import('../views/MyCommunities.vue'),
        meta: { title: '我的社区' }
      },
      {
        path: 'bookmarks',
        name: 'MyBookmarks',
        component: () => import('../views/MyBookmarks.vue'),
        meta: { title: '我的收藏' }
      },
      {
        path: 'my-posts',
        name: 'MyPosts',
        component: () => import('../views/MyPosts.vue'),
        meta: { title: '我的帖子' }
      },
      {
        path: 'community/:id',
        name: 'CommunityDetail',
        component: () => import('../views/CommunityDetail.vue'),
        meta: { title: '社区详情' }
      },
      {
        path: 'community/:id/members',
        name: 'CommunityMembers',
        component: () => import('../views/CommunityMembers.vue'),
        meta: { title: '社区成员' }
      },
      {
        path: 'trending',
        name: 'Trending',
        component: () => import('../views/Trending.vue'),
        meta: { title: '热门内容' }
      },
      {
        path: 'search',
        name: 'SearchResults',
        component: () => import('../views/SearchResults.vue'),
        meta: { title: '搜索结果' }
      },
      {
        path: 'user/:username',
        name: 'UserDetail',
        component: () => import('../views/UserDetail.vue'),
        meta: { title: '用户详情' }
      }
    ]
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