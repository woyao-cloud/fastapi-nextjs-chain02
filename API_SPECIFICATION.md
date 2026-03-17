# API 接口规范

## 概述

本文档定义了用户管理系统的 RESTful API 接口规范。所有 API 遵循 OpenAPI 3.0 标准，提供清晰、一致、可预测的接口设计。

## 设计原则

### 1. RESTful 设计
- **资源导向**: 所有端点对应具体资源
- **HTTP 方法语义**: GET(查询), POST(创建), PUT(全量更新), PATCH(部分更新), DELETE(删除)
- **状态码正确使用**: 2xx(成功), 4xx(客户端错误), 5xx(服务器错误)

### 2. 一致性原则
- **URL 格式**: `/api/v{version}/{resource}/{id}/{sub-resource}`
- **命名规范**: 使用小写字母和连字符 (`kebab-case`)
- **版本管理**: 所有 API 包含版本号，支持向后兼容

### 3. 安全性原则
- **HTTPS 强制**: 所有请求必须使用 HTTPS
- **认证授权**: 所有非公开端点需要认证和授权
- **输入验证**: 所有输入必须验证，防止注入攻击

### 4. 可发现性原则
- **文档完整**: 提供完整的 OpenAPI/Swagger 文档
- **错误信息明确**: 错误响应包含足够调试信息
- **链接关系**: 使用 HATEOAS 原则提供资源链接

## 基础规范

### 1. 请求头
```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer {access_token}
X-Request-ID: {request_id}  # 用于请求追踪
```

### 2. 响应格式

**成功响应 (2xx)**:
```json
{
  "data": {
    // 资源数据
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "req_123456",
    "page": 1,
    "per_page": 20,
    "total": 100
  },
  "links": {
    "self": "/api/v1/users/123",
    "related": {
      "roles": "/api/v1/users/123/roles"
    }
  }
}
```

**错误响应 (4xx/5xx)**:
```json
{
  "error": {
    "code": "validation_error",
    "message": "输入验证失败",
    "details": [
      {
        "field": "email",
        "message": "邮箱格式不正确"
      }
    ],
    "request_id": "req_123456",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

### 3. 分页和排序

**查询参数**:
- `page`: 页码 (默认: 1)
- `per_page`: 每页数量 (默认: 20, 最大: 100)
- `sort`: 排序字段 (默认: `created_at`)
- `order`: 排序方向 (`asc` 或 `desc`, 默认: `desc`)
- `q`: 搜索关键词

**分页响应**:
```json
{
  "data": [...],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8,
    "has_next": true,
    "has_previous": false
  },
  "links": {
    "self": "/api/v1/users?page=1&per_page=20",
    "first": "/api/v1/users?page=1&per_page=20",
    "prev": null,
    "next": "/api/v1/users?page=2&per_page=20",
    "last": "/api/v1/users?page=8&per_page=20"
  }
}
```

### 4. 错误码定义

| 状态码 | 错误码 | 描述 |
|--------|--------|------|
| 400 | `validation_error` | 输入验证失败 |
| 401 | `unauthorized` | 未认证或令牌无效 |
| 403 | `forbidden` | 权限不足 |
| 404 | `not_found` | 资源不存在 |
| 409 | `conflict` | 资源冲突（如重复创建） |
| 422 | `unprocessable_entity` | 业务逻辑验证失败 |
| 429 | `rate_limit_exceeded` | 请求频率超限 |
| 500 | `internal_server_error` | 服务器内部错误 |
| 503 | `service_unavailable` | 服务暂时不可用 |

## 认证 API

### 1. 用户登录

**POST** `/api/v1/auth/login`

**请求体**:
```json
{
  "username": "john_doe",
  "password": "SecurePassword123!",
  "remember_me": false
}
```

**成功响应 (200)**:
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "john_doe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "is_active": true,
      "is_verified": true,
      "last_login_at": "2024-01-01T10:30:00Z"
    }
  }
}
```

**错误响应**:
- `400`: 用户名或密码错误
- `423`: 账户被锁定
- `429`: 登录尝试次数过多

### 2. 令牌刷新

**POST** `/api/v1/auth/refresh`

**请求体**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**成功响应 (200)**:
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### 3. 用户登出

**POST** `/api/v1/auth/logout`

**请求头**:
```http
Authorization: Bearer {access_token}
```

**成功响应 (204)**: 无内容

### 4. 获取当前用户

**GET** `/api/v1/auth/me`

**请求头**:
```http
Authorization: Bearer {access_token}
```

**成功响应 (200)**:
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "avatar_url": "https://example.com/avatars/john.jpg",
    "phone_number": "+8613800138000",
    "timezone": "Asia/Shanghai",
    "locale": "zh-CN",
    "is_active": true,
    "is_verified": true,
    "is_superuser": false,
    "last_login_at": "2024-01-01T10:30:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "roles": [
      {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "name": "admin",
        "description": "管理员"
      }
    ],
    "permissions": [
      "users.create",
      "users.read",
      "users.update",
      "users.delete"
    ]
  }
}
```

### 5. 用户注册

**POST** `/api/v1/auth/register`

**请求体**:
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+8613800138000"
}
```

**成功响应 (201)**:
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "is_verified": false,
    "created_at": "2024-01-01T00:00:00Z"
  },
  "meta": {
    "message": "注册成功，请查收邮箱验证邮件"
  }
}
```

### 6. 邮箱验证

**POST** `/api/v1/auth/verify-email`

**请求体**:
```json
{
  "token": "verification_token_123456"
}
```

**成功响应 (200)**:
```json
{
  "data": {
    "verified": true
  },
  "meta": {
    "message": "邮箱验证成功"
  }
}
```

### 7. 密码重置请求

**POST** `/api/v1/auth/forgot-password`

**请求体**:
```json
{
  "email": "john@example.com"
}
```

**成功响应 (202)**:
```json
{
  "data": null,
  "meta": {
    "message": "如果邮箱存在，重置链接已发送"
  }
}
```

### 8. 密码重置确认

**POST** `/api/v1/auth/reset-password`

**请求体**:
```json
{
  "token": "reset_token_123456",
  "new_password": "NewSecurePassword123!"
}
```

**成功响应 (200)**:
```json
{
  "data": null,
  "meta": {
    "message": "密码重置成功"
  }
}
```

## 用户管理 API

### 1. 获取用户列表

**GET** `/api/v1/users`

**查询参数**:
- `page` (默认: 1)
- `per_page` (默认: 20, 最大: 100)
- `search`: 搜索关键词（用户名、邮箱、姓名）
- `is_active`: 过滤激活状态
- `is_verified`: 过滤验证状态
- `role_id`: 按角色过滤
- `sort` (默认: `created_at`)
- `order` (默认: `desc`)

**成功响应 (200)**:
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "john_doe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "is_active": true,
      "is_verified": true,
      "last_login_at": "2024-01-01T10:30:00Z",
      "created_at": "2024-01-01T00:00:00Z",
      "roles": [
        {
          "id": "660e8400-e29b-41d4-a716-446655440001",
          "name": "admin",
          "description": "管理员"
        }
      ]
    }
  ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8
  },
  "links": {
    "self": "/api/v1/users?page=1&per_page=20",
    "next": "/api/v1/users?page=2&per_page=20",
    "last": "/api/v1/users?page=8&per_page=20"
  }
}
```

**所需权限**: `users.list`

### 2. 创建用户

**POST** `/api/v1/users`

**请求体**:
```json
{
  "username": "jane_doe",
  "email": "jane@example.com",
  "password": "SecurePassword123!",
  "first_name": "Jane",
  "last_name": "Doe",
  "phone_number": "+8613800138001",
  "timezone": "Asia/Shanghai",
  "locale": "zh-CN",
  "is_active": true,
  "role_ids": ["660e8400-e29b-41d4-a716-446655440001"]
}
```

**成功响应 (201)**:
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "username": "jane_doe",
    "email": "jane@example.com",
    "first_name": "Jane",
    "last_name": "Doe",
    "is_active": true,
    "is_verified": false,
    "created_at": "2024-01-01T00:00:00Z"
  },
  "links": {
    "self": "/api/v1/users/550e8400-e29b-41d4-a716-446655440001"
  }
}
```

**所需权限**: `users.create`

### 3. 获取单个用户

**GET** `/api/v1/users/{user_id}`

**路径参数**:
- `user_id`: 用户 UUID

**成功响应 (200)**:
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "avatar_url": "https://example.com/avatars/john.jpg",
    "phone_number": "+8613800138000",
    "timezone": "Asia/Shanghai",
    "locale": "zh-CN",
    "is_active": true,
    "is_verified": true,
    "is_superuser": false,
    "last_login_at": "2024-01-01T10:30:00Z",
    "failed_login_attempts": 0,
    "locked_until": null,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "roles": [
      {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "name": "admin",
        "description": "管理员"
      }
    ],
    "permissions": [
      "users.create",
      "users.read",
      "users.update",
      "users.delete"
    ]
  },
  "links": {
    "self": "/api/v1/users/550e8400-e29b-41d4-a716-446655440000",
    "roles": "/api/v1/users/550e8400-e29b-41d4-a716-446655440000/roles",
    "sessions": "/api/v1/users/550e8400-e29b-41d4-a716-446655440000/sessions"
  }
}
```

**所需权限**: `users.read` 或自己的用户信息

### 4. 更新用户

**PUT** `/api/v1/users/{user_id}`

**路径参数**:
- `user_id`: 用户 UUID

**请求体**:
```json
{
  "first_name": "Johnathan",
  "last_name": "Doe",
  "phone_number": "+8613800138002",
  "timezone": "America/New_York",
  "locale": "en-US",
  "is_active": true
}
```

**成功响应 (200)**:
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "Johnathan",
    "last_name": "Doe",
    "phone_number": "+8613800138002",
    "timezone": "America/New_York",
    "locale": "en-US",
    "is_active": true,
    "is_verified": true,
    "updated_at": "2024-01-01T11:00:00Z"
  }
}
```

**所需权限**: `users.update` 或更新自己的用户信息

### 5. 部分更新用户

**PATCH** `/api/v1/users/{user_id}`

**路径参数**:
- `user_id`: 用户 UUID

**请求体**:
```json
{
  "is_active": false
}
```

**成功响应 (200)**:
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "is_active": false,
    "updated_at": "2024-01-01T11:30:00Z"
  }
}
```

**所需权限**: `users.update`

### 6. 删除用户

**DELETE** `/api/v1/users/{user_id}`

**路径参数**:
- `user_id`: 用户 UUID

**成功响应 (204)**: 无内容

**所需权限**: `users.delete`

### 7. 获取用户角色

**GET** `/api/v1/users/{user_id}/roles`

**路径参数**:
- `user_id`: 用户 UUID

**成功响应 (200)**:
```json
{
  "data": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "name": "admin",
      "description": "管理员",
      "assigned_at": "2024-01-01T10:00:00Z",
      "assigned_by": {
        "id": "770e8400-e29b-41d4-a716-446655440002",
        "username": "system"
      }
    }
  ]
}
```

**所需权限**: `users.read` 或自己的用户信息

### 8. 分配用户角色

**POST** `/api/v1/users/{user_id}/roles`

**路径参数**:
- `user_id`: 用户 UUID

**请求体**:
```json
{
  "role_id": "660e8400-e29b-41d4-a716-446655440001",
  "expires_at": "2025-01-01T00:00:00Z"  // 可选
}
```

**成功响应 (201)**:
```json
{
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "role_id": "660e8400-e29b-41d4-a716-446655440001",
    "assigned_at": "2024-01-01T12:00:00Z",
    "expires_at": "2025-01-01T00:00:00Z"
  }
}
```

**所需权限**: `users.manage_roles`

### 9. 移除用户角色

**DELETE** `/api/v1/users/{user_id}/roles/{role_id}`

**路径参数**:
- `user_id`: 用户 UUID
- `role_id`: 角色 UUID

**成功响应 (204)**: 无内容

**所需权限**: `users.manage_roles`

### 10. 获取用户会话

**GET** `/api/v1/users/{user_id}/sessions`

**路径参数**:
- `user_id`: 用户 UUID

**成功响应 (200)**:
```json
{
  "data": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "device_info": {
        "browser": "Chrome",
        "os": "Windows 10",
        "device": "Desktop"
      },
      "ip_address": "192.168.1.100",
      "last_activity_at": "2024-01-01T10:30:00Z",
      "created_at": "2024-01-01T10:00:00Z",
      "expires_at": "2024-01-08T10:00:00Z"
    }
  ]
}
```

**所需权限**: `users.read_sessions` 或查看自己的会话

### 11. 终止用户会话

**DELETE** `/api/v1/users/{user_id}/sessions/{session_id}`

**路径参数**:
- `user_id`: 用户 UUID
- `session_id`: 会话 UUID

**成功响应 (204)**: 无内容

**所需权限**: `users.manage_sessions` 或终止自己的会话

## 角色管理 API

### 1. 获取角色列表

**GET** `/api/v1/roles`

**查询参数**:
- `page` (默认: 1)
- `per_page` (默认: 20, 最大: 100)
- `search`: 搜索关键词
- `is_system`: 过滤系统角色
- `sort` (默认: `weight`)
- `order` (默认: `desc`)

**所需权限**: `roles.list`

### 2. 创建角色

**POST** `/api/v1/roles`

**请求体**:
```json
{
  "name": "moderator",
  "description": "内容审核员",
  "is_default": false,
  "weight": 500,
  "permission_ids": [
    "770e8400-e29b-41d4-a716-446655440004",
    "770e8400-e29b-41d4-a716-446655440005"
  ]
}
```

**所需权限**: `roles.create`

### 3. 获取单个角色

**GET** `/api/v1/roles/{role_id}`

**所需权限**: `roles.read`

### 4. 更新角色

**PUT** `/api/v1/roles/{role_id}`

**所需权限**: `roles.update`

### 5. 删除角色

**DELETE** `/api/v1/roles/{role_id}`

**所需权限**: `roles.delete`（不能删除系统角色）

### 6. 获取角色权限

**GET** `/api/v1/roles/{role_id}/permissions`

**所需权限**: `roles.read`

### 7. 分配角色权限

**POST** `/api/v1/roles/{role_id}/permissions`

**请求体**:
```json
{
  "permission_id": "770e8400-e29b-41d4-a716-446655440006"
}
```

**所需权限**: `roles.manage_permissions`

### 8. 移除角色权限

**DELETE** `/api/v1/roles/{role_id}/permissions/{permission_id}`

**所需权限**: `roles.manage_permissions`

## 权限管理 API

### 1. 获取权限列表

**GET** `/api/v1/permissions`

**查询参数**:
- `resource`: 按资源过滤
- `action`: 按操作过滤
- `scope`: 按范围过滤

**所需权限**: `permissions.list`

### 2. 创建权限

**POST** `/api/v1/permissions`

**请求体**:
```json
{
  "name": "users.export",
  "description": "导出用户数据",
  "resource": "users",
  "action": "export",
  "scope": "global"
}
```

**所需权限**: `permissions.create`

### 3. 获取单个权限

**GET** `/api/v1/permissions/{permission_id}`

**所需权限**: `permissions.read`

### 4. 更新权限

**PUT** `/api/v1/permissions/{permission_id}`

**所需权限**: `permissions.update`

### 5. 删除权限

**DELETE** `/api/v1/permissions/{permission_id}`

**所需权限**: `permissions.delete`

## 审计日志 API

### 1. 获取审计日志

**GET** `/api/v1/audit-logs`

**查询参数**:
- `user_id`: 按用户过滤
- `resource_type`: 按资源类型过滤
- `resource_id`: 按资源ID过滤
- `action`: 按操作过滤
- `start_date`: 开始日期
- `end_date`: 结束日期
- `page` (默认: 1)
- `per_page` (默认: 50, 最大: 200)

**所需权限**: `audit_logs.list`

### 2. 获取单个审计日志

**GET** `/api/v1/audit-logs/{log_id}`

**所需权限**: `audit_logs.read`

## 系统健康 API

### 1. 健康检查

**GET** `/api/v1/health`

**成功响应 (200)**:
```json
{
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-01T00:00:00Z",
    "services": {
      "database": {
        "status": "connected",
        "latency_ms": 12.5
      },
      "redis": {
        "status": "connected",
        "latency_ms": 2.1
      },
      "cache": {
        "status": "operational"
      }
    },
    "metrics": {
      "uptime_seconds": 86400,
      "memory_usage_mb": 256.5,
      "active_connections": 42
    }
  }
}
```

### 2. 就绪检查

**GET** `/api/v1/health/ready`

**成功响应 (200)**:
```json
{
  "data": {
    "status": "ready",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

### 3. 存活检查

**GET** `/api/v1/health/live`

**成功响应 (200)**:
```json
{
  "data": {
    "status": "alive",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## WebSocket API

### 1. 实时通知

**WebSocket** `/api/v1/ws/notifications`

**连接参数**:
- `token`: 访问令牌（查询参数）

**消息格式**:
```json
{
  "type": "notification",
  "data": {
    "id": "990e8400-e29b-41d4-a716-446655440007",
    "title": "新用户注册",
    "message": "用户 jane_doe 已注册",
    "level": "info",
    "created_at": "2024-01-01T12:00:00Z",
    "read": false
  }
}
```

## 文件上传 API

### 1. 上传用户头像

**POST** `/api/v1/users/{user_id}/avatar`

**Content-Type**: `multipart/form-data`

**表单数据**:
- `file`: 图片文件（JPG, PNG, WebP, 最大 5MB）

**成功响应 (200)**:
```json
{
  "data": {
    "url": "https://storage.example.com/avatars/550e8400-e29b-41d4-a716-446655440000.jpg",
    "size": 123456,
    "mime_type": "image/jpeg",
    "dimensions": {
      "width": 400,
      "height": 400
    }
  }
}
```

**所需权限**: `users.update` 或更新自己的头像

## OpenAPI 配置

### Swagger UI 访问
- **开发环境**: `http://localhost:8000/docs`
- **生产环境**: `/docs`（需要认证）

### ReDoc 访问
- **开发环境**: `http://localhost:8000/redoc`
- **生产环境**: `/redoc`（需要认证）

### OpenAPI 规范导出
- **JSON 格式**: `/openapi.json`
- **YAML 格式**: `/openapi.yaml`

## 版本管理策略

### 1. 版本号格式
- API 版本: `v1`, `v2`, `v3`
- URL 中包含版本: `/api/v1/resource`
- 默认版本: `v1`

### 2. 向后兼容性
- 不删除现有端点，只标记为废弃
- 不修改现有端点的响应结构
- 新功能添加新端点或新版本

### 3. 废弃策略
- 端点废弃后继续工作至少 6 个月
- 废弃端点返回 `Deprecation` 头
- 文档中明确标记废弃日期

## 速率限制

### 1. 限制规则
- 认证用户: 1000 请求/小时
- 未认证用户: 100 请求/小时
- 登录端点: 10 请求/小时（每 IP）
- 注册端点: 5 请求/小时（每 IP）

### 2. 响应头
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1704067200
Retry-After: 60  # 当超出限制时
```

## 数据格式标准

### 1. 日期时间
- 格式: ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`)
- 时区: UTC
- 示例: `2024-01-01T00:00:00Z`

### 2. UUID
- 格式: 标准 UUID v4
- 示例: `550e8400-e29b-41d4-a716-446655440000`

### 3. 枚举值
- 使用小写字母和连字符
- 示例: `active`, `inactive`, `pending`

### 4. 分页
- 页码从 1 开始
- 每页默认 20 条，最大 100 条
- 支持游标分页（用于无限滚动）

## 错误处理示例

### 1. 验证错误
```json
{
  "error": {
    "code": "validation_error",
    "message": "输入验证失败",
    "details": [
      {
        "field": "email",
        "message": "邮箱格式不正确",
        "code": "invalid_email"
      },
      {
        "field": "password",
        "message": "密码必须至少8个字符",
        "code": "password_too_short"
      }
    ]
  }
}
```

### 2. 权限错误
```json
{
  "error": {
    "code": "forbidden",
    "message": "权限不足",
    "details": "需要权限: users.create"
  }
}
```

### 3. 资源不存在
```json
{
  "error": {
    "code": "not_found",
    "message": "用户不存在",
    "details": "ID: 550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### 4. 业务逻辑错误
```json
{
  "error": {
    "code": "unprocessable_entity",
    "message": "无法删除自己",
    "details": "管理员不能删除自己的账户"
  }
}
```

---
*本文档是 API 接口的权威参考，所有 API 实现必须遵循此规范。API 变更需要更新此文档并通知相关团队。*