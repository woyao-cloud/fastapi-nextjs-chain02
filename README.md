前端代码生成实施计划                                                                           │
│                                                                                                │
│ 上下文                                                                                         │
│                                                                                                │
│ 用户请求"代码生成前端代码"，这是一个全栈用户管理系统项目，采用FastAPI后端和Next.js前端。前端代 │
│ 码已有基础结构（布局、页面、部分组件），但缺失大量关键组件、API客户端、认证系统和状态管理等。  │
│ 现有代码已直接引用许多不存在的组件，导致编译失败。                                             │
│                                                                                                │
│ 问题：前端项目无法编译和运行，缺失约50个关键文件。                                             │
│ 目标：生成完整的前端代码，实现用户管理系统的所有功能。                                         │
│ 约束：遵循FRONTEND_ARCHITECTURE.md架构，使用TypeScript严格模式，保持与现有代码风格一致。       │
│                                                                                                │
│ 推荐方法                                                                                       │
│                                                                                                │
│ 采用分阶段实施策略，按优先级创建文件，确保每阶段完成后项目部分功能可运行。                     │
│                                                                                                │
│ 阶段一：基础架构搭建（优先级：最高）                                                           │
│                                                                                                │
│ 目标：解决编译错误，使应用能正常启动。                                                         │
│                                                                                                │
│ 关键文件：                                                                                     │
│ 1. frontend/components/providers/theme-provider.tsx - layout.tsx直接引用                       │
│ 2. frontend/components/providers/auth-provider.tsx - layout.tsx直接引用                        │
│ 3. frontend/components/ui/toaster.tsx - layout.tsx直接引用                                     │
│ 4. frontend/components/ui/input.tsx - login/page.tsx直接引用                                   │
│ 5. frontend/components/ui/checkbox.tsx - login/page.tsx直接引用                                │
│ 6. frontend/hooks/use-toast.ts - login/page.tsx直接引用                                        │
│ 7. frontend/lib/api/client.ts - 所有API调用的基础                                              │
│ 8. frontend/lib/api/auth.ts - login/page.tsx直接引用                                           │
│                                                                                                │
│ 验证：npm run type-check通过，npm run dev能正常启动，首页可访问。                              │
│                                                                                                │
│ 阶段二：认证系统完善（优先级：高）                                                             │
│                                                                                                │
│ 目标：实现完整的用户认证流程。                                                                 │
│                                                                                                │
│ 关键文件：                                                                                     │
│ 1. frontend/lib/auth/require-auth.ts - dashboard/layout.tsx直接引用                            │
│ 2. frontend/middleware.ts - 路由保护                                                           │
│ 3. frontend/stores/auth-store.ts - 认证状态管理                                                │
│ 4. frontend/hooks/use-auth.ts - 认证Hook                                                       │
│ 5. frontend/lib/schemas/auth.ts - 认证表单验证                                                 │
│ 6. frontend/types/auth.ts - 认证类型定义                                                       │
│                                                                                                │
│ 验证：登录/注册功能正常工作，仪表板访问需要认证，未认证用户重定向到登录页。                    │
│                                                                                                │
│ 阶段三：仪表板核心功能（优先级：高）                                                           │
│                                                                                                │
│ 目标：实现仪表板基本布局和导航。                                                               │
│                                                                                                │
│ 关键文件：                                                                                     │
│ 1. frontend/components/layout/dashboard-nav.tsx - dashboard/layout.tsx直接引用                 │
│ 2. frontend/components/layout/header.tsx - dashboard/layout.tsx直接引用                        │
│ 3. frontend/app/(dashboard)/page.tsx - 仪表板主页                                              │
│ 4. frontend/components/data-display/data-table.tsx - 通用表格组件                              │
│                                                                                                │
│ 验证：仪表板能正常访问，导航菜单工作，主页显示基本统计信息。                                   │
│                                                                                                │
│ 阶段四：用户管理功能（优先级：中）                                                             │
│                                                                                                │
│ 目标：实现完整的用户CRUD操作。                                                                 │
│                                                                                                │
│ 关键文件：                                                                                     │
│ 1. frontend/lib/api/users.ts - 用户API                                                         │
│ 2. frontend/types/user.ts - 用户类型定义                                                       │
│ 3. frontend/app/(dashboard)/users/page.tsx - 用户列表页                                        │
│ 4. frontend/components/data-display/user-table.tsx - 用户表格组件                              │
│ 5. frontend/components/forms/user-form.tsx - 用户表单组件                                      │
│ 6. frontend/app/(dashboard)/users/[id]/page.tsx - 用户详情页                                   │
│ 7. frontend/app/(dashboard)/users/new/page.tsx - 创建用户页                                    │
│                                                                                                │
│ 验证：用户列表能查看、搜索、分页，能创建/编辑/删除用户。                                       │
│                                                                                                │
│ 阶段五：角色管理和其他功能（优先级：低）                                                       │
│                                                                                                │
│ 目标：完善系统功能，添加角色管理和个人资料。                                                   │
│                                                                                                │
│ 关键文件：                                                                                     │
│ 1. frontend/lib/api/roles.ts - 角色API                                                         │
│ 2. frontend/types/role.ts - 角色类型定义                                                       │
│ 3. frontend/app/(dashboard)/roles/page.tsx - 角色管理页                                        │
│ 4. frontend/app/(dashboard)/profile/page.tsx - 个人资料页                                      │
│ 5. frontend/components/ui/theme-toggle.tsx - 主题切换组件                                      │
│                                                                                                │
│ 验证：角色管理功能完整，个人资料可编辑，主题切换正常工作。                                     │
│                                                                                                │
│ 实施细节                                                                                       │
│                                                                                                │
│ 代码重用                                                                                       │
│                                                                                                │
│ - 现有组件模式：参考frontend/components/ui/button.tsx、card.tsx、form.tsx的代码风格            │
│ - 工具函数：使用frontend/lib/utils.ts中的现有工具                                              │
│ - 样式系统：遵循现有Tailwind CSS类命名约定                                                     │
│                                                                                                │
│ 架构遵循                                                                                       │
│                                                                                                │
│ - 组件化设计：Atomic Design原则（原子、分子、组织、模板、页面）                                │
│ - 类型安全：所有API响应都有TypeScript类型定义，使用Zod进行运行时验证                           │
│ - 状态管理：使用Zustand进行客户端状态管理                                                      │
│ - API集成：统一API客户端包含拦截器、错误处理和自动令牌刷新                                     │
│                                                                                                │
│ 关键决策                                                                                       │
│                                                                                                │
│ 1. 认证策略：使用JWT令牌，存储在localStorage，通过axios拦截器自动附加到请求                    │
│ 2. 路由保护：使用Next.js中间件进行页面级保护，组件级使用require-auth工具                       │
│ 3. 表单处理：React Hook Form + Zod验证，统一错误处理                                           │
│ 4. 数据表格：使用@tanstack/react-table实现功能丰富的表格组件                                   │
│ 5. 主题系统：使用next-themes实现light/dark主题切换                                             │
│                                                                                                │
│ 验证计划                                                                                       │
│                                                                                                │
│ 每阶段验证                                                                                     │
│                                                                                                │
│ 1. 编译检查：npm run type-check确保无TypeScript错误                                            │
│ 2. 构建检查：npm run build-check确保可成功构建                                                 │
│ 3. 运行检查：npm run dev确保应用正常启动                                                       │
│ 4. 功能检查：手动测试核心功能流程                                                              │
│                                                                                                │
│ 最终验收标准                                                                                   │
│                                                                                                │
│ - ✅ 用户能注册、登录、退出                                                                    │
│ - ✅ 仪表板能正常访问和导航                                                                    │
│ - ✅ 用户列表能查看、搜索、分页                                                                │
│ - ✅ 能创建、编辑、删除用户                                                                    │
│ - ✅ 能管理用户角色和权限                                                                      │
│ - ✅ 支持light/dark主题切换                                                                    │
│ - ✅ TypeScript编译无错误                                                                      │
│ - ✅ Next.js构建成功                                                                           │
│ - ✅ 代码符合ESLint规则                                                                        │
│                                                                                                │
│ 风险与缓解                                                                                     │
│                                                                                                │
│ 技术风险                                                                                       │
│                                                                                                │
│ 1. API兼容性：前端API调用需与后端API规范匹配                                                   │
│   - 缓解：仔细阅读API_SPECIFICATION.md，创建准确的类型定义                                     │
│ 2. 认证状态同步：客户端认证状态管理复杂                                                        │
│   - 缓解：使用React Context + localStorage，实现令牌自动刷新                                   │
│ 3. CORS问题：跨域请求可能被阻止                                                                │
│   - 缓解：配置正确的CORS头，使用环境变量配置API地址                                            │
│                                                                                                │
│ 开发风险                                                                                       │
│                                                                                                │
│ 1. 组件依赖关系：创建顺序错误可能导致编译失败                                                  │
│   - 缓解：严格按照上述优先级顺序创建文件                                                       │
│ 2. 样式一致性：确保所有组件使用一致样式                                                        │
│   - 缓解：参考现有组件样式，使用设计系统token                                                  │
│                                                                                                │
│ 工作量估计                                                                                     │
│                                                                                                │
│ - 阶段一：2-3小时                                                                              │
│ - 阶段二：3-4小时                                                                              │
│ - 阶段三：3-4小时                                                                              │
│ - 阶段四：4-5小时                                                                              │
│ - 阶段五：3-4小时                                                                              │
│ - 总计：约15-20小时                                                                            │
│                                                                                                │
│ 下一步                                                                                         │
│                                                                                                │
│ 开始实施阶段一，创建缺失的Provider和UI组件，解决编译错误。                    
