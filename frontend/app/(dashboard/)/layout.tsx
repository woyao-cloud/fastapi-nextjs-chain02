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