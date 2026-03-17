'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Loader2, CheckCircle } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { AuthApi } from '@/lib/api/auth'

const forgotPasswordSchema = z.object({
  email: z.string()
    .email('请输入有效的邮箱地址')
    .min(5, '邮箱至少5个字符')
    .max(255, '邮箱最多255个字符'),
})

type ForgotPasswordFormValues = z.infer<typeof forgotPasswordSchema>

export default function ForgotPasswordPage() {
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)

  const form = useForm<ForgotPasswordFormValues>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: {
      email: '',
    },
  })

  const onSubmit = async (data: ForgotPasswordFormValues) => {
    setIsLoading(true)
    try {
      await AuthApi.forgotPassword(data.email)
      setIsSubmitted(true)
      toast({
        title: '重置链接已发送',
        description: '如果邮箱存在，重置链接已发送到您的邮箱',
      })
    } catch (error: any) {
      toast({
        title: '发送失败',
        description: error.response?.data?.error?.message || '发送重置链接失败，请稍后重试',
        variant: 'destructive',
      })
    } finally {
      setIsLoading(false)
    }
  }

  if (isSubmitted) {
    return (
      <>
        <CardHeader className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-4">
            <CheckCircle className="h-8 w-8 text-primary" />
          </div>
          <CardTitle className="text-2xl">重置链接已发送</CardTitle>
          <CardDescription>
            如果邮箱存在，重置链接已发送到您的邮箱
          </CardDescription>
        </CardHeader>
        <CardContent className="text-center">
          <p className="text-muted-foreground mb-6">
            请检查您的邮箱，点击重置链接设置新密码。如果未收到邮件，请检查垃圾邮件文件夹。
          </p>
          <div className="space-y-4">
            <Button asChild className="w-full">
              <Link href="/login">返回登录</Link>
            </Button>
            <Button
              variant="outline"
              className="w-full"
              onClick={() => setIsSubmitted(false)}
            >
              重新发送
            </Button>
          </div>
        </CardContent>
      </>
    )
  }

  return (
    <>
      <CardHeader className="text-center">
        <CardTitle className="text-2xl">重置密码</CardTitle>
        <CardDescription>
          输入您的邮箱地址，我们将发送重置链接
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>邮箱地址</FormLabel>
                  <FormControl>
                    <Input
                      type="email"
                      placeholder="请输入您的注册邮箱"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              发送重置链接
            </Button>
          </form>
        </Form>

        <div className="mt-6 text-center text-sm">
          <Link
            href="/login"
            className="text-primary font-medium hover:underline"
          >
            返回登录
          </Link>
        </div>
      </CardContent>
    </>
  )
}