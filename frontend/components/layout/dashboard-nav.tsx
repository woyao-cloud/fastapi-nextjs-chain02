"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { User } from "@/types/user"
import {
  Users,
  Settings,
  LogOut,
  Home,
  Shield,
  User as UserIcon,
  BarChart3,
  FileText,
  Bell
} from "lucide-react"

interface DashboardNavProps {
  user: User
}

const navItems = [
  {
    title: "仪表板",
    href: "/dashboard",
    icon: Home,
  },
  {
    title: "用户管理",
    href: "/dashboard/users",
    icon: Users,
    permissions: ["users.list"],
  },
  {
    title: "角色管理",
    href: "/dashboard/roles",
    icon: Shield,
    permissions: ["roles.list"],
  },
  {
    title: "审计日志",
    href: "/dashboard/audit-logs",
    icon: FileText,
    permissions: ["audit_logs.list"],
  },
  {
    title: "系统设置",
    href: "/dashboard/settings",
    icon: Settings,
    permissions: ["settings.manage"],
  },
]

export function DashboardNav({ user }: DashboardNavProps) {
  const pathname = usePathname()

  // 检查用户是否有权限访问特定菜单项
  const hasPermission = (requiredPermissions?: string[]) => {
    if (!requiredPermissions || requiredPermissions.length === 0) {
      return true
    }

    // 超级管理员拥有所有权限
    if (user.is_superuser || user.permissions?.includes("*")) {
      return true
    }

    return requiredPermissions.some(permission =>
      user.permissions?.includes(permission)
    )
  }

  const handleLogout = async () => {
    // 实现登出逻辑
    try {
      // 清除本地存储的令牌
      localStorage.removeItem("access_token")
      localStorage.removeItem("refresh_token")

      // 调用API登出
      // await AuthApi.logout()

      // 重定向到登录页
      window.location.href = "/login"
    } catch (error) {
      console.error("Logout failed:", error)
    }
  }

  return (
    <div className="flex h-full flex-col">
      {/* Logo/品牌 */}
      <div className="px-6 py-4 border-b">
        <Link href="/dashboard" className="flex items-center space-x-2">
          <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
            <UserIcon className="h-5 w-5 text-primary-foreground" />
          </div>
          <span className="text-lg font-semibold">用户管理系统</span>
        </Link>
      </div>

      {/* 用户信息 */}
      <div className="px-6 py-4 border-b">
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
            {user.avatar_url ? (
              <img
                src={user.avatar_url}
                alt={user.username}
                className="h-10 w-10 rounded-full"
              />
            ) : (
              <UserIcon className="h-5 w-5 text-primary" />
            )}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">
              {user.first_name} {user.last_name}
            </p>
            <p className="text-xs text-muted-foreground truncate">
              @{user.username}
            </p>
          </div>
        </div>
      </div>

      {/* 导航菜单 */}
      <nav className="flex-1 space-y-1 px-4 py-4">
        {navItems.map((item) => {
          if (!hasPermission(item.permissions)) {
            return null
          }

          const isActive = pathname === item.href ||
            (item.href !== "/dashboard" && pathname?.startsWith(item.href))

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center space-x-3 rounded-lg px-3 py-2.5 text-sm transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <item.icon className="h-4 w-4" />
              <span>{item.title}</span>
            </Link>
          )
        })}
      </nav>

      {/* 底部区域 */}
      <div className="mt-auto border-t px-4 py-4">
        <div className="space-y-2">
          {/* 通知按钮 */}
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start"
            onClick={() => {/* 打开通知面板 */}}
          >
            <Bell className="mr-2 h-4 w-4" />
            通知
            <span className="ml-auto rounded-full bg-primary px-2 py-0.5 text-xs text-primary-foreground">
              3
            </span>
          </Button>

          {/* 登出按钮 */}
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start text-destructive hover:text-destructive hover:bg-destructive/10"
            onClick={handleLogout}
          >
            <LogOut className="mr-2 h-4 w-4" />
            退出登录
          </Button>
        </div>
      </div>
    </div>
  )
}