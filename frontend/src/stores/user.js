import { defineStore } from 'pinia'
import { client } from '@/api/client'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: null,
    refreshToken: null,
    userId: null,
    isSuperuser: false,
    userInfo: null
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.isSuperuser
  },

  actions: {
    // 登录
    async login(username, password) {
      console.log('[DEBUG] 开始登录:', { username, passwordLength: password?.length })

      const formData = new URLSearchParams()
      formData.append('username', username)
      formData.append('password', password)
      formData.append('grant_type', 'password')
      formData.append('scope', '')

      console.log('[DEBUG] 登录请求体:', formData.toString())

      const response = await client.POST('/v1/login', {
        body: formData,
        // 显式设置 Content-Type，确保使用 form-urlencoded 格式
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })

      console.log('[DEBUG] 登录响应:', response)
      console.log('[DEBUG] 响应状态:', response.response?.status)
      console.log('[DEBUG] 响应数据:', response.data)

      // 检查响应数据是否存在
      if (!response.data) {
        console.error('[DEBUG] 登录失败：响应数据为空')
        throw new Error('登录失败：未收到服务器响应')
      }

      this.setAuth(response.data)
      console.log('[DEBUG] 登录成功，token 已保存')
      return response.data
    },

    // 注册
    async register(username, password, nickname) {
      console.log('[DEBUG] 开始注册:', { username, nickname, passwordLength: password?.length })

      const response = await client.POST('/v1/user', {
        body: { username, password, nickname }
      })

      console.log('[DEBUG] 注册响应:', response)
      console.log('[DEBUG] 响应状态:', response.response?.status)
      console.log('[DEBUG] 响应数据:', response.data)

      return response.data
    },

    // 管理员注册
    async registerAdmin(username, password, nickname, email, adminRegisterKey) {
      console.log('[DEBUG] 开始管理员注册:', { username, nickname, email, passwordLength: password?.length })

      const body = { username, password, admin_register_key: adminRegisterKey }
      if (nickname) body.nickname = nickname
      if (email) body.email = email

      const response = await client.POST('/v1/user', {
        body: body
      })

      console.log('[DEBUG] 管理员注册响应:', response)
      console.log('[DEBUG] 响应状态:', response.response?.status)
      console.log('[DEBUG] 响应数据:', response.data)

      return response.data
    },

    // 刷新Token
    async refreshAccessToken() {
      console.log('[DEBUG] 开始刷新 Token')
      if (!this.refreshToken) {
        console.log('[DEBUG] 没有 refresh token，无法刷新')
        return false
      }
      try {
        const response = await client.POST('/v1/refresh', {
          body: { refresh_token: this.refreshToken }
        })
        console.log('[DEBUG] 刷新 Token 响应:', response)
        if (!response.data) {
          console.log('[DEBUG] 刷新失败：响应数据为空')
          return false
        }
        this.setAuth(response.data)
        console.log('[DEBUG] Token 刷新成功')
        return true
      } catch (error) {
        console.error('[DEBUG] 刷新 Token 出错:', error)
        this.clearAuth()
        return false
      }
    },

    // 登出
    async logout() {
      console.log('[DEBUG] 开始登出')
      try {
        await client.POST('/v1/logout')
        console.log('[DEBUG] 登出 API 调用成功')
      } catch (error) {
        console.error('[DEBUG] 登出 API 调用失败:', error)
        // 忽略登出接口错误，直接清除本地状态
      } finally {
        this.clearAuth()
        console.log('[DEBUG] 本地认证信息已清除')
      }
    },

    // 设置认证信息
    setAuth(data) {
      console.log('[DEBUG] 设置认证信息:', {
        hasToken: !!data.access_token,
        hasRefreshToken: !!data.refresh_token,
        userId: data.user_id,
        isSuperuser: data.is_superuser,
        isSuperuserType: typeof data.is_superuser
      })
      this.token = data.access_token
      this.refreshToken = data.refresh_token
      this.userId = data.user_id
      
      // 确保 is_superuser 为布尔值 true
      const isSuperuserValue = data.is_superuser === true || data.is_superuser === 'true';
      this.isSuperuser = isSuperuserValue;
      console.log('[DEBUG] isSuperuser 设置为:', this.isSuperuser)

      // 同时也保存到 localStorage（兼容现有的请求拦截器）
      localStorage.setItem('token', JSON.stringify(data.access_token))
      localStorage.setItem('refresh_token', data.refresh_token)
      localStorage.setItem('user_id', String(data.user_id))
      localStorage.setItem('is_superuser', String(data.is_superuser))
      console.log('[DEBUG] 认证信息已保存到 localStorage')

      // 登录成功后获取用户信息
      this.fetchUserInfo()
    },

    // 清除认证信息
    clearAuth() {
      console.log('[DEBUG] 清除认证信息')
      this.token = null
      this.refreshToken = null
      this.userId = null
      this.isSuperuser = false
      this.userInfo = null

      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_id')
      localStorage.removeItem('is_superuser')
    },

    // 从 localStorage 恢复状态
    restoreState() {
      const token = localStorage.getItem('token')
      if (token) {
        try {
          this.token = JSON.parse(token)
          this.refreshToken = localStorage.getItem('refresh_token')
          this.userId = Number(localStorage.getItem('user_id'))
          this.isSuperuser = localStorage.getItem('is_superuser') === 'true'

          // 恢复状态后获取用户信息
          this.fetchUserInfo()
        } catch (error) {
          // localStorage 数据损坏，清除
          this.clearAuth()
        }
      }
    },

    // 获取当前用户信息
    async fetchUserInfo() {
      console.log('[DEBUG] 获取用户信息')
      try {
        const response = await client.GET('/v1/users')
        if (response.data) {
          this.userInfo = response.data
          console.log('[DEBUG] 用户信息获取成功:', response.data)
        }
      } catch (error) {
        console.error('[DEBUG] 获取用户信息失败:', error)
      }
    }
  }
})
