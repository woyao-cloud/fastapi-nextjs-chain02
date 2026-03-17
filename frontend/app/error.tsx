'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { AlertCircle } from 'lucide-react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-6">
      <div className="max-w-md w-full text-center">
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-destructive/10 mb-6">
          <AlertCircle className="h-10 w-10 text-destructive" />
        </div>
        <h1 className="text-2xl font-bold mb-3">发生错误</h1>
        <p className="text-muted-foreground mb-6">
          {error.message || '抱歉，页面加载时出现了问题。'}
        </p>
        <div className="space-y-4">
          <Button onClick={() => reset()}>重试</Button>
          <Button variant="outline" onClick={() => window.location.href = '/'}>
            返回首页
          </Button>
        </div>
        {error.digest && (
          <p className="mt-8 text-xs text-muted-foreground">
            错误代码: {error.digest}
          </p>
        )}
      </div>
    </div>
  )
}