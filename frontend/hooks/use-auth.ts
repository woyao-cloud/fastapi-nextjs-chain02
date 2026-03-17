import { useCallback } from 'react'
import { useAuthStore } from '@/stores/auth-store'
import type { User } from '@/types/user'

/**
 * 认证相关操作的React Hook
 * 提供对认证状态的便捷访问和操作方法
 */
export function useAuth() {
  const {
    user,
    accessToken,
    refreshToken,
    isLoading,
    error,
    isAuthenticated,
    login,
    register,
    logout,
    refreshAccessToken,
    getCurrentUser,
    clearError,
    setTokens,
    setUser,
  } = useAuthStore()

  /**
   * 检查用户是否有特定权限
   */
  const hasPermission = useCallback((permission: string): boolean => {
    if (!user) return false

    // 超级管理员拥有所有权限
    if (user.is_superuser || user.permissions?.includes('*')) {
      return true
    }

    return user.permissions?.includes(permission) || false
  }, [user])

  /**
   * 检查用户是否有任意权限
   */
  const hasAnyPermission = useCallback((permissions: string[]): boolean => {
    if (!user) return false

    // 超级管理员拥有所有权限
    if (user.is_superuser || user.permissions?.includes('*')) {
      return true
    }

    return permissions.some(permission =>
      user.permissions?.includes(permission)
    ) || false
  }, [user])

  /**
   * 检查用户是否有所有权限
   */
  const hasAllPermissions = useCallback((permissions: string[]): boolean => {
    if (!user) return false

    // 超级管理员拥有所有权限
    if (user.is_superuser || user.permissions?.includes('*')) {
      return true
    }

    return permissions.every(permission =>
      user.permissions?.includes(permission)
    ) || false
  }, [user])

  /**
   * 检查用户是否有特定角色
   */
  const hasRole = useCallback((roleName: string): boolean => {
    if (!user) return false
    return user.roles?.some(role => role.name === roleName) || false
  }, [user])

  /**
   * 检查用户是否有任意角色
   */
  const hasAnyRole = useCallback((roleNames: string[]): boolean => {
    if (!user) return false
    return user.roles?.some(role => roleNames.includes(role.name)) || false
  }, [user])

  /**
   * 初始化认证状态（应用启动时调用）
   */
  const initializeAuth = useCallback(async () => {
    try {
      // 检查localStorage中是否有令牌
      const storedAccessToken = localStorage.getItem('access_token')
      const storedRefreshToken = localStorage.getItem('refresh_token')

      if (storedAccessToken && storedRefreshToken) {
        // 设置令牌
        setTokens(storedAccessToken, storedRefreshToken)

        // 获取用户信息
        await getCurrentUser()
      }
    } catch (error) {
      console.error('Auth initialization failed:', error)
      // 初始化失败，清除令牌
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }, [setTokens, getCurrentUser])

  /**
   * 静默刷新令牌（在后台刷新，不中断用户操作）
   */
  const silentRefresh = useCallback(async () => {
    try {
      await refreshAccessToken()
    } catch (error) {
      console.error('Silent token refresh failed:', error)
      // 刷新失败，可以尝试重新登录或显示提示
    }
  }, [refreshAccessToken])

  return {
    // 状态
    user,
    accessToken,
    refreshToken,
    isLoading,
    error,
    isAuthenticated,

    // 操作
    login,
    register,
    logout,
    refreshAccessToken,
    getCurrentUser,
    clearError,
    setTokens,
    setUser,

    // 权限检查
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    hasRole,
    hasAnyRole,

    // 辅助方法
    initializeAuth,
    silentRefresh,
  }
}

/**
 * 使用权限检查的Hook
 */
export function usePermissions() {
  const { user } = useAuthStore()

  const hasPermission = useCallback((permission: string): boolean => {
    if (!user) return false
    if (user.is_superuser || user.permissions?.includes('*')) return true
    return user.permissions?.includes(permission) || false
  }, [user])

  const hasAnyPermission = useCallback((permissions: string[]): boolean => {
    if (!user) return false
    if (user.is_superuser || user.permissions?.includes('*')) return true
    return permissions.some(p => user.permissions?.includes(p)) || false
  }, [user])

  const hasAllPermissions = useCallback((permissions: string[]): boolean => {
    if (!user) return false
    if (user.is_superuser || user.permissions?.includes('*')) return true
    return permissions.every(p => user.permissions?.includes(p)) || false
  }, [user])

  return {
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
  }
}