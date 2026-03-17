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

**仪表板布局 (app/(dashboard)/layout.tsx)**:


### 2. 认证系统

**认证提供者 (components/providers/auth-provider.tsx)**:

### 4. 表单处理



### 5. 数据表格组件



### 6. 路由保护中间件




## 开发指南

### 1. 本地开发


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