export default function Loading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-primary/30 border-t-primary rounded-full animate-spin"></div>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-8 h-8 bg-primary/20 rounded-full animate-ping"></div>
          </div>
        </div>
        <p className="mt-6 text-lg font-medium">加载中...</p>
        <p className="text-sm text-muted-foreground mt-2">请稍等片刻</p>
      </div>
    </div>
  )
}