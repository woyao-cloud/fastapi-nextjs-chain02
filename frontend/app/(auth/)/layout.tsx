import { redirect } from 'next/navigation'
import { getCurrentUser } from '@/lib/auth/get-current-user'
import { Card } from '@/components/ui/card'

export default async function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // 如果用户已登录，重定向到仪表板
  const user = await getCurrentUser()
  if (user) {
    redirect('/dashboard')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background to-secondary/30 p-6">
      <div className="w-full max-w-md">
        <Card className="shadow-lg">
          {children}
        </Card>
        <div className="mt-6 text-center text-sm text-muted-foreground">
          <p>
            用户管理系统 © {new Date().getFullYear()}
          </p>
        </div>
      </div>
    </div>
  )
}