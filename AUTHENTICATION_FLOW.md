# 认证授权流程设计

## 概述

本文档定义了用户管理系统的认证和授权流程。系统采用基于 JWT 的认证机制和基于角色的访问控制（RBAC），确保安全、灵活和可扩展的权限管理。

## 架构概览

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   客户端    │    │   FastAPI   │    │ PostgreSQL  │
│   (前端)    │    │   (后端)    │    │   (数据库)  │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                   │
       │ 1. 登录请求      │                   │
       ├─────────────────►│                   │
       │                  │ 2. 验证用户凭证   │
       │                  ├──────────────────►│
       │                  │                   │
       │                  │ 3. 返回用户数据   │
       │                  │◄──────────────────┤
       │                  │                   │
       │ 4. 返回JWT令牌   │                   │
       │◄─────────────────┤                   │
       │                  │                   │
       │ 5. 携带令牌请求  │                   │
       ├─────────────────►│                   │
       │                  │ 6. 验证令牌       │
       │                  │ 7. 检查权限       │
       │                  ├──────────────────►│
       │                  │                   │
       │                  │ 8. 返回资源       │
       │                  │◄──────────────────┤
       │ 9. 返回响应      │                   │
       │◄─────────────────┤                   │
       │                  │                   │
       │ 10. 令牌刷新请求 │                   │
       ├─────────────────►│                   │
       │                  │ 11. 验证刷新令牌  │
       │                  ├──────────────────►│
       │                  │                   │
       │                  │ 12. 返回新令牌    │
       │                  │◄──────────────────┤
       │ 13. 返回新令牌   │                   │
       │◄─────────────────┤                   │
└──────┴──────┘    └──────┴──────┘    └──────┴──────┘
```

## 认证流程

### 1. 用户注册流程

```
1. 用户填写注册表单
   ↓
2. 前端验证表单数据
   ↓
3. 发送注册请求到 /api/v1/auth/register
   ↓
4. 后端验证数据唯一性（用户名、邮箱）
   ↓
5. 创建用户记录（密码哈希存储）
   ↓
6. 分配默认角色（如 'user'）
   ↓
7. 发送邮箱验证邮件（异步）
   ↓
8. 返回注册成功响应
   ↓
9. 前端显示成功消息并重定向到登录页
```

### 2. 邮箱验证流程

```
1. 用户点击邮箱中的验证链接
   ↓
2. 链接包含验证令牌（JWT格式）
   ↓
3. 前端调用 /api/v1/auth/verify-email
   ↓
4. 后端验证令牌有效性和过期时间
   ↓
5. 更新用户验证状态为已验证
   ↓
6. 删除已使用的验证令牌
   ↓
7. 返回验证成功响应
   ↓
8. 前端显示验证成功页面
```

### 3. 用户登录流程

```
1. 用户输入用户名/邮箱和密码
   ↓
2. 前端发送登录请求到 /api/v1/auth/login
   ↓
3. 后端验证用户凭证：
   a. 查找用户（通过用户名或邮箱）
   b. 验证密码哈希
   c. 检查账户状态（是否激活、是否锁定）
   ↓
4. 如果验证失败：
   a. 记录登录失败尝试
   b. 达到阈值后锁定账户
   c. 返回错误响应
   ↓
5. 如果验证成功：
   a. 生成访问令牌（JWT，有效期30分钟）
   b. 生成刷新令牌（JWT，有效期7天）
   c. 创建用户会话记录
   d. 更新最后登录时间
   ↓
6. 返回令牌和用户信息
   ↓
7. 前端存储令牌（安全存储）
   ↓
8. 重定向到仪表板
```

### 4. 令牌刷新流程

```
1. 访问令牌过期（401错误）
   ↓
2. 前端检测到401错误
   ↓
3. 使用刷新令牌调用 /api/v1/auth/refresh
   ↓
4. 后端验证刷新令牌：
   a. 验证签名和有效期
   b. 检查令牌是否在撤销列表中
   c. 验证关联的用户会话
   ↓
5. 如果验证失败：
   a. 返回401错误
   b. 前端清除本地存储并重定向到登录页
   ↓
6. 如果验证成功：
   a. 生成新的访问令牌
   b. 可选生成新的刷新令牌（滚动刷新）
   c. 更新用户会话的最后活动时间
   ↓
7. 返回新令牌
   ↓
8. 前端更新本地存储的令牌
   ↓
9. 重试原始请求（自动或手动）
```

### 5. 用户登出流程

```
1. 用户点击登出按钮
   ↓
2. 前端发送登出请求到 /api/v1/auth/logout
   ↓
3. 后端：
   a. 验证访问令牌
   b. 将令牌加入撤销列表（可选）
   c. 删除用户会话记录
   ↓
4. 返回登出成功响应
   ↓
5. 前端清除本地存储的令牌
   ↓
6. 重定向到登录页
```

### 6. 密码重置流程

```
1. 用户点击"忘记密码"
   ↓
2. 输入邮箱地址
   ↓
3. 前端发送请求到 /api/v1/auth/forgot-password
   ↓
4. 后端：
   a. 查找用户（通过邮箱）
   b. 生成密码重置令牌（JWT，有效期1小时）
   c. 发送包含重置链接的邮件
   ↓
5. 返回成功响应（无论用户是否存在）
   ↓
6. 用户点击邮件中的重置链接
   ↓
7. 前端显示密码重置表单
   ↓
8. 用户输入新密码
   ↓
9. 前端发送请求到 /api/v1/auth/reset-password
   ↓
10. 后端：
    a. 验证重置令牌
    b. 更新用户密码（哈希存储）
    c. 使令牌失效
    d. 可选：终止用户的所有活跃会话
    ↓
11. 返回重置成功响应
    ↓
12. 前端显示成功消息并重定向到登录页
```

## 授权模型

### 1. RBAC（基于角色的访问控制）模型

```
用户 (User) ─── 属于 ───► 角色 (Role) ─── 拥有 ───► 权限 (Permission)
     │                          │                         │
     │                          │                         │
     │                   可以有多个                对应具体操作
     │                                              (资源 + 动作)
     │
可以属于多个角色
```

### 2. 权限粒度

权限格式：`{resource}.{action}`

**资源类型**:
- `users`: 用户管理
- `roles`: 角色管理
- `permissions`: 权限管理
- `audit_logs`: 审计日志
- `system`: 系统管理

**操作类型**:
- `create`: 创建资源
- `read`: 读取资源（单个）
- `update`: 更新资源
- `delete`: 删除资源
- `list`: 列出资源
- `manage`: 管理资源（包含所有操作）

**示例权限**:
- `users.create`: 创建用户
- `users.read`: 查看用户详情
- `users.update`: 更新用户信息
- `users.delete`: 删除用户
- `users.list`: 查看用户列表
- `users.manage_roles`: 管理用户角色
- `roles.create`: 创建角色
- `permissions.list`: 查看权限列表

### 3. 权限范围

- `global`: 全局权限（所有资源）
- `own`: 仅自己的资源
- `team`: 团队内的资源
- `department`: 部门内的资源

## 令牌设计

### 1. 访问令牌（Access Token）

**JWT 结构**:
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "550e8400-e29b-41d4-a716-446655440000",  // 用户ID
    "username": "john_doe",
    "email": "john@example.com",
    "roles": ["admin", "user"],
    "permissions": ["users.create", "users.read", "users.update"],
    "session_id": "880e8400-e29b-41d4-a716-446655440003",
    "iat": 1704067200,  // 签发时间
    "exp": 1704069000,  // 过期时间（30分钟后）
    "jti": "token_id_123456"  // 令牌唯一标识
  },
  "signature": "HMACSHA256(...)"
}
```

**特点**:
- 有效期短：30分钟
- 包含用户基本信息和权限
- 用于API访问认证
- 存储在客户端（安全存储）

### 2. 刷新令牌（Refresh Token）

**JWT 结构**:
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "550e8400-e29b-41d4-a716-446655440000",  // 用户ID
    "session_id": "880e8400-e29b-41d4-a716-446655440003",
    "device_fingerprint": "device_hash_123",
    "iat": 1704067200,  // 签发时间
    "exp": 1704672000,  // 过期时间（7天后）
    "jti": "refresh_token_id_123456"
  },
  "signature": "HMACSHA256(...)"
}
```

**特点**:
- 有效期长：7天
- 不包含权限信息
- 用于获取新的访问令牌
- 需要安全存储（HttpOnly Cookie）
- 可撤销（通过会话管理）

### 3. 令牌安全措施

**存储安全**:
- 访问令牌：内存存储或安全本地存储
- 刷新令牌：HttpOnly Cookie（防XSS）或安全存储

**传输安全**:
- 始终使用 HTTPS
- 避免 URL 参数传递令牌
- 使用 Authorization 头

**令牌撤销**:
- 登出时撤销令牌
- 密码更改时撤销所有令牌
- 可疑活动时撤销令牌
- 定期清理过期令牌

## 会话管理

### 1. 会话记录表结构

```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    session_token TEXT NOT NULL UNIQUE,
    refresh_token TEXT NOT NULL UNIQUE,
    device_info JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    revoked_at TIMESTAMP WITH TIME ZONE
);
```

### 2. 会话生命周期

```
1. 创建会话（登录时）
   - 生成唯一会话ID
   - 记录设备信息和IP
   - 设置过期时间

2. 活动会话（每次请求）
   - 更新最后活动时间
   - 验证会话未过期
   - 检查会话是否被撤销

3. 会话维护（定期任务）
   - 清理过期会话
   - 终止不活跃会话（30天无活动）
   - 同步会话状态到所有设备

4. 会话终止（登出或撤销）
   - 标记会话为已撤销
   - 通知所有相关服务
   - 清理相关资源
```

### 3. 并发会话管理

**策略选项**:
1. **单设备登录**: 新登录终止旧会话
2. **多设备登录**: 允许同时多个会话
3. **有限设备登录**: 限制最大会话数（如5个）

**实现方式**:
```python
class SessionManager:
    def create_session(self, user_id, device_info, ip_address):
        # 检查并发会话限制
        active_sessions = self.get_active_sessions(user_id)

        if self.MAX_SESSIONS_PER_USER and \
           len(active_sessions) >= self.MAX_SESSIONS_PER_USER:
            # 终止最旧的会话
            oldest_session = min(active_sessions, key=lambda s: s.last_activity_at)
            self.revoke_session(oldest_session.id)

        # 创建新会话
        session = UserSession(
            user_id=user_id,
            device_info=device_info,
            ip_address=ip_address,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        # ... 保存会话
```

## 安全防护

### 1. 密码安全

**哈希算法**: Argon2id（或 bcrypt）
**配置参数**:
- 时间成本：2
- 内存成本：64MB
- 并行度：2
- 盐值长度：16字节

**密码策略**:
- 最小长度：8字符
- 必须包含：大小写字母、数字、特殊字符
- 禁止常用密码
- 密码历史记录（防止重复使用）
- 定期强制更改（90天）

### 2. 账户锁定

**锁定条件**:
- 连续失败登录尝试：5次
- 锁定时间：15分钟（可递增）
- 锁定范围：按用户名+IP组合

**解锁方式**:
- 等待锁定时间结束
- 管理员手动解锁
- 密码重置解锁

### 3. 令牌安全

**防止令牌泄露**:
- 短有效期访问令牌
- 令牌绑定设备指纹
- 令牌绑定IP地址（可选）
- 令牌撤销列表

**防止令牌重用**:
- 一次性使用令牌（如密码重置）
- 令牌使用后立即失效
- 记录令牌使用历史

### 4. 速率限制

**保护端点**:
- 登录端点：10次/小时（每IP）
- 注册端点：5次/小时（每IP）
- 密码重置：3次/小时（每用户）
- API端点：1000次/小时（每用户）

**实现方式**:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/auth/login")
@limiter.limit("10/hour")
async def login(request: Request):
    # 登录逻辑
```

## OAuth2 集成

### 1. 支持的 OAuth2 提供商

- Google OAuth2
- GitHub OAuth2
- Microsoft Entra ID
- 微信登录
- 自定义 OAuth2 提供商

### 2. OAuth2 登录流程

```
1. 用户点击"通过Google登录"
   ↓
2. 重定向到Google授权页面
   ↓
3. 用户授权并返回授权码
   ↓
4. 后端使用授权码交换访问令牌
   ↓
5. 获取用户基本信息（邮箱、姓名等）
   ↓
6. 查找或创建本地用户
   ↓
7. 生成系统访问令牌
   ↓
8. 重定向回应用并设置令牌
```

### 3. OAuth2 用户映射

```python
class OAuth2UserMapper:
    def map_user(self, provider, oauth_user_data):
        # 查找现有用户
        user = self.find_user_by_oauth_id(provider, oauth_user_data.id)

        if not user:
            # 查找通过邮箱（如果提供商已验证邮箱）
            if oauth_user_data.verified_email:
                user = self.find_user_by_email(oauth_user_data.email)

            if not user:
                # 创建新用户
                user = self.create_user_from_oauth(provider, oauth_user_data)

        # 更新OAuth关联
        self.update_oauth_connection(user, provider, oauth_user_data)

        return user
```

## 多因素认证（MFA）

### 1. 支持的 MFA 方法

1. **TOTP（基于时间的一次性密码）**
   - 使用 Google Authenticator 或类似应用
   - 6位数字，30秒有效期

2. **短信验证码**
   - 通过短信发送6位验证码
   - 5分钟有效期

3. **邮箱验证码**
   - 通过邮箱发送6位验证码
   - 10分钟有效期

4. **安全密钥（WebAuthn）**
   - 硬件安全密钥或生物识别
   - FIDO2/WebAuthn 标准

### 2. MFA 启用流程

```
1. 用户登录后访问安全设置
   ↓
2. 选择启用MFA方法（如TOTP）
   ↓
3. 生成密钥并显示二维码
   ↓
4. 用户使用验证器应用扫描
   ↓
5. 输入验证码确认设置
   ↓
6. 保存恢复代码（紧急使用）
   ↓
7. MFA启用成功
```

### 3. MFA 验证流程

```
1. 用户使用用户名密码登录
   ↓
2. 检查用户是否启用MFA
   ↓
3. 如果启用MFA：
   a. 要求输入MFA验证码
   b. 验证TOTP代码或短信验证码
   c. 如果验证失败，记录尝试次数
   ↓
4. 如果验证成功：
   a. 生成访问令牌
   b. 标记此次登录已验证MFA
   ↓
5. 如果未启用MFA：直接生成令牌
```

## 审计和日志

### 1. 认证事件日志

**记录事件**:
- 用户注册
- 邮箱验证
- 登录成功/失败
- 令牌刷新
- 密码重置
- 账户锁定/解锁
- 会话创建/销毁
- MFA启用/禁用
- OAuth2登录

**日志字段**:
```json
{
  "event": "user_login",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "success": true,
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "device_fingerprint": "device_hash_123",
  "timestamp": "2024-01-01T10:30:00Z",
  "metadata": {
    "mfa_used": true,
    "mfa_method": "totp",
    "session_id": "880e8400-e29b-41d4-a716-446655440003"
  }
}
```

### 2. 可疑活动检测

**检测规则**:
- 短时间内多次登录失败
- 异常地理位置登录
- 新设备登录
- 异常时间登录（如凌晨3点）
- 多次密码重置请求

**响应动作**:
- 发送安全通知邮件
- 要求额外验证（MFA）
- 临时锁定账户
- 记录安全事件

## 前端集成

### 1. 令牌存储策略

```typescript
class TokenManager {
  // 存储访问令牌（安全存储）
  setAccessToken(token: string): void {
    // 使用内存存储或安全本地存储
    sessionStorage.setItem('access_token', token);
  }

  // 存储刷新令牌（更安全的方式）
  setRefreshToken(token: string): void {
    // 使用HttpOnly Cookie（后端设置）
    // 或安全本地存储
    localStorage.setItem('refresh_token', token);
  }

  // 获取令牌
  getAccessToken(): string | null {
    return sessionStorage.getItem('access_token');
  }

  // 清除令牌
  clearTokens(): void {
    sessionStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    // 通知后端撤销令牌
  }
}
```

### 2. 自动令牌刷新

```typescript
class AuthInterceptor {
  private isRefreshing = false;
  private failedQueue: Array<{
    resolve: (value: any) => void;
    reject: (reason?: any) => void;
  }> = [];

  intercept(request: AxiosRequestConfig): Promise<AxiosRequestConfig> {
    const token = tokenManager.getAccessToken();

    if (token) {
      request.headers.Authorization = `Bearer ${token}`;
    }

    return Promise.resolve(request);
  }

  handleError(error: AxiosError): Promise<any> {
    const originalRequest = error.config;

    // 如果是401错误且不是刷新令牌的请求
    if (error.response?.status === 401 &&
        !originalRequest.url?.includes('/auth/refresh')) {

      if (this.isRefreshing) {
        // 加入队列等待刷新完成
        return new Promise((resolve, reject) => {
          this.failedQueue.push({ resolve, reject });
        })
          .then(() => this.retryRequest(originalRequest))
          .catch((err) => Promise.reject(err));
      }

      this.isRefreshing = true;

      return authService.refreshToken()
        .then(({ access_token }) => {
          tokenManager.setAccessToken(access_token);

          // 重试所有失败的请求
          this.failedQueue.forEach((promise) => promise.resolve());
          this.failedQueue = [];

          return this.retryRequest(originalRequest);
        })
        .catch((refreshError) => {
          // 刷新失败，清理并重定向到登录页
          this.failedQueue.forEach((promise) => promise.reject(refreshError));
          this.failedQueue = [];

          tokenManager.clearTokens();
          window.location.href = '/login';

          return Promise.reject(refreshError);
        })
        .finally(() => {
          this.isRefreshing = false;
        });
    }

    return Promise.reject(error);
  }
}
```

### 3. 路由保护

```typescript
// 路由中间件（Next.js）
export function requireAuth(redirectTo = '/login') {
  return async (context: GetServerSidePropsContext) => {
    const token = context.req.cookies.access_token;

    if (!token) {
      return {
        redirect: {
          destination: redirectTo,
          permanent: false,
        },
      };
    }

    try {
      // 验证令牌有效性
      const user = await authService.verifyToken(token);

      return {
        props: { user },
      };
    } catch (error) {
      return {
        redirect: {
          destination: redirectTo,
          permanent: false,
        },
      };
    }
  };
}
```

## 测试策略

### 1. 单元测试

**测试覆盖**:
- 密码哈希验证
- 令牌生成和验证
- 权限检查逻辑
- 会话管理操作

**示例测试**:
```python
def test_password_hashing():
    password = "SecurePassword123!"
    hashed = hash_password(password)

    # 验证密码
    assert verify_password(password, hashed) == True
    assert verify_password("WrongPassword", hashed) == False

def test_token_generation():
    user = User(id=1, username="test")
    token = generate_access_token(user)

    # 验证令牌
    payload = verify_token(token)
    assert payload["sub"] == "1"
    assert payload["username"] == "test"
```

### 2. 集成测试

**测试场景**:
- 完整登录流程
- 令牌刷新流程
- 权限验证流程
- 并发会话管理
- OAuth2集成流程

**示例测试**:
```python
def test_login_flow(client, test_user):
    # 登录请求
    response = client.post("/auth/login", json={
        "username": test_user.username,
        "password": "test_password"
    })

    assert response.status_code == 200
    data = response.json()

    # 验证响应包含令牌
    assert "access_token" in data
    assert "refresh_token" in data
    assert "user" in data

    # 使用令牌访问受保护端点
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["username"] == test_user.username
```

### 3. 安全测试

**测试项目**:
- SQL注入防护
- XSS攻击防护
- CSRF防护
- 令牌安全测试
- 速率限制测试
- 密码策略测试

## 部署配置

### 1. 环境变量配置

```bash
# 认证配置
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# 密码安全
BCRYPT_ROUNDS=12
PASSWORD_MIN_LENGTH=8
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_MINUTES=15

# OAuth2 配置
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
GITHUB_OAUTH_CLIENT_ID=your-github-client-id
GITHUB_OAUTH_CLIENT_SECRET=your-github-client-secret

# 会话配置
SESSION_TIMEOUT_MINUTES=30
MAX_SESSIONS_PER_USER=5
ALLOW_CONCURRENT_SESSIONS=true

# 安全头
ENABLE_CSP=true
ENABLE_HSTS=true
ENABLE_XSS_PROTECTION=true
```

### 2. 安全头配置

```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.cors import CORSMiddleware

app.add_middleware(HTTPSRedirectMiddleware)  # 强制HTTPS
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["example.com"])  # 主机验证

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend.example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"]
)

# 安全头中间件
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    # 添加安全头
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # CSP头（内容安全策略）
    response.headers["Content-Security-Policy"] = \
        "default-src 'self'; " \
        "script-src 'self' 'unsafe-inline' https://cdn.example.com; " \
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; " \
        "img-src 'self' data: https://*.example.com; " \
        "font-src 'self' https://fonts.gstatic.com; " \
        "connect-src 'self' https://api.example.com;"

    return response
```

## 故障排除

### 常见问题及解决方案

1. **令牌无效或过期**
   - 检查令牌有效期
   - 验证令牌签名
   - 检查令牌是否被撤销

2. **权限不足**
   - 检查用户角色分配
   - 验证权限配置
   - 检查资源范围限制

3. **会话管理问题**
   - 检查会话过期时间
   - 验证并发会话限制
   - 清理过期会话

4. **OAuth2集成问题**
   - 检查提供商配置
   - 验证回调URL
   - 检查令牌交换流程

5. **性能问题**
   - 优化权限缓存
   - 减少数据库查询
   - 实现令牌黑名单缓存

---
*本文档是认证授权系统的权威参考，所有认证相关实现必须遵循此设计。架构变更需要更新此文档并通知相关团队。*