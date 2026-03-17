import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { User } from '@/types/user'
import { AuthApi } from '@/lib/api/auth'

interface AuthState {
  // 状态
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isLoading: boolean
  error: string | null

  // 计算属性
  isAuthenticated: boolean

  // 操作
  login: (username: string, password: string) => Promise<void>
  register: (data: {
    username: string
    email: string
    password: string
    first_name: string
    last_name: string
    phone_number?: string
  }) => Promise<void>
  logout: () => Promise<void>
  refreshAccessToken: () => Promise<void>
  getCurrentUser: () => Promise<void>
  clearError: () => void
  setTokens: (accessToken: string, refreshToken: string) => void
  setUser: (user: User | null) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // 初始状态
      user: null,
      accessToken: null,
      refreshToken: null,
      isLoading: false,
      error: null,

      // 计算属性
      get isAuthenticated() {
        return !!get().accessToken && !!get().user
      },

      // 登录
      login: async (username: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await AuthApi.login(username, password)

          // 存储令牌和用户信息
          set({
            user: response.user,
            accessToken: response.access_token,
            refreshToken: response.refresh_token,
            isLoading: false,
          })

          // 存储到localStorage（zustand persist已经处理，但为了兼容性也存储）
          localStorage.setItem('access_token', response.access_token)
          localStorage.setItem('refresh_token', response.refresh_token)
        } catch (error: any) {
          set({
            error: error.response?.data?.error?.message || '登录失败',
            isLoading: false,
          })
          throw error
        }
      },

      // 注册
      register: async (data) => {
        set({ isLoading: true, error: null })
        try {
          await AuthApi.register(data)
          set({ isLoading: false })
        } catch (error: any) {
          set({
            error: error.response?.data?.error?.message || '注册失败',
            isLoading: false,
          })
          throw error
        }
      },

      // 登出
      logout: async () => {
        set({ isLoading: true })
        try {
          // 调用API登出
          await AuthApi.logout()
        } catch (error) {
          console.error('Logout API error:', error)
          // 即使API调用失败，也清除本地状态
        } finally {
          // 清除所有状态
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isLoading: false,
            error: null,
          })

          // 清除localStorage
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        }
      },

      // 刷新访问令牌
      refreshAccessToken: async () => {
        const { refreshToken } = get()
        if (!refreshToken) {
          throw new Error('No refresh token available')
        }

        set({ isLoading: true })
        try {
          const response = await AuthApi.refreshToken(refreshToken)
          set({
            accessToken: response.access_token,
            refreshToken: response.refresh_token,
            isLoading: false,
          })

          // 更新localStorage
          localStorage.setItem('access_token', response.access_token)
          localStorage.setItem('refresh_token', response.refresh_token)
        } catch (error: any) {
          set({
            error: error.response?.data?.error?.message || '令牌刷新失败',
            isLoading: false,
          })
          // 刷新失败，清除令牌
          get().logout()
          throw error
        }
      },

      // 获取当前用户信息
      getCurrentUser: async () => {
        set({ isLoading: true, error: null })
        try {
          const user = await AuthApi.getCurrentUser()
          set({
            user,
            isLoading: false,
          })
        } catch (error: any) {
          set({
            error: error.response?.data?.error?.message || '获取用户信息失败',
            isLoading: false,
          })
          throw error
        }
      },

      // 清除错误
      clearError: () => {
        set({ error: null })
      },

      // 设置令牌（用于外部令牌设置，如OAuth回调）
      setTokens: (accessToken: string, refreshToken: string) => {
        set({
          accessToken,
          refreshToken,
        })
        localStorage.setItem('access_token', accessToken)
        localStorage.setItem('refresh_token', refreshToken)
      },

      // 设置用户信息
      setUser: (user: User | null) => {
        set({ user })
      },
    }),
    {
      name: 'auth-storage', // localStorage中的键名
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
      }),
    }
  )
)

// 辅助函数：检查用户是否有特定权限
export const hasPermission = (permission: string): boolean => {
  const { user } = useAuthStore.getState()
  if (!user) return false

  // 超级管理员拥有所有权限
  if (user.is_superuser || user.permissions?.includes('*')) {
    return true
  }

  return user.permissions?.includes(permission) || false
}

// 辅助函数：检查用户是否有任意权限
export const hasAnyPermission = (permissions: string[]): boolean => {
  const { user } = useAuthStore.getState()
  if (!user) return false

  // 超级管理员拥有所有权限
  if (user.is_superuser || user.permissions?.includes('*')) {
    return true
  }

  return permissions.some(permission =>
    user.permissions?.includes(permission)
  ) || false
}

// 辅助函数：检查用户是否有所有权限
export const hasAllPermissions = (permissions: string[]): boolean => {
  const { user } = useAuthStore.getState()
  if (!user) return false

  // 超级管理员拥有所有权限
  if (user.is_superuser || user.permissions?.includes('*')) {
    return true
  }

  return permissions.every(permission =>
    user.permissions?.includes(permission)
  ) || false
}