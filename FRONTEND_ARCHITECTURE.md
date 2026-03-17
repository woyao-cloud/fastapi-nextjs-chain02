# Next.js 前端架构设计

## 概述

本文档定义了用户管理系统前端的架构设计。我们采用 Next.js 14（App Router）作为主要框架，配合 TypeScript、Tailwind CSS 和现代 React 生态系统，构建一个高性能、可维护、可扩展的前端应用。

## 架构原则

### 1. 组件化设计
- **原子设计**: Atomic Design 原则（原子、分子、组织、模板、页面）
- **单一职责**: 每个组件只做一件事，且做好
- **组合优于继承**: 通过组件组合构建复杂 UI

### 2. 类型安全
- **全面 TypeScript**: 所有代码都使用 TypeScript
- **运行时验证**: 使用 Zod 进行运行时数据验证
- **API 类型同步**: 自动生成前端类型定义

### 3. 性能优先
- **服务端渲染**: 充分利用 Next.js 的 SSR/SSG 能力
- **代码分割**: 自动代码分割和动态导入
- **图片优化**: 使用 Next.js Image 组件自动优化

### 4. 开发者体验
- **快速反馈**: 热重载和快速构建
- **工具集成**: ESLint、Prettier、Husky 等工具链
- **文档驱动**: Storybook 组件文档

## 项目结构

```
frontend/
├── app/                          # App Router 页面
│   ├── (auth)/                   # 认证相关路由组
│   │   ├── login/
│   │   │   ├── page.tsx
│   │   │   └── layout.tsx
│   │   ├── register/
│   │   │   └── page.tsx
│   │   └── forgot-password/
│   │       └── page.tsx
│   ├── (dashboard)/              # 仪表板路由组
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── users/
│   │   │   ├── page.tsx
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx
│   │   │   └── new/
│   │   │       └── page.tsx
│   │   ├── roles/
│   │   │   └── page.tsx
│   │   └── profile/
│   │       └── page.tsx
│   ├── api/                      # API 路由（前端 API）
│   │   ├── auth/
│   │   │   ├── login/
│   │   │   │   └── route.ts
│   │   │   └── logout/
│   │   │       └── route.ts
│   │   └── health/
│   │       └── route.ts
│   ├── layout.tsx                # 根布局
│   ├── page.tsx                  # 首页
│   ├── error.tsx                 # 全局错误页面
│   ├── loading.tsx               # 全局加载状态
│   ├── not-found.tsx             # 404 页面
│   └── globals.css               # 全局样式
├── components/                   # 共享组件
│   ├── ui/                       # 基础 UI 组件（使用 shadcn/ui）
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   ├── dialog.tsx
│   │   ├── dropdown-menu.tsx
│   │   ├── table.tsx
│   │   └── ...
│   ├── layout/                   # 布局组件
│   │   ├── header.tsx
│   │   ├── sidebar.tsx
│   │   ├── footer.tsx
│   │   └── main-nav.tsx
│   ├── forms/                    # 表单组件
│   │   ├── login-form.tsx
│   │   ├── register-form.tsx
│   │   ├── user-form.tsx
│   │   └── role-form.tsx
│   ├── data-display/             # 数据展示组件
│   │   ├── user-table.tsx
│   │   ├── role-table.tsx
│   │   ├── data-table.tsx
│   │   └── pagination.tsx
│   └── feedback/                 # 反馈组件
│       ├── alert.tsx
│       ├── toast.tsx
│       ├── loading-spinner.tsx
│       └── skeleton.tsx
├── lib/                          # 工具库
│   ├── api/                      # API 客户端
│   │   ├── client.ts             # Axios 实例配置
│   │   ├── auth.ts               # 认证相关 API
│   │   ├── users.ts              # 用户相关 API
│   │   ├── roles.ts              # 角色相关 API
│   │   └── types/                # 自动生成的 API 类型
│   │       └── index.ts
│   ├── utils/                    # 工具函数
│   │   ├── validators.ts         # 验证工具
│   │   ├── formatters.ts         # 格式化工具
│   │   ├── constants.ts          # 常量定义
│   │   └── helpers.ts            # 辅助函数
│   ├── hooks/                    # 自定义 Hook
│   │   ├── use-auth.ts           # 认证状态 Hook
│   │   ├── use-api.ts            # API 调用 Hook
│   │   ├── use-permissions.ts    # 权限检查 Hook
│   │   └── use-toast.ts          # Toast 通知 Hook
│   └── schemas/                  # Zod 模式定义
│       ├── auth.ts
│       ├── user.ts
│       ├── role.ts
│       └── common.ts
├── stores/                       # 状态管理
│   ├── auth-store.ts             # 认证状态
│   ├── user-store.ts             # 用户状态
│   ├── ui-store.ts               # UI 状态
│   └── index.ts                  # 统一导出
├── styles/                       # 样式文件
│   ├── themes/                   # 主题定义
│   │   ├── light.ts
│   │   ├── dark.ts
│   │   └── index.ts
│   └── animations.css            # 动画定义
├── types/                        # 类型定义
│   ├── user.ts
│   ├── role.ts
│   ├── auth.ts
│   └── index.ts
├── middleware.ts                 # 中间件（路由保护）
├── next.config.js                # Next.js 配置
├── tailwind.config.js            # Tailwind 配置
├── tsconfig.json                 # TypeScript 配置
├── package.json                  # 项目依赖
└── README.md
```

## 核心组件设计

### 1. 布局系统

**根布局 (app/layout.tsx)**:
```tsx
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { ThemeProvider } from '@/components/providers/theme-provider'
import { AuthProvider } from '@/components/providers/auth-provider'
import { Toaster } from '@/components/ui/toaster'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: '用户管理系统',
  description: '现代化的用户权限管理系统',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <AuthProvider>
            {children}
            <Toaster />
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
```

**仪表板布局 (app/(dashboard)/layout.tsx)**:
```tsx
import { DashboardNav } from '@/components/layout/dashboard-nav'
import { Header } from '@/components/layout/header'
import { requireAuth } from '@/lib/auth/require-auth'

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // 验证用户是否已登录
  const user = await requireAuth()

  return (
    <div className="min-h-screen bg-background">
      <div className="flex min-h-screen">
        {/* 侧边栏 */}
        <aside className="hidden w-64 border-r bg-card lg:block">
          <div className="sticky top-0 h-screen overflow-y-auto py-6">
            <DashboardNav user={user} />
          </div>
        </aside>

        {/* 主内容区 */}
        <main className="flex-1">
          <Header user={user} />
          <div className="container mx-auto p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
```

### 2. 认证系统

**认证提供者 (components/providers/auth-provider.tsx)**:
```tsx
'use client'

import { createContext, useContext, useEffect, useState } from 'react'
import { User } from '@/types/user'
import { AuthService } from '@/lib/services/auth-service'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  refreshToken: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // 初始化时检查认证状态
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        setIsLoading(false)
        return
      }

      // 验证令牌有效性
      const userData = await AuthService.getCurrentUser()
      setUser(userData)
    } catch (error) {
      console.error('Auth check failed:', error)
      // 令牌无效，清理本地存储
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    setIsLoading(true)
    try {
      const { access_token, refresh_token, user } = await AuthService.login(
        email,
        password
      )

      // 存储令牌
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)

      setUser(user)
    } catch (error) {
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    try {
      await AuthService.logout()
    } finally {
      // 无论后端是否成功，都清理本地状态
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      setUser(null)
    }
  }

  const refreshToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) throw new Error('No refresh token')

      const { access_token, refresh_token } = await AuthService.refreshToken(
        refreshToken
      )

      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
    } catch (error) {
      // 刷新失败，强制登出
      logout()
      throw error
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        login,
        logout,
        refreshToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
```

**认证 Hook (lib/hooks/use-auth.ts)**:
```tsx
'use client'

import { useRouter } from 'next/navigation'
import { useAuth } from '@/components/providers/auth-provider'

export function useRequireAuth(redirectTo = '/login') {
  const { user, isLoading } = useAuth()
  const router = useRouter()

  if (!isLoading && !user) {
    router.push(redirectTo)
  }

  return { user, isLoading }
}
```

### 3. API 客户端

**Axios 配置 (lib/api/client.ts)**:
```typescript
import axios, {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from 'axios'
import { AuthService } from '../services/auth-service'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

class ApiClient {
  private instance: AxiosInstance
  private isRefreshing = false
  private failedQueue: Array<{
    resolve: (value: unknown) => void
    reject: (reason?: any) => void
  }> = []

  constructor() {
    this.instance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // 请求拦截器：添加认证令牌
    this.instance.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = localStorage.getItem('access_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // 响应拦截器：处理令牌刷新
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => response,
      async (error) => {
        const originalRequest = error.config

        // 如果是 401 错误且不是刷新令牌的请求
        if (
          error.response?.status === 401 &&
          !originalRequest._retry &&
          !originalRequest.url?.includes('/auth/refresh')
        ) {
          if (this.isRefreshing) {
            // 如果已经在刷新，将请求加入队列
            return new Promise((resolve, reject) => {
              this.failedQueue.push({ resolve, reject })
            })
              .then(() => {
                return this.instance(originalRequest)
              })
              .catch((err) => Promise.reject(err))
          }

          originalRequest._retry = true
          this.isRefreshing = true

          try {
            // 尝试刷新令牌
            await AuthService.refreshToken()
            this.isRefreshing = false

            // 重试所有失败的请求
            this.failedQueue.forEach((promise) => promise.resolve())
            this.failedQueue = []

            // 重试原始请求
            return this.instance(originalRequest)
          } catch (refreshError) {
            this.isRefreshing = false
            this.failedQueue.forEach((promise) => promise.reject(refreshError))
            this.failedQueue = []

            // 刷新失败，跳转到登录页
            if (typeof window !== 'undefined') {
              window.location.href = '/login'
            }

            return Promise.reject(refreshError)
          }
        }

        return Promise.reject(error)
      }
    )
  }

  public get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.get(url, config).then((response) => response.data)
  }

  public post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.post(url, data, config).then((response) => response.data)
  }

  public put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.put(url, data, config).then((response) => response.data)
  }

  public patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.patch(url, data, config).then((response) => response.data)
  }

  public delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.delete(url, config).then((response) => response.data)
  }
}

export const apiClient = new ApiClient()
```

**用户 API (lib/api/users.ts)**:
```typescript
import { apiClient } from './client'
import {
  User,
  UserListResponse,
  UserCreateRequest,
  UserUpdateRequest,
} from '@/types/user'

export const UserApi = {
  // 获取用户列表
  getUsers: async (
    params?: {
      page?: number
      limit?: number
      search?: string
      sortBy?: string
      sortOrder?: 'asc' | 'desc'
    }
  ): Promise<UserListResponse> => {
    return apiClient.get('/users', { params })
  },

  // 获取单个用户
  getUser: async (id: string): Promise<User> => {
    return apiClient.get(`/users/${id}`)
  },

  // 创建用户
  createUser: async (data: UserCreateRequest): Promise<User> => {
    return apiClient.post('/users', data)
  },

  // 更新用户
  updateUser: async (id: string, data: UserUpdateRequest): Promise<User> => {
    return apiClient.put(`/users/${id}`, data)
  },

  // 删除用户
  deleteUser: async (id: string): Promise<void> => {
    return apiClient.delete(`/users/${id}`)
  },

  // 搜索用户
  searchUsers: async (query: string): Promise<User[]> => {
    return apiClient.get('/users/search', { params: { q: query } })
  },
}
```

### 4. 表单处理

**使用 React Hook Form + Zod (components/forms/user-form.tsx)**:
```tsx
'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Switch } from '@/components/ui/switch'
import { Loader2 } from 'lucide-react'
import { UserApi } from '@/lib/api/users'

// Zod 验证模式
const userFormSchema = z.object({
  username: z.string()
    .min(3, '用户名至少3个字符')
    .max(50, '用户名最多50个字符')
    .regex(/^[a-zA-Z0-9_.-]+$/, '只能包含字母、数字、下划线、点和横线'),
  email: z.string()
    .email('请输入有效的邮箱地址')
    .min(5, '邮箱至少5个字符')
    .max(255, '邮箱最多255个字符'),
  firstName: z.string()
    .max(100, '名字最多100个字符')
    .optional(),
  lastName: z.string()
    .max(100, '姓氏最多100个字符')
    .optional(),
  phoneNumber: z.string()
    .regex(/^\+?[1-9]\d{1,14}$/, '请输入有效的手机号码')
    .optional()
    .or(z.literal('')),
  isActive: z.boolean().default(true),
})

type UserFormValues = z.infer<typeof userFormSchema>

interface UserFormProps {
  initialData?: UserFormValues
  userId?: string
  onSuccess?: () => void
  onCancel?: () => void
}

export function UserForm({
  initialData,
  userId,
  onSuccess,
  onCancel,
}: UserFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)

  const form = useForm<UserFormValues>({
    resolver: zodResolver(userFormSchema),
    defaultValues: initialData || {
      username: '',
      email: '',
      firstName: '',
      lastName: '',
      phoneNumber: '',
      isActive: true,
    },
  })

  const onSubmit = async (data: UserFormValues) => {
    setIsSubmitting(true)
    try {
      if (userId) {
        // 更新用户
        await UserApi.updateUser(userId, data)
      } else {
        // 创建用户（需要密码）
        const createData = {
          ...data,
          password: 'TempPassword123!', // 实际应用中应该让用户设置密码或发送重置邮件
        }
        await UserApi.createUser(createData)
      }

      onSuccess?.()
    } catch (error) {
      console.error('Failed to save user:', error)
      // 处理错误，显示错误消息
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormField
            control={form.control}
            name="username"
            render={({ field }) => (
              <FormItem>
                <FormLabel>用户名 *</FormLabel>
                <FormControl>
                  <Input placeholder="john_doe" {...field} />
                </FormControl>
                <FormDescription>
                  用于登录的用户名，只能包含字母、数字、下划线、点和横线
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>邮箱 *</FormLabel>
                <FormControl>
                  <Input type="email" placeholder="john@example.com" {...field} />
                </FormControl>
                <FormDescription>
                  用于接收系统通知和重置密码
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="firstName"
            render={({ field }) => (
              <FormItem>
                <FormLabel>名字</FormLabel>
                <FormControl>
                  <Input placeholder="John" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="lastName"
            render={({ field }) => (
              <FormItem>
                <FormLabel>姓氏</FormLabel>
                <FormControl>
                  <Input placeholder="Doe" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="phoneNumber"
            render={({ field }) => (
              <FormItem>
                <FormLabel>手机号码</FormLabel>
                <FormControl>
                  <Input placeholder="+8613800138000" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <FormField
          control={form.control}
          name="isActive"
          render={({ field }) => (
            <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
              <div className="space-y-0.5">
                <FormLabel className="text-base">账户状态</FormLabel>
                <FormDescription>
                  禁用后用户将无法登录系统
                </FormDescription>
              </div>
              <FormControl>
                <Switch
                  checked={field.value}
                  onCheckedChange={field.onChange}
                />
              </FormControl>
            </FormItem>
          )}
        />

        <div className="flex justify-end space-x-4">
          {onCancel && (
            <Button type="button" variant="outline" onClick={onCancel}>
              取消
            </Button>
          )}
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {userId ? '更新用户' : '创建用户'}
          </Button>
        </div>
      </form>
    </Form>
  )
}
```

### 5. 数据表格组件

**通用数据表格 (components/data-display/data-table.tsx)**:
```tsx
'use client'

import { useState } from 'react'
import {
  ColumnDef,
  ColumnFiltersState,
  SortingState,
  VisibilityState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { ChevronLeft, ChevronRight, Filter, Settings } from 'lucide-react'

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
  searchColumn?: string
  searchPlaceholder?: string
}

export function DataTable<TData, TValue>({
  columns,
  data,
  searchColumn,
  searchPlaceholder = '搜索...',
}: DataTableProps<TData, TValue>) {
  const [sorting, setSorting] = useState<SortingState>([])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({})
  const [rowSelection, setRowSelection] = useState({})

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    state: {
      sorting,
      columnFilters,
      columnVisibility,
      rowSelection,
    },
  })

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        {searchColumn && (
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <Input
              placeholder={searchPlaceholder}
              value={
                (table.getColumn(searchColumn)?.getFilterValue() as string) ?? ''
              }
              onChange={(event) =>
                table.getColumn(searchColumn)?.setFilterValue(event.target.value)
              }
              className="max-w-sm"
            />
          </div>
        )}

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm" className="ml-auto">
              <Settings className="mr-2 h-4 w-4" />
              列设置
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {table
              .getAllColumns()
              .filter((column) => column.getCanHide())
              .map((column) => {
                return (
                  <DropdownMenuCheckboxItem
                    key={column.id}
                    className="capitalize"
                    checked={column.getIsVisible()}
                    onCheckedChange={(value) => column.toggleVisibility(!!value)}
                  >
                    {column.id}
                  </DropdownMenuCheckboxItem>
                )
              })}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </TableHead>
                  )
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && 'selected'}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  暂无数据
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          已选择 {table.getFilteredSelectedRowModel().rows.length} 条，共{' '}
          {table.getFilteredRowModel().rows.length} 条数据
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="text-sm">
            第 {table.getState().pagination.pageIndex + 1} 页，共{' '}
            {table.getPageCount()} 页
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}
```

### 6. 路由保护中间件

**中间件配置 (middleware.ts)**:
```typescript
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { jwtVerify } from 'jose'

const PUBLIC_PATHS = ['/login', '/register', '/forgot-password', '/']
const API_PATHS = ['/api/']

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // 检查是否是公开路径
  const isPublicPath = PUBLIC_PATHS.some((path) => pathname.startsWith(path))
  const isApiPath = API_PATHS.some((path) => pathname.startsWith(path))

  // API 请求使用不同的验证逻辑
  if (isApiPath) {
    return handleApiRequest(request)
  }

  // 公开路径直接放行
  if (isPublicPath) {
    return NextResponse.next()
  }

  // 验证访问令牌
  const token = request.cookies.get('access_token')?.value

  if (!token) {
    // 重定向到登录页
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('redirect', pathname)
    return NextResponse.redirect(loginUrl)
  }

  try {
    // 验证 JWT 令牌
    await jwtVerify(
      token,
      new TextEncoder().encode(process.env.JWT_SECRET!)
    )

    // 令牌有效，继续请求
    return NextResponse.next()
  } catch (error) {
    // 令牌无效，清理 cookie 并重定向
    const response = NextResponse.redirect(new URL('/login', request.url))
    response.cookies.delete('access_token')
    response.cookies.delete('refresh_token')
    return response
  }
}

async function handleApiRequest(request: NextRequest) {
  // 公开 API 路径
  if (request.nextUrl.pathname.startsWith('/api/auth/')) {
    return NextResponse.next()
  }

  const token = request.headers.get('authorization')?.replace('Bearer ', '')

  if (!token) {
    return NextResponse.json(
      { error: '未授权访问' },
      { status: 401 }
    )
  }

  try {
    await jwtVerify(
      token,
      new TextEncoder().encode(process.env.JWT_SECRET!)
    )
    return NextResponse.next()
  } catch (error) {
    return NextResponse.json(
      { error: '令牌无效或已过期' },
      { status: 401 }
    )
  }
}

export const config = {
  matcher: [
    /*
     * 匹配所有路径除了:
     * 1. _next/static (静态文件)
     * 2. _next/image (图片优化)
     * 3. favicon.ico, sitemap.xml, robots.txt
     * 4. 公共资源
     */
    '/((?!_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}
```

## 主题系统

**主题提供者 (components/providers/theme-provider.tsx)**:
```tsx
'use client'

import * as React from 'react'
import { ThemeProvider as NextThemesProvider } from 'next-themes'
import { type ThemeProviderProps } from 'next-themes'

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>
}
```

**主题切换组件 (components/ui/theme-toggle.tsx)**:
```tsx
'use client'

import * as React from 'react'
import { Moon, Sun } from 'lucide-react'
import { useTheme } from 'next-themes'
import { Button } from '@/components/ui/button'

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
    >
      <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
      <span className="sr-only">切换主题</span>
    </Button>
  )
}
```

## 开发指南

### 1. 本地开发
```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 启动生产服务器
npm start
```

### 2. 环境变量配置
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_NAME="用户管理系统"
JWT_SECRET=your-jwt-secret-key-change-in-production
```

### 3. 代码质量工具
```bash
# 代码格式化
npm run format

# 代码检查
npm run lint

# 类型检查
npm run type-check

# 运行测试
npm run test

# 构建检查
npm run build-check
```

### 4. 组件开发
```bash
# 启动 Storybook
npm run storybook

# 生成组件
npx shadcn@latest add button
```

## 性能优化策略

### 1. 图片优化
- 使用 Next.js Image 组件自动优化
- 实现响应式图片和懒加载
- 使用 WebP 格式和图片 CDN

### 2. 代码分割
- 使用动态导入 (`import()`) 分割代码
- 路由级别的代码分割（自动）
- 第三方库单独打包

### 3. 缓存策略
- 服务端数据缓存 (React Cache)
- 客户端数据缓存 (SWR/React Query)
- CDN 静态资源缓存

### 4. 渲染策略
- 静态生成适合的页面 (SSG)
- 服务端渲染动态页面 (SSR)
- 客户端渲染交互密集部分 (CSR)

## 测试策略

### 1. 单元测试
- 组件测试: React Testing Library
- Hook 测试: @testing-library/react-hooks
- 工具函数测试: Jest

### 2. 集成测试
- API 集成测试: Mock Service Worker
- 页面集成测试: Playwright/Cypress

### 3. E2E 测试
- 用户流程测试: Playwright
- 跨浏览器测试: BrowserStack

### 4. 可视化测试
- 组件快照测试: Storybook + Chromatic
- 视觉回归测试: Percy

---
*本文档是前端架构的权威参考，所有前端开发必须遵循此架构设计。架构变更需要更新此文档并通知相关团队。*