import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../components/Layout.vue' // 主布局
import Login from '../views/Login.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login, // 登录页独立，不包裹在 Layout 中
    meta: { title: '登录' } 
  },
  {
    path: '/',
    component: Layout, // 主应用包裹在 Layout 中
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('../components/Layout.vue') // 主页面
      },
      // 其他页面...
    ]
  }
]


const router = createRouter({
  history: createWebHistory(),
  routes
})


export default router