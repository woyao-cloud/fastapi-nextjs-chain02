# FastAPI 后端架构设计

## 概述

本文档定义了用户管理系统后端的架构设计。我们采用 FastAPI 作为主要框架，遵循分层架构和领域驱动设计原则，确保系统的可维护性、可扩展性和高性能。

## 架构原则

### 1. 分层架构
- **表现层 (API Layer)**: 处理 HTTP 请求/响应，路由分发
- **应用层 (Service Layer)**: 业务逻辑协调，事务管理
- **领域层 (Domain Layer)**: 核心业务规则和实体
- **基础设施层 (Infrastructure Layer)**: 外部依赖（数据库、缓存、消息队列等）

### 2. 依赖倒置原则
- 高层模块不依赖低层模块，两者都依赖抽象
- 抽象不依赖细节，细节依赖抽象
- 通过依赖注入实现松耦合

### 3. 关注点分离
- 每个模块/组件有单一的明确职责
- 业务逻辑与技术实现分离
- 数据访问与业务逻辑分离

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── dependencies.py      # 依赖注入定义
│   ├── middleware.py        # 自定义中间件
│   ├── exceptions.py        # 自定义异常
│   ├── api/                 # API 路由
│   │   ├── __init__.py
│   │   ├── v1/              # API 版本 1
│   │   │   ├── __init__.py
│   │   │   ├── auth.py      # 认证相关路由
│   │   │   ├── users.py     # 用户管理路由
│   │   │   ├── roles.py     # 角色管理路由
│   │   │   ├── permissions.py # 权限管理路由
│   │   │   └── health.py    # 健康检查路由
│   │   └── deps.py          # API 层依赖
│   ├── core/                # 核心模块
│   │   ├── __init__.py
│   │   ├── security.py      # 安全相关（JWT、密码哈希等）
│   │   ├── auth.py          # 认证逻辑
│   │   ├── permissions.py   # 权限检查逻辑
│   │   └── events.py        # 事件处理
│   ├── domain/              # 领域模型
│   │   ├── __init__.py
│   │   ├── entities/        # 领域实体
│   │   │   ├── user.py
│   │   │   ├── role.py
│   │   │   └── permission.py
│   │   └── value_objects/   # 值对象
│   │       └── email.py
│   ├── application/         # 应用服务层
│   │   ├── __init__.py
│   │   ├── services/        # 应用服务
│   │   │   ├── user_service.py
│   │   │   ├── auth_service.py
│   │   │   └── role_service.py
│   │   └── use_cases/       # 用例
│   │       ├── register_user.py
│   │       └── assign_role.py
│   ├── infrastructure/      # 基础设施层
│   │   ├── __init__.py
│   │   ├── database/        # 数据库相关
│   │   │   ├── __init__.py
│   │   │   ├── session.py   # 数据库会话管理
│   │   │   ├── models/      # SQLAlchemy 模型
│   │   │   │   ├── base.py
│   │   │   │   ├── user.py
│   │   │   │   ├── role.py
│   │   │   │   └── permission.py
│   │   │   └── repositories/ # 仓储实现
│   │   │       ├── user_repository.py
│   │   │       ├── role_repository.py
│   │   │       └── base_repository.py
│   │   ├── cache/           # 缓存
│   │   │   └── redis_client.py
│   │   ├── email/           # 邮件服务
│   │   │   └── email_service.py
│   │   └── storage/         # 文件存储
│   │       └── s3_client.py
│   ├── schemas/             # Pydantic 模式
│   │   ├── __init__.py
│   │   ├── auth.py          # 认证相关模式
│   │   ├── user.py          # 用户相关模式
│   │   ├── role.py          # 角色相关模式
│   │   └── common.py        # 通用模式
│   └── utils/               # 工具函数
│       ├── __init__.py
│       ├── validators.py    # 自定义验证器
│       ├── pagination.py    # 分页工具
│       └── logging.py       # 日志配置
├── alembic/                 # 数据库迁移
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
├── tests/                   # 测试
│   ├── __init__.py
│   ├── conftest.py          # 测试配置
│   ├── unit/                # 单元测试
│   ├── integration/         # 集成测试
│   └── fixtures/            # 测试数据
├── scripts/                 # 脚本
│   ├── init_db.py
│   └── create_admin.py
├── pyproject.toml           # 项目配置和依赖
├── docker-compose.yml       # 开发环境 Docker 配置
├── Dockerfile               # 生产环境 Dockerfile
└── README.md
```

## 核心组件设计

### 1. 配置管理 (app/config.py)



## 安全设计

### 1. 认证机制
- **JWT 令牌**: 使用 HS256 算法，短有效期访问令牌 + 长有效期刷新令牌
- **令牌刷新**: 支持无感刷新，刷新时验证设备和 IP
- **多重验证**: 支持 TOTP 二次验证（可选）

### 2. 授权机制
- **RBAC 模型**: 基于角色的访问控制
- **权限粒度**: 细粒度权限控制到资源+操作级别
- **权限缓存**: 用户权限缓存到 Redis，减少数据库查询

### 3. 安全防护
- **速率限制**: API 访问频率限制
- **SQL 注入防护**: 使用参数化查询，ORM 自动防护
- **XSS 防护**: 输入输出转义，CSP 头
- **CSRF 防护**: 同源策略，状态更改操作使用 CSRF 令牌

## 性能优化

### 1. 数据库优化
- **连接池**: SQLAlchemy 连接池配置
- **查询优化**: N+1 查询防护，合理使用 eager loading
- **索引策略**: 基于查询模式的复合索引
- **读写分离**: 支持主从复制（可选）

### 2. 缓存策略
- **Redis 缓存**: 热点数据缓存（用户信息、权限数据）
- **响应缓存**: API 响应缓存，支持 ETag
- **分布式锁**: 使用 Redis 实现分布式锁

### 3. 异步处理
- **后台任务**: 使用 Celery 或 RQ 处理耗时操作
- **事件驱动**: 使用消息队列解耦系统组件
- **流式响应**: 支持大数据的流式返回

## 监控和日志

### 1. 日志策略
- **结构化日志**: JSON 格式，包含请求 ID
- **日志分级**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **日志聚合**: 发送到 ELK Stack 或 Loki

### 2. 指标监控
- **Prometheus**: 暴露 metrics 端点
- **健康检查**: /health 端点，包含依赖服务状态
- **性能指标**: 请求延迟，错误率，数据库查询时间

### 3. 追踪系统
- **OpenTelemetry**: 分布式追踪
- **请求追踪**: 跨服务请求追踪
- **性能分析**: 慢请求分析，瓶颈识别

## 部署配置

### 1. Docker 配置
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# 复制应用代码
COPY . .

# 运行应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. 环境变量配置
```bash
# 数据库
DATABASE_URL=postgresql://user:password@postgres:5432/user_management

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production

# 邮件
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```




*本文档是后端架构的权威参考，所有后端开发必须遵循此架构设计。架构变更需要更新此文档并通知相关团队。*