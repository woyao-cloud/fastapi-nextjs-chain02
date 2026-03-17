import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Shield, Users, Lock, BarChart } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-background to-secondary/30 py-20">
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            现代化<span className="text-primary">用户管理系统</span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
            基于 FastAPI 和 Next.js 构建的完整用户权限管理解决方案，提供安全、高效、可扩展的用户管理功能。
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" asChild>
              <Link href="/login">立即开始</Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="/register">注册账号</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-background">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl font-bold text-center mb-12">核心功能</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <Card className="text-center">
              <CardHeader>
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary/10 mb-4">
                  <Users className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>用户管理</CardTitle>
                <CardDescription>完整的用户生命周期管理</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  创建、编辑、删除用户，管理用户状态和基本信息
                </p>
              </CardContent>
            </Card>

            <Card className="text-center">
              <CardHeader>
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary/10 mb-4">
                  <Lock className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>权限控制</CardTitle>
                <CardDescription>细粒度的权限管理系统</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  基于角色的访问控制（RBAC），支持权限分配和验证
                </p>
              </CardContent>
            </Card>

            <Card className="text-center">
              <CardHeader>
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary/10 mb-4">
                  <Shield className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>安全可靠</CardTitle>
                <CardDescription>多重安全保护机制</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  JWT 认证、密码加密、会话管理、登录审计等安全功能
                </p>
              </CardContent>
            </Card>

            <Card className="text-center">
              <CardHeader>
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary/10 mb-4">
                  <BarChart className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>数据洞察</CardTitle>
                <CardDescription>全面的数据统计和分析</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  用户行为分析、系统使用统计、操作审计日志
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-primary/10 to-secondary/10">
        <div className="container mx-auto px-6 text-center">
          <h2 className="text-3xl font-bold mb-6">立即体验现代化用户管理</h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
            免费试用完整功能，无需信用卡，立即开始构建您的用户管理系统。
          </p>
          <Button size="lg" asChild>
            <Link href="/register">免费开始使用</Link>
          </Button>
        </div>
      </section>
    </div>
  )
}