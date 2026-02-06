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
    name: 'Home',
    component: Layout // Layout 组件已经包含了 Main，不需要嵌套路由
  }
]


const router = createRouter({
  history: createWebHistory(),
  routes
})


export default router