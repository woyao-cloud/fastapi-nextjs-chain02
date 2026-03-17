import { apiClient } from "./client"
import type { User, Role } from "@/types/user"

export interface LoginRequest {
  username: string
  password: string
  remember_me?: boolean
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface RefreshTokenRequest {
  refresh_token: string
}

export interface RefreshTokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  first_name: string
  last_name: string
  phone_number?: string
}

export interface RegisterResponse {
  id: string
  username: string
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  is_verified: boolean
  created_at: string
}

export interface ForgotPasswordRequest {
  email: string
}

export interface ResetPasswordRequest {
  token: string
  new_password: string
}

export interface VerifyEmailRequest {
  token: string
}

export interface AuthApiResponse<T = any> {
  data: T
  meta?: {
    timestamp: string
    request_id: string
    [key: string]: any
  }
  links?: {
    [key: string]: string
  }
}

export class AuthApi {
  /**
   * 用户登录
   */
  static async login(username: string, password: string): Promise<LoginResponse> {
    const response = await apiClient.post<AuthApiResponse<LoginResponse>>("/v1/auth/login", {
      username,
      password,
      remember_me: false,
    })
    return response.data
  }

  /**
   * 用户注册
   */
  static async register(data: RegisterRequest): Promise<RegisterResponse> {
    const response = await apiClient.post<AuthApiResponse<RegisterResponse>>("/v1/auth/register", data)
    return response.data
  }

  /**
   * 刷新访问令牌
   */
  static async refreshToken(refreshToken: string): Promise<RefreshTokenResponse> {
    const response = await apiClient.post<AuthApiResponse<RefreshTokenResponse>>("/v1/auth/refresh", {
      refresh_token: refreshToken,
    })
    return response.data
  }

  /**
   * 用户登出
   */
  static async logout(): Promise<void> {
    await apiClient.post("/v1/auth/logout")
  }

  /**
   * 获取当前用户信息
   */
  static async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<AuthApiResponse<User>>("/v1/auth/me")
    return response.data
  }

  /**
   * 请求密码重置邮件
   */
  static async forgotPassword(email: string): Promise<void> {
    await apiClient.post("/v1/auth/forgot-password", { email })
  }

  /**
   * 重置密码
   */
  static async resetPassword(token: string, newPassword: string): Promise<void> {
    await apiClient.post("/v1/auth/reset-password", {
      token,
      new_password: newPassword,
    })
  }

  /**
   * 验证邮箱
   */
  static async verifyEmail(token: string): Promise<void> {
    await apiClient.post("/v1/auth/verify-email", { token })
  }
}