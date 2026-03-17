# 数据库设计文档

## 概述

本文档定义了用户管理系统的数据库架构。我们使用 PostgreSQL 作为主要数据库，SQLite 用于开发和测试环境。

## 设计原则

### 1. 规范化设计
- 遵循第三范式（3NF），减少数据冗余
- 合理使用外键约束确保数据完整性
- 避免过度规范化导致的性能问题

### 2. 扩展性考虑
- 使用 UUID 作为主键，便于分布式系统
- 设计支持多租户（如果需要）
- 考虑未来功能扩展的灵活性

### 3. 性能优化
- 合理使用索引，平衡读写性能
- 分区策略设计（按时间分区）
- 查询模式驱动的表结构设计

### 4. 安全性
- 敏感字段加密存储（密码、令牌等）
- 审计日志记录所有重要操作
- 数据保留和清理策略

## 实体关系图

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     users       │     │     roles       │     │  permissions    │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │     │ id (PK)         │
│ username        │     │ name            │     │ name            │
│ email           │     │ description     │     │ description     │
│ password_hash   │     │ is_default      │     │ resource        │
│ first_name      │     │ created_at      │     │ action          │
│ last_name       │     │ updated_at      │     │ created_at      │
│ is_active       │     └────────┬────────┘     │ updated_at      │
│ is_verified     │              │              └────────┬────────┘
│ last_login_at   │              │                       │
│ created_at      │              │                       │
│ updated_at      │              │                       │
└────────┬────────┘              │                       │
         │                       │                       │
         │              ┌────────▼────────┐              │
         │              │  user_roles     │              │
         └──────────────┤                 │              │
                        ├─────────────────┤              │
                        │ user_id (FK)    │              │
                        │ role_id (FK)    │              │
                        │ assigned_at     │              │
                        │ assigned_by     │              │
                        └────────┬────────┘              │
                                 │                       │
                        ┌────────▼────────┐              │
                        │ role_permissions│              │
                        ├─────────────────┤              │
                        │ role_id (FK)    │              │
                        │ permission_id(FK)│             │
                        │ granted_at      │              │
                        │ granted_by      │              │
                        └─────────────────┘              │
                                                         │
┌─────────────────┐     ┌─────────────────┐             │
│  audit_logs     │     │  user_sessions  │             │
├─────────────────┤     ├─────────────────┤             │
│ id (PK)         │     │ id (PK)         │             │
│ user_id (FK)    │     │ user_id (FK)    │             │
│ action          │     │ session_token   │             │
│ resource_type   │     │ refresh_token   │             │
│ resource_id     │     │ device_info     │             │
│ old_values      │     │ ip_address      │             │
│ new_values      │     │ last_activity_at│             │
│ ip_address      │     │ expires_at      │             │
│ user_agent      │     │ created_at      │             │
│ created_at      │     └─────────────────┘             │
└─────────────────┘                                     │
                                                        │
┌─────────────────┐     ┌─────────────────┐             │
│ password_resets │     │  email_verification │         │
├─────────────────┤     ├─────────────────┤             │
│ id (PK)         │     │ id (PK)         │             │
│ user_id (FK)    │     │ user_id (FK)    │             │
│ token_hash      │     │ token_hash      │             │
│ expires_at      │     │ expires_at      │             │
│ used_at         │     │ verified_at     │             │
│ created_at      │     │ created_at      │             │
└─────────────────┘     └─────────────────┘             │
                                                        │
                                                ┌───────▼───────┐
                                                │ login_attempts│
                                                ├───────────────┤
                                                │ id (PK)       │
                                                │ username      │
                                                │ ip_address    │
                                                │ success       │
                                                │ user_agent    │
                                                │ created_at    │
                                                └───────────────┘
```

## 表结构详细设计

### 1. users 表 - 用户基本信息

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    avatar_url TEXT,
    phone_number VARCHAR(20),
    timezone VARCHAR(50) DEFAULT 'UTC',
    locale VARCHAR(10) DEFAULT 'en-US',
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    is_superuser BOOLEAN DEFAULT false,
    last_login_at TIMESTAMP WITH TIME ZONE,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT valid_username CHECK (username ~* '^[a-zA-Z0-9_.-]{3,50}$'),
    CONSTRAINT valid_phone CHECK (
        phone_number IS NULL OR
        phone_number ~* '^\+?[1-9]\d{1,14}$'
    )
);

-- 索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = true;
CREATE INDEX idx_users_verified ON users(is_verified) WHERE is_verified = true;
CREATE INDEX idx_users_created_at ON users(created_at DESC);
```

### 2. roles 表 - 角色定义

```sql
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT false,
    is_system BOOLEAN DEFAULT false,
    weight INTEGER DEFAULT 0, -- 用于角色层级排序
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT valid_role_name CHECK (name ~* '^[a-z_]{3,50}$')
);

-- 默认角色
INSERT INTO roles (name, description, is_default, is_system, weight) VALUES
    ('superadmin', '超级管理员，拥有所有权限', false, true, 1000),
    ('admin', '管理员，拥有大部分管理权限', false, true, 900),
    ('user', '普通用户', true, true, 100),
    ('guest', '访客角色', false, true, 10);
```

### 3. permissions 表 - 权限定义

```sql
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    resource VARCHAR(50) NOT NULL, -- 资源类型：user, role, permission等
    action VARCHAR(50) NOT NULL,   -- 操作：create, read, update, delete, list
    scope VARCHAR(50) DEFAULT 'global', -- 范围：global, own, team等
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT valid_permission_name CHECK (name ~* '^[a-z_.]{5,100}$'),
    CONSTRAINT valid_action CHECK (action IN ('create', 'read', 'update', 'delete', 'list', 'manage'))
);

-- 索引
CREATE INDEX idx_permissions_resource ON permissions(resource);
CREATE INDEX idx_permissions_action ON permissions(action);
CREATE INDEX idx_permissions_resource_action ON permissions(resource, action);
```

### 4. user_roles 表 - 用户角色关联

```sql
CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assigned_by UUID REFERENCES users(id),
    expires_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',

    -- 唯一约束，避免重复分配
    UNIQUE(user_id, role_id),

    -- 外键索引
    CONSTRAINT fk_user_roles_user FOREIGN KEY (assigned_by) REFERENCES users(id)
);

-- 索引
CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_role_id ON user_roles(role_id);
CREATE INDEX idx_user_roles_expires ON user_roles(expires_at) WHERE expires_at IS NOT NULL;
```

### 5. role_permissions 表 - 角色权限关联

```sql
CREATE TABLE role_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    granted_by UUID REFERENCES users(id),
    metadata JSONB DEFAULT '{}',

    -- 唯一约束
    UNIQUE(role_id, permission_id),

    -- 外键索引
    CONSTRAINT fk_role_permissions_granted_by FOREIGN KEY (granted_by) REFERENCES users(id)
);

-- 索引
CREATE INDEX idx_role_permissions_role_id ON role_permissions(role_id);
CREATE INDEX idx_role_permissions_permission_id ON role_permissions(permission_id);
```

### 6. audit_logs 表 - 审计日志

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL, -- create, update, delete, login, logout等
    resource_type VARCHAR(50) NOT NULL, -- 资源类型
    resource_id UUID, -- 资源ID
    old_values JSONB, -- 变更前值
    new_values JSONB, -- 变更后值
    changes JSONB, -- 具体变更字段
    ip_address INET,
    user_agent TEXT,
    request_id VARCHAR(100), -- 用于关联同一请求的多个日志
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- 按月分区（示例）
CREATE TABLE audit_logs_2024_01 PARTITION OF audit_logs
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- 索引
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_logs_request_id ON audit_logs(request_id);
```

### 7. user_sessions 表 - 用户会话

```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(500) NOT NULL,
    refresh_token VARCHAR(500) NOT NULL,
    device_info JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- 唯一约束
    UNIQUE(session_token),
    UNIQUE(refresh_token)
);

-- 索引
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX idx_user_sessions_last_activity ON user_sessions(last_activity_at DESC);
```

### 8. password_resets 表 - 密码重置令牌

```sql
CREATE TABLE password_resets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- 确保一个用户同时只有一个有效令牌
    UNIQUE(user_id) WHERE used_at IS NULL AND expires_at > NOW()
);

-- 索引
CREATE INDEX idx_password_resets_token_hash ON password_resets(token_hash);
CREATE INDEX idx_password_resets_expires_at ON password_resets(expires_at);
```

### 9. email_verification 表 - 邮箱验证

```sql
CREATE TABLE email_verification (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- 唯一约束
    UNIQUE(token_hash),
    UNIQUE(user_id) WHERE verified_at IS NULL AND expires_at > NOW()
);

-- 索引
CREATE INDEX idx_email_verification_token_hash ON email_verification(token_hash);
CREATE INDEX idx_email_verification_expires_at ON email_verification(expires_at);
```

### 10. login_attempts 表 - 登录尝试记录

```sql
CREATE TABLE login_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    ip_address INET NOT NULL,
    success BOOLEAN NOT NULL,
    failure_reason VARCHAR(100),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- 索引
CREATE INDEX idx_login_attempts_username ON login_attempts(username);
CREATE INDEX idx_login_attempts_ip_address ON login_attempts(ip_address);
CREATE INDEX idx_login_attempts_success ON login_attempts(success);
CREATE INDEX idx_login_attempts_created_at ON login_attempts(created_at DESC);
```

## 数据迁移策略

### 迁移工具
- 使用 **Alembic** 进行数据库迁移管理
- 所有迁移脚本必须可回滚（提供 downgrade 函数）
- 迁移脚本必须包含必要的索引和约束

### 迁移规范
1. **版本命名**: `YYYYMMDD_HHMMSS_description.py`
2. **测试要求**: 每个迁移必须在测试环境中验证
3. **回滚计划**: 生产环境迁移必须有回滚计划
4. **数据迁移**: 大数据量迁移需要分批进行

### 迁移脚本示例
```python
"""YYYYMMDD_HHMMSS_create_users_table.py"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        # ... 其他字段
    )

    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_username', 'users', ['username'], unique=True)

def downgrade():
    op.drop_index('idx_users_username', table_name='users')
    op.drop_index('idx_users_email', table_name='users')
    op.drop_table('users')
```

## 性能优化策略

### 索引策略
1. **查询驱动索引**: 根据实际查询模式创建索引
2. **复合索引**: 对频繁查询的多个字段创建复合索引
3. **部分索引**: 对特定条件的查询创建部分索引
4. **表达式索引**: 对常用表达式创建索引

### 分区策略
1. **按时间分区**: 日志类表按时间范围分区
2. **按范围分区**: 特定范围的数据分区
3. **按列表分区**: 固定值的列表分区

### 维护策略
1. **定期清理**: 自动清理过期数据
2. **索引重建**: 定期重建碎片化索引
3. **统计更新**: 定期更新表统计信息
4. **性能监控**: 监控慢查询和锁等待

## 安全策略

### 数据加密
1. **字段级加密**: 密码、令牌等敏感字段必须加密存储
2. **传输加密**: 所有数据传输使用 TLS
3. **密钥管理**: 使用密钥管理服务管理加密密钥

### 访问控制
1. **最小权限**: 数据库用户仅具有必要权限
2. **连接限制**: 限制数据库连接源 IP
3. **审计日志**: 记录所有数据库操作

### 备份和恢复
1. **定期备份**: 每日完整备份 + 事务日志备份
2. **异地备份**: 备份数据存储在不同地理位置
3. **恢复测试**: 定期测试备份恢复流程

## 数据保留策略

### 保留期限
1. **用户数据**: 永久保留（除非用户删除）
2. **审计日志**: 13个月（满足合规要求）
3. **会话数据**: 30天
4. **登录尝试**: 90天
5. **临时令牌**: 使用后立即删除或标记为已使用

### 清理策略
1. **自动清理**: 使用调度任务自动清理过期数据
2. **归档策略**: 重要数据先归档后清理
3. **合规要求**: 满足 GDPR、CCPA 等数据保护法规

---
*本文档是数据库设计的权威参考，任何数据库变更必须首先更新此文档，并通过 Alembic 迁移脚本实现。*