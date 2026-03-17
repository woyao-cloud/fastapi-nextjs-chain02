# 测试策略文档

## 概述

本文档定义了全栈用户管理系统的测试策略。我们采用测试金字塔模型，结合多种测试类型，确保软件质量、可靠性和可维护性。测试覆盖从单元测试到端到端测试的全方位验证。

## 测试金字塔

```
        ┌─────────────────┐
        │  端到端测试      │  ~10%
        │  (E2E Tests)    │
        └─────────────────┘
               │
        ┌─────────────────┐
        │  集成测试        │  ~20%
        │  (Integration)  │
        └─────────────────┘
               │
        ┌─────────────────┐
        │  单元测试        │  ~70%
        │  (Unit Tests)   │
        └─────────────────┘
```

**测试分布目标**:
- 单元测试: 70% - 快速、独立、细粒度
- 集成测试: 20% - 验证组件交互
- 端到端测试: 10% - 验证完整用户流程

## 测试工具栈

### 后端测试工具
- **测试框架**: pytest
- **HTTP 测试**: pytest-asyncio, httpx
- **数据库测试**: pytest-postgresql, factory-boy
- **覆盖率**: pytest-cov
- **Mock**: unittest.mock, pytest-mock
- **性能测试**: locust, pytest-benchmark

### 前端测试工具
- **测试框架**: Jest
- **组件测试**: React Testing Library
- **E2E 测试**: Playwright
- **快照测试**: Jest snapshot
- **覆盖率**: Jest --coverage
- **Mock**: MSW (Mock Service Worker)

### API 测试工具
- **API 测试**: Postman, Newman
- **契约测试**: Pact
- **性能测试**: k6
- **安全测试**: OWASP ZAP

### 质量检查工具
- **代码质量**: Black, isort, flake8, mypy
- **安全扫描**: Bandit, Safety, npm audit
- **依赖检查**: dependabot, renovate

## 测试目录结构

### 后端测试结构
```
backend/tests/
├── unit/                    # 单元测试
│   ├── core/               # 核心模块测试
│   │   ├── test_security.py
│   │   ├── test_auth.py
│   │   └── test_permissions.py
│   ├── application/        # 应用服务测试
│   │   ├── test_user_service.py
│   │   ├── test_auth_service.py
│   │   └── test_role_service.py
│   ├── domain/             # 领域模型测试
│   │   ├── test_user_entity.py
│   │   └── test_value_objects.py
│   └── utils/              # 工具函数测试
│       ├── test_validators.py
│       └── test_pagination.py
├── integration/            # 集成测试
│   ├── api/               # API 集成测试
│   │   ├── test_auth_api.py
│   │   ├── test_users_api.py
│   │   └── test_roles_api.py
│   ├── database/          # 数据库集成测试
│   │   ├── test_repositories.py
│   │   └── test_migrations.py
│   └── external/          # 外部服务集成测试
│       ├── test_email_service.py
│       └── test_cache_service.py
├── e2e/                   # 端到端测试
│   ├── test_auth_flow.py
│   ├── test_user_management.py
│   └── test_role_permission_flow.py
├── performance/           # 性能测试
│   ├── test_api_performance.py
│   └── locustfile.py
├── security/              # 安全测试
│   ├── test_auth_security.py
│   └── test_input_validation.py
├── fixtures/              # 测试夹具
│   ├── users.py
│   ├── roles.py
│   └── factories.py
└── conftest.py            # 测试配置
```

### 前端测试结构
```
frontend/tests/
├── unit/                    # 单元测试
│   ├── components/         # 组件测试
│   │   ├── ui/            # UI 组件测试
│   │   │   ├── Button.test.tsx
│   │   │   └── Input.test.tsx
│   │   ├── forms/         # 表单组件测试
│   │   │   ├── LoginForm.test.tsx
│   │   │   └── UserForm.test.tsx
│   │   └── layout/        # 布局组件测试
│   │       ├── Header.test.tsx
│   │       └── Sidebar.test.tsx
│   ├── hooks/             # Hook 测试
│   │   ├── useAuth.test.ts
│   │   ├── useApi.test.ts
│   │   └── usePermissions.test.ts
│   ├── utils/             # 工具函数测试
│   │   ├── validators.test.ts
│   │   └── formatters.test.ts
│   └── stores/            # 状态管理测试
│       ├── authStore.test.ts
│       └── userStore.test.ts
├── integration/           # 集成测试
│   ├── api/              # API 集成测试
│   │   ├── authApi.test.ts
│   │   └── usersApi.test.ts
│   ├── pages/            # 页面集成测试
│   │   ├── login.test.tsx
│   │   └── dashboard.test.tsx
│   └── workflows/        # 工作流测试
│       ├── authWorkflow.test.tsx
│       └── userManagementWorkflow.test.tsx
├── e2e/                  # 端到端测试
│   ├── auth/             # 认证流程
│   │   ├── login.spec.ts
│   │   ├── register.spec.ts
│   │   └── logout.spec.ts
│   ├── users/            # 用户管理
│   │   ├── userList.spec.ts
│   │   ├── userCreate.spec.ts
│   │   └── userEdit.spec.ts
│   ├── roles/            # 角色管理
│   │   ├── roleList.spec.ts
│   │   └── roleAssign.spec.ts
│   └── profile/          # 个人资料
│       └── profileEdit.spec.ts
├── __mocks__/            # Mock 文件
│   ├── fileMock.js
│   └── styleMock.js
├── setup/                # 测试设置
│   ├── test-utils.tsx
│   ├── jest.setup.ts
│   └── playwright.setup.ts
└── jest.config.js        # Jest 配置
```

## 单元测试策略

### 1. 后端单元测试

**测试范围**:
- 领域实体和值对象
- 应用服务逻辑
- 工具函数和验证器
- 核心算法和业务规则

**测试原则**:
- 每个测试只测试一个功能点
- 使用 Mock 隔离外部依赖
- 测试边界条件和异常情况
- 测试应该快速执行（< 100ms）

**示例测试**:
```python
# tests/unit/core/test_security.py
import pytest
from app.core.security import hash_password, verify_password, create_access_token

def test_password_hashing():
    """测试密码哈希和验证"""
    password = "SecurePassword123!"
    hashed = hash_password(password)

    # 验证正确密码
    assert verify_password(password, hashed) is True

    # 验证错误密码
    assert verify_password("WrongPassword", hashed) is False

    # 验证空密码
    with pytest.raises(ValueError):
        hash_password("")

def test_access_token_creation():
    """测试访问令牌创建"""
    user_data = {
        "sub": "user123",
        "username": "testuser",
        "roles": ["user"]
    }

    token = create_access_token(user_data)

    # 验证令牌格式
    assert isinstance(token, str)
    assert len(token) > 100

    # 验证令牌可以解码
    payload = verify_token(token)
    assert payload["sub"] == "user123"
    assert payload["username"] == "testuser"

def test_token_expiration():
    """测试令牌过期"""
    user_data = {"sub": "user123"}

    # 创建短期令牌
    token = create_access_token(user_data, expires_delta=timedelta(seconds=1))

    # 等待令牌过期
    time.sleep(2)

    # 验证过期令牌
    with pytest.raises(TokenExpiredError):
        verify_token(token)
```

### 2. 前端单元测试

**测试范围**:
- React 组件渲染
- 用户交互和事件处理
- 自定义 Hook 逻辑
- 工具函数和格式化

**测试原则**:
- 测试组件渲染，不测试实现细节
- 模拟用户行为（点击、输入等）
- 使用 Testing Library 最佳实践
- 测试可访问性和语义

**示例测试**:
```typescript
// tests/unit/components/forms/LoginForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LoginForm } from '@/components/forms/LoginForm'

describe('LoginForm', () => {
  const mockOnSubmit = jest.fn()

  beforeEach(() => {
    mockOnSubmit.mockClear()
  })

  test('渲染登录表单', () => {
    render(<LoginForm onSubmit={mockOnSubmit} />)

    // 验证表单元素
    expect(screen.getByLabelText(/用户名或邮箱/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/密码/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /登录/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /登录/i })).toBeDisabled()
  })

  test('表单验证 - 必填字段', async () => {
    render(<LoginForm onSubmit={mockOnSubmit} />)

    const submitButton = screen.getByRole('button', { name: /登录/i })

    // 尝试提交空表单
    fireEvent.click(submitButton)

    // 验证错误消息
    await waitFor(() => {
      expect(screen.getByText(/请输入用户名或邮箱/i)).toBeInTheDocument()
      expect(screen.getByText(/请输入密码/i)).toBeInTheDocument()
    })

    // 验证未调用 onSubmit
    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  test('表单提交 - 有效数据', async () => {
    render(<LoginForm onSubmit={mockOnSubmit} />)
    const user = userEvent.setup()

    // 填写表单
    await user.type(screen.getByLabelText(/用户名或邮箱/i), 'test@example.com')
    await user.type(screen.getByLabelText(/密码/i), 'password123')

    // 提交表单
    await user.click(screen.getByRole('button', { name: /登录/i }))

    // 验证 onSubmit 被调用
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        username: 'test@example.com',
        password: 'password123',
        rememberMe: false
      })
    })
  })

  test('密码可见性切换', async () => {
    render(<LoginForm onSubmit={mockOnSubmit} />)
    const user = userEvent.setup()

    const passwordInput = screen.getByLabelText(/密码/i)
    const toggleButton = screen.getByRole('button', { name: /显示密码/i })

    // 初始类型为 password
    expect(passwordInput).toHaveAttribute('type', 'password')

    // 点击显示密码
    await user.click(toggleButton)

    // 类型变为 text
    expect(passwordInput).toHaveAttribute('type', 'text')
    expect(toggleButton).toHaveAttribute('aria-label', /隐藏密码/i)

    // 再次点击隐藏密码
    await user.click(toggleButton)
    expect(passwordInput).toHaveAttribute('type', 'password')
  })
})
```

## 集成测试策略

### 1. API 集成测试

**测试范围**:
- API 端点功能和响应
- 认证和授权集成
- 数据库操作集成
- 错误处理和状态码

**测试原则**:
- 使用测试数据库（非生产）
- 每个测试后清理测试数据
- 测试完整的请求-响应流程
- 验证数据库状态变化

**示例测试**:
```python
# tests/integration/api/test_auth_api.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
class TestAuthAPI:
    async def test_user_registration(self, client: AsyncClient):
        """测试用户注册"""
        response = await client.post("/api/v1/auth/register", json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePassword123!",
            "first_name": "New",
            "last_name": "User"
        })

        assert response.status_code == 201
        data = response.json()["data"]

        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "password" not in data  # 密码不应返回
        assert data["is_active"] is True
        assert data["is_verified"] is False

    async def test_user_login(self, client: AsyncClient, test_user):
        """测试用户登录"""
        response = await client.post("/api/v1/auth/login", json={
            "username": test_user.username,
            "password": "test_password"
        })

        assert response.status_code == 200
        data = response.json()["data"]

        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["username"] == test_user.username

    async def test_protected_endpoint_with_token(self, client: AsyncClient, test_user):
        """测试带令牌的受保护端点"""
        # 先登录获取令牌
        login_response = await client.post("/api/v1/auth/login", json={
            "username": test_user.username,
            "password": "test_password"
        })
        token = login_response.json()["data"]["access_token"]

        # 使用令牌访问受保护端点
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["username"] == test_user.username

    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        """测试无令牌的受保护端点"""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401
        error = response.json()["error"]
        assert error["code"] == "unauthorized"
```

### 2. 数据库集成测试

**测试范围**:
- 仓储层与数据库交互
- 复杂查询和事务
- 数据库约束和关系
- 数据迁移脚本

**示例测试**:
```python
# tests/integration/database/test_repositories.py
import pytest
from sqlalchemy.orm import Session
from app.infrastructure.database.repositories import UserRepository
from app.infrastructure.database.models import UserModel

@pytest.mark.integration
class TestUserRepository:
    def test_create_user(self, db_session: Session):
        """测试创建用户"""
        repo = UserRepository(db_session)

        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": "hashed_password"
        }

        user = repo.create(user_data)

        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.created_at is not None

        # 验证用户已保存到数据库
        db_user = db_session.query(UserModel).filter_by(id=user.id).first()
        assert db_user is not None
        assert db_user.username == "testuser"

    def test_get_user_by_email(self, db_session: Session, test_user):
        """测试通过邮箱获取用户"""
        repo = UserRepository(db_session)

        user = repo.get_by_email(test_user.email)

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    def test_update_user(self, db_session: Session, test_user):
        """测试更新用户"""
        repo = UserRepository(db_session)

        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "is_active": False
        }

        updated_user = repo.update(test_user, update_data)

        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "Name"
        assert updated_user.is_active is False
        assert updated_user.updated_at is not None

        # 验证数据库已更新
        db_session.refresh(test_user)
        assert test_user.first_name == "Updated"

    def test_delete_user(self, db_session: Session, test_user):
        """测试删除用户（软删除）"""
        repo = UserRepository(db_session)

        success = repo.delete(str(test_user.id))

        assert success is True

        # 验证用户标记为已删除
        db_session.refresh(test_user)
        assert test_user.deleted_at is not None

        # 验证已删除用户不再出现在查询中
        active_users = repo.get_all()
        assert test_user not in active_users
```

## 端到端测试策略

### 1. 后端 E2E 测试

**测试范围**:
- 完整的用户流程
- 多步骤操作序列
- 系统状态变化
- 外部服务集成

**示例测试**:
```python
# tests/e2e/test_auth_flow.py
import pytest
from httpx import AsyncClient

@pytest.mark.e2e
class TestAuthEndToEnd:
    async def test_complete_auth_flow(self, client: AsyncClient):
        """测试完整的认证流程：注册 → 登录 → 使用 → 登出"""

        # 1. 用户注册
        register_response = await client.post("/api/v1/auth/register", json={
            "username": "e2euser",
            "email": "e2e@example.com",
            "password": "E2ePassword123!",
            "first_name": "End",
            "last_name": "ToEnd"
        })
        assert register_response.status_code == 201

        user_id = register_response.json()["data"]["id"]

        # 2. 用户登录
        login_response = await client.post("/api/v1/auth/login", json={
            "username": "e2euser",
            "password": "E2ePassword123!"
        })
        assert login_response.status_code == 200

        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. 访问受保护端点
        me_response = await client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()["data"]["username"] == "e2euser"

        # 4. 更新用户信息
        update_response = await client.put(
            f"/api/v1/users/{user_id}",
            headers=headers,
            json={"first_name": "Updated"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["data"]["first_name"] == "Updated"

        # 5. 用户登出
        logout_response = await client.post("/api/v1/auth/logout", headers=headers)
        assert logout_response.status_code == 204

        # 6. 验证令牌已失效
        me_after_logout = await client.get("/api/v1/auth/me", headers=headers)
        assert me_after_logout.status_code == 401
```

### 2. 前端 E2E 测试（Playwright）

**测试范围**:
- 完整的用户界面流程
- 跨浏览器兼容性
- 响应式设计验证
- 性能和加载测试

**示例测试**:
```typescript
// tests/e2e/auth/login.spec.ts
import { test, expect } from '@playwright/test'

test.describe('登录流程', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
  })

  test('成功登录', async ({ page }) => {
    // 填写登录表单
    await page.fill('input[name="username"]', 'test@example.com')
    await page.fill('input[name="password"]', 'password123')

    // 点击登录按钮
    await page.click('button[type="submit"]')

    // 验证重定向到仪表板
    await page.waitForURL('/dashboard')

    // 验证用户信息显示
    await expect(page.locator('text=欢迎回来')).toBeVisible()

    // 验证导航菜单显示
    await expect(page.locator('nav >> text=用户管理')).toBeVisible()
  })

  test('登录失败 - 无效凭证', async ({ page }) => {
    // 填写错误凭证
    await page.fill('input[name="username"]', 'wrong@example.com')
    await page.fill('input[name="password"]', 'wrongpassword')

    await page.click('button[type="submit"]')

    // 验证错误消息显示
    await expect(page.locator('text=用户名或密码错误')).toBeVisible()

    // 验证仍在登录页面
    await expect(page).toHaveURL('/login')
  })

  test('表单验证', async ({ page }) => {
    // 不填写直接提交
    await page.click('button[type="submit"]')

    // 验证必填字段错误
    await expect(page.locator('text=请输入用户名或邮箱')).toBeVisible()
    await expect(page.locator('text=请输入密码')).toBeVisible()

    // 填写无效邮箱
    await page.fill('input[name="username"]', 'invalid-email')
    await page.click('button[type="submit"]')

    await expect(page.locator('text=请输入有效的邮箱地址')).toBeVisible()
  })

  test('记住我功能', async ({ page, context }) => {
    // 启用记住我
    await page.fill('input[name="username"]', 'test@example.com')
    await page.fill('input[name="password"]', 'password123')
    await page.check('input[name="rememberMe"]')

    await page.click('button[type="submit"]')
    await page.waitForURL('/dashboard')

    // 关闭浏览器标签
    await page.close()

    // 重新打开页面
    const newPage = await context.newPage()
    await newPage.goto('/dashboard')

    // 验证自动登录（记住我生效）
    await expect(newPage).toHaveURL('/dashboard')
    await expect(newPage.locator('text=欢迎回来')).toBeVisible()
  })
})
```

## 性能测试策略

### 1. API 性能测试

**测试工具**: k6 或 Locust
**测试场景**:
- 用户登录性能
- 用户列表查询性能
- 并发用户操作
- 数据库查询优化

**示例测试脚本**:
```javascript
// tests/performance/auth_performance.js (k6)
import http from 'k6/http'
import { check, sleep } from 'k6'
import { randomString, randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js'

export const options = {
  stages: [
    { duration: '30s', target: 50 },   // 逐步增加到50用户
    { duration: '1m', target: 50 },    // 保持50用户1分钟
    { duration: '30s', target: 100 },  // 增加到100用户
    { duration: '1m', target: 100 },   // 保持100用户1分钟
    { duration: '30s', target: 0 },    // 逐步减少到0
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95%请求<500ms
    http_req_failed: ['rate<0.01'],    // 错误率<1%
  }
}

export default function() {
  // 测试登录性能
  const loginPayload = JSON.stringify({
    username: `user_${randomString(8)}@test.com`,
    password: 'TestPassword123!'
  })

  const loginParams = {
    headers: {
      'Content-Type': 'application/json',
    },
  }

  const loginRes = http.post('http://localhost:8000/api/v1/auth/login', loginPayload, loginParams)

  check(loginRes, {
    '登录成功': (r) => r.status === 200,
    '响应时间<500ms': (r) => r.timings.duration < 500,
  })

  // 如果登录成功，测试受保护端点
  if (loginRes.status === 200) {
    const token = loginRes.json().data.access_token

    const protectedParams = {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }

    // 获取当前用户信息
    const meRes = http.get('http://localhost:8000/api/v1/auth/me', protectedParams)

    check(meRes, {
      '获取用户信息成功': (r) => r.status === 200,
      '用户信息响应时间<300ms': (r) => r.timings.duration < 300,
    })

    // 获取用户列表
    const usersRes = http.get('http://localhost:8000/api/v1/users?page=1&per_page=20', protectedParams)

    check(usersRes, {
      '获取用户列表成功': (r) => r.status === 200,
      '用户列表响应时间<1000ms': (r) => r.timings.duration < 1000,
    })
  }

  sleep(randomIntBetween(1, 3))
}
```

## 安全测试策略

### 1. 认证安全测试

**测试项目**:
- SQL 注入防护
- XSS 攻击防护
- CSRF 防护
- 令牌安全测试
- 密码策略验证

**示例测试**:
```python
# tests/security/test_auth_security.py
import pytest
from httpx import AsyncClient

@pytest.mark.security
class TestAuthSecurity:
    async def test_sql_injection_login(self, client: AsyncClient):
        """测试登录接口SQL注入防护"""
        # SQL 注入尝试
        sql_injection_payloads = [
            "' OR '1'='1",
            "admin'--",
            "' UNION SELECT username, password FROM users--",
            "'; DROP TABLE users;--"
        ]

        for payload in sql_injection_payloads:
            response = await client.post("/api/v1/auth/login", json={
                "username": payload,
                "password": payload
            })

            # 应该返回验证错误，而不是服务器错误
            assert response.status_code in [400, 401, 422]
            assert response.status_code != 500  # 不应有内部服务器错误

    async def test_xss_injection_registration(self, client: AsyncClient):
        """测试注册接口XSS防护"""
        xss_payload = "<script>alert('xss')</script>"

        response = await client.post("/api/v1/auth/register", json={
            "username": xss_payload,
            "email": f"{xss_payload}@example.com",
            "password": "ValidPassword123!",
            "first_name": xss_payload,
            "last_name": xss_payload
        })

        # 应该返回验证错误
        assert response.status_code == 422

        error_data = response.json()
        assert "error" in error_data
        assert error_data["error"]["code"] == "validation_error"

        # 验证错误消息中不应包含原始XSS代码
        error_message = str(error_data)
        assert "<script>" not in error_message

    async def test_jwt_tampering(self, client: AsyncClient, test_user):
        """测试JWT令牌篡改防护"""
        # 获取有效令牌
        login_response = await client.post("/api/v1/auth/login", json={
            "username": test_user.username,
            "password": "test_password"
        })

        token = login_response.json()["data"]["access_token"]

        # 尝试篡改令牌
        parts = token.split('.')
        if len(parts) == 3:
            # 篡改载荷部分
            tampered_token = f"{parts[0]}.{parts[1][:-5]}tampered.{parts[2]}"

            response = await client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {tampered_token}"}
            )

            # 应该返回401未授权
            assert response.status_code == 401

    async def test_rate_limiting_login(self, client: AsyncClient):
        """测试登录接口速率限制"""
        failed_responses = 0

        # 尝试多次登录（超过限制）
        for i in range(15):
            response = await client.post("/api/v1/auth/login", json={
                "username": f"testuser{i}",
                "password": "wrongpassword"
            })

            if response.status_code == 429:  # 速率限制
                failed_responses += 1

        # 应该至少有几次返回429
        assert failed_responses > 0
```

## 测试数据管理

### 1. 测试夹具（Fixtures）

**后端夹具**:
```python
# tests/fixtures/users.py
import pytest
from sqlalchemy.orm import Session
from app.infrastructure.database.models import UserModel, RoleModel

@pytest.fixture
def test_user(db_session: Session) -> UserModel:
    """创建测试用户"""
    user = UserModel(
        username="testuser",
        email="test@example.com",
        password_hash="$2b$12$...",  # 哈希后的密码
        first_name="Test",
        last_name="User",
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def admin_user(db_session: Session, admin_role: RoleModel) -> UserModel:
    """创建管理员用户"""
    user = UserModel(
        username="admin",
        email="admin@example.com",
        password_hash="$2b$12$...",
        first_name="Admin",
        last_name="User",
        is_active=True,
        is_verified=True,
        is_superuser=True
    )
    db_session.add(user)
    db_session.commit()

    # 分配管理员角色
    user.roles.append(admin_role)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def user_factory(db_session: Session):
    """用户工厂函数"""
    def create_user(**kwargs):
        defaults = {
            "username": f"user_{uuid.uuid4().hex[:8]}",
            "email": f"{uuid.uuid4().hex[:8]}@example.com",
            "password_hash": "$2b$12$...",
            "is_active": True,
            "is_verified": True
        }
        defaults.update(kwargs)

        user = UserModel(**defaults)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    return create_user
```

### 2. 测试数据清理

**策略**:
- 每个测试函数后清理测试数据
- 使用数据库事务回滚
- 清理临时文件和资源
- 重置模拟和存根

**配置示例**:
```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infrastructure.database.models import Base

@pytest.fixture(scope="session")
def test_engine():
    """测试数据库引擎"""
    engine = create_engine("postgresql://test:test@localhost/test_db")

    # 创建测试表
    Base.metadata.create_all(engine)

    yield engine

    # 测试结束后清理
    Base.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture
def db_session(test_engine):
    """数据库会话，自动回滚"""
    connection = test_engine.connect()
    transaction = connection.begin()

    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    # 测试后回滚并关闭
    session.close()
    transaction.rollback()
    connection.close()
```

## 测试覆盖率要求

### 1. 覆盖率目标

**后端覆盖率**:
- 总体覆盖率: ≥ 85%
- 业务逻辑覆盖率: ≥ 90%
- 核心模块覆盖率: ≥ 95%
- 工具函数覆盖率: ≥ 80%

**前端覆盖率**:
- 总体覆盖率: ≥ 80%
- 组件覆盖率: ≥ 85%
- Hook 覆盖率: ≥ 90%
- 工具函数覆盖率: ≥ 85%

### 2. 覆盖率报告

**生成报告**:
```bash
# 后端覆盖率报告
pytest --cov=app --cov-report=html --cov-report=term

# 前端覆盖率报告
npm test -- --coverage
```

**报告内容**:
- 行覆盖率（Line Coverage）
- 分支覆盖率（Branch Coverage）
- 函数覆盖率（Function Coverage）
- 未覆盖代码分析

## CI/CD 集成

### 1. 测试流水线

**阶段**:
1. **代码质量检查**
   - 代码格式化检查（Black, Prettier）
   - 代码规范检查（Flake8, ESLint）
   - 类型检查（Mypy, TypeScript）
   - 安全扫描（Bandit, npm audit）

2. **单元测试**
   - 运行所有单元测试
   - 生成覆盖率报告
   - 检查覆盖率阈值

3. **集成测试**
   - 运行 API 集成测试
   - 运行数据库集成测试
   - 运行前端集成测试

4. **端到端测试**
   - 运行关键用户流程测试
   - 跨浏览器测试
   - 性能基准测试

5. **部署前测试**
   - 生产环境冒烟测试
   - 性能负载测试
   - 安全扫描测试

### 2. GitHub Actions 配置示例

```yaml
name: Test Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  code-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install black flake8 mypy bandit

      - name: Code formatting check
        run: black --check app/

      - name: Lint check
        run: flake8 app/

      - name: Type check
        run: mypy app/

      - name: Security scan
        run: bandit -r app/

  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -e .[test]

      - name: Run unit tests
        run: |
          pytest tests/unit/ -v --cov=app --cov-report=xml

      - name: Run integration tests
        run: |
          pytest tests/integration/ -v

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: backend

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm test -- --coverage

      - name: Run E2E tests
        run: npx playwright test

      - name: Upload Playwright report
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 30
```

## 测试最佳实践

### 1. 测试命名规范

**后端测试命名**:
- 测试文件: `test_<module>_<functionality>.py`
- 测试类: `Test<ClassName>`
- 测试方法: `test_<scenario>_<expected_result>`

**前端测试命名**:
- 测试文件: `<Component>.test.tsx` 或 `<Component>.spec.ts`
- 测试描述: 使用 `describe` 描述组件或功能
- 测试用例: 使用 `test` 或 `it` 描述具体场景

### 2. 测试组织原则

**AAA 模式** (Arrange-Act-Assert):
```python
def test_user_creation():
    # Arrange: 准备测试数据
    user_data = {"username": "test", "email": "test@example.com"}

    # Act: 执行被测试代码
    user = user_service.create_user(user_data)

    # Assert: 验证结果
    assert user.username == "test"
    assert user.email == "test@example.com"
```

**Given-When-Then 模式**:
```typescript
test('用户登录成功', () => {
  // Given: 给定用户存在且凭证正确
  const user = { username: 'test', password: 'correct' }

  // When: 当用户尝试登录
  const result = login(user.username, user.password)

  // Then: 那么应该返回成功响应
  expect(result.success).toBe(true)
  expect(result.token).toBeDefined()
})
```

### 3. 测试数据管理

**原则**:
- 每个测试独立，不依赖其他测试
- 使用夹具创建测试数据
- 测试后清理测试数据
- 避免使用生产数据

### 4. 测试性能优化

**优化策略**:
- 并行运行独立测试
- 使用内存数据库进行单元测试
- 缓存昂贵的测试设置
- 避免不必要的 I/O 操作

## 故障排查和调试

### 1. 测试失败处理

**常见问题**:
- 测试数据污染
- 异步操作时序问题
- 环境配置差异
- 依赖服务不可用

**调试技巧**:
- 使用 `pytest -v` 显示详细输出
- 使用 `pytest --pdb` 进入调试器
- 添加调试日志和断言
- 检查测试数据状态

### 2. 测试环境管理

**环境配置**:
- 开发环境: 本地运行，使用开发数据库
- 测试环境: CI/CD 运行，使用测试数据库
- 预发布环境: 模拟生产环境
- 生产环境: 仅运行监控和健康检查

---
*本文档是测试策略的权威参考，所有测试实现必须遵循此策略。测试策略变更需要更新此文档并通知相关团队。*