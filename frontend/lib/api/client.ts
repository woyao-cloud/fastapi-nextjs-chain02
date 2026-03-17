import axios from "axios"
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from "axios"

// 从环境变量获取API基础URL，默认为开发环境
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

export class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        "Content-Type": "application/json",
      },
    })

    // 请求拦截器 - 添加认证令牌
    this.client.interceptors.request.use(
      (config) => {
        // 从localStorage获取令牌
        const accessToken = localStorage.getItem("access_token")
        if (accessToken) {
          config.headers.Authorization = `Bearer ${accessToken}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // 响应拦截器 - 处理令牌刷新和错误
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config

        // 如果是401错误且不是刷新令牌请求，尝试刷新令牌
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true

          try {
            // 尝试刷新令牌
            const refreshToken = localStorage.getItem("refresh_token")
            if (!refreshToken) {
              throw new Error("No refresh token available")
            }

            const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
              refresh_token: refreshToken,
            })

            const { access_token, refresh_token } = response.data

            // 存储新令牌
            localStorage.setItem("access_token", access_token)
            localStorage.setItem("refresh_token", refresh_token)

            // 更新原始请求的授权头
            originalRequest.headers.Authorization = `Bearer ${access_token}`

            // 重试原始请求
            return this.client(originalRequest)
          } catch (refreshError) {
            // 刷新失败，清除令牌并重定向到登录页
            localStorage.removeItem("access_token")
            localStorage.removeItem("refresh_token")

            // 如果是客户端环境，重定向到登录页
            if (typeof window !== "undefined") {
              window.location.href = "/login"
            }

            return Promise.reject(refreshError)
          }
        }

        return Promise.reject(error)
      }
    )
  }

  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config)
    return response.data
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config)
    return response.data
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<T>(url, data, config)
    return response.data
  }

  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.patch<T>(url, data, config)
    return response.data
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config)
    return response.data
  }
}

// 创建默认实例
export const apiClient = new ApiClient()

// 默认导出axios实例
export default apiClient