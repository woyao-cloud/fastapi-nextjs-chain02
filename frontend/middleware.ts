import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// 需要认证的路由
const protectedRoutes = [
  '/dashboard',
  '/dashboard/:path*',
  '/api/:path*', // 保护API路由
]

// 公开路由（无需认证）
const publicRoutes = [
  '/',
  '/login',
  '/register',
  '/forgot-password',
  '/reset-password',
  '/verify-email',
  '/auth/:path*',
]

// 认证后重定向到仪表板的路由
const authRoutes = [
  '/login',
  '/register',
]

/**
 * 检查请求是否匹配路径模式
 */
function matchesPath(pathname: string, patterns: string[]): boolean {
  for (const pattern of patterns) {
    // 简单路径匹配
    if (pattern === pathname) {
      return true
    }

    // 通配符匹配
    if (pattern.includes('*')) {
      const regexPattern = pattern.replace(/\*/g, '.*')
      const regex = new RegExp(`^${regexPattern}$`)
      if (regex.test(pathname)) {
        return true
      }
    }

    // 参数匹配（如 /dashboard/:path*）
    if (pattern.includes(':')) {
      const patternParts = pattern.split('/')
      const pathParts = pathname.split('/')

      if (patternParts.length !== pathParts.length) {
        continue
      }

      let matches = true
      for (let i = 0; i < patternParts.length; i++) {
        if (patternParts[i].startsWith(':')) {
          // 参数部分，匹配任何非空段
          if (!pathParts[i]) {
            matches = false
            break
          }
        } else if (patternParts[i] !== pathParts[i]) {
          matches = false
          break
        }
      }

      if (matches) {
        return true
      }
    }
  }

  return false
}

/**
 * 从请求中获取访问令牌
 */
function getAccessToken(request: NextRequest): string | null {
  // 1. 从Authorization头获取
  const authHeader = request.headers.get('authorization')
  if (authHeader?.startsWith('Bearer ')) {
    return authHeader.substring(7)
  }

  // 2. 从cookie获取
  const tokenCookie = request.cookies.get('access_token')
  if (tokenCookie) {
    return tokenCookie.value
  }

  // 3. 从查询参数获取（用于邮箱验证等）
  const { searchParams } = new URL(request.url)
  const tokenParam = searchParams.get('token')
  if (tokenParam) {
    return tokenParam
  }

  return null
}

/**
 * 验证令牌有效性
 * 在实际应用中，这里应该调用API验证令牌
 */
async function validateToken(token: string): Promise<boolean> {
  // TODO: 实现实际的令牌验证逻辑
  // 暂时返回true，假设令牌有效
  return true
}

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // 检查是否是公开路由
  const isPublicRoute = matchesPath(pathname, publicRoutes)
  const isProtectedRoute = matchesPath(pathname, protectedRoutes)
  const isAuthRoute = matchesPath(pathname, authRoutes)

  // 获取令牌
  const token = getAccessToken(request)

  // 如果是API路由，添加CORS头
  if (pathname.startsWith('/api/')) {
    const response = NextResponse.next()
    response.headers.set('Access-Control-Allow-Origin', '*')
    response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response
  }

  // 如果是认证路由且用户已登录，重定向到仪表板
  if (isAuthRoute && token) {
    // 验证令牌有效性
    const isValid = await validateToken(token)
    if (isValid) {
      return NextResponse.redirect(new URL('/dashboard', request.url))
    }
  }

  // 如果是受保护路由且用户未登录，重定向到登录页
  if (isProtectedRoute && !token) {
    const loginUrl = new URL('/login', request.url)
    // 保存当前URL以便登录后重定向回来
    loginUrl.searchParams.set('redirect', pathname)
    return NextResponse.redirect(loginUrl)
  }

  // 如果是受保护路由且有令牌，验证令牌有效性
  if (isProtectedRoute && token) {
    const isValid = await validateToken(token)
    if (!isValid) {
      const loginUrl = new URL('/login', request.url)
      loginUrl.searchParams.set('expired', 'true')
      return NextResponse.redirect(loginUrl)
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * 匹配所有请求路径，除了：
     * - _next/static (静态文件)
     * - _next/image (图片优化)
     * - favicon.ico (网站图标)
     * - public文件夹
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico)$).*)',
  ],
}