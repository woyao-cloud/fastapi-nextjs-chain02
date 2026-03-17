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

```python
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, RedisDsn, EmailStr
from typing import Optional

class Settings(BaseSettings):
    # 应用配置
    PROJECT_NAME: str = "User Management System"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 数据库配置
    DATABASE_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis 配置
    REDIS_URL: Optional[RedisDsn] = None

    # JWT 配置
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 安全配置
    BCRYPT_ROUNDS: int = 12
    PASSWORD_MIN_LENGTH: int = 8

    # 邮件配置
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None

    # CORS 配置
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 2. 依赖注入 (app/dependencies.py)

```python
from typing import Annotated, Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.config import settings
from app.infrastructure.database.session import get_db
from app.infrastructure.database.repositories import (
    UserRepository,
    RoleRepository,
    PermissionRepository
)
from app.schemas.token import TokenPayload
from app.core.security import verify_token

# 数据库会话依赖
def get_database() -> Generator[Session, None, None]:
    db = get_db()
    try:
        yield db
    finally:
        db.close()

DatabaseDep = Annotated[Session, Depends(get_database)]

# 仓储依赖
def get_user_repository(db: DatabaseDep) -> UserRepository:
    return UserRepository(db)

def get_role_repository(db: DatabaseDep) -> RoleRepository:
    return RoleRepository(db)

def get_permission_repository(db: DatabaseDep) -> PermissionRepository:
    return PermissionRepository(db)

# 认证依赖
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(token, credentials_exception)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user

# 权限依赖
def require_permission(permission_name: str):
    def dependency(
        current_user: User = Depends(get_current_user),
        permission_repo: PermissionRepository = Depends(get_permission_repository)
    ) -> User:
        if not current_user.has_permission(permission_name, permission_repo):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return dependency
```

### 3. 数据库模型 (infrastructure/database/models/)

**Base 模型**:
```python
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
```

**User 模型**:
```python
from sqlalchemy import Boolean, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class UserModel(BaseModel):
    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    avatar_url = Column(Text)
    phone_number = Column(String(20))
    timezone = Column(String(50), default="UTC")
    locale = Column(String(10), default="en-US")
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False, index=True)
    is_superuser = Column(Boolean, default=False)
    last_login_at = Column(DateTime(timezone=True))
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))
    deleted_at = Column(DateTime(timezone=True))

    # 关系
    roles = relationship("RoleModel", secondary="user_roles", back_populates="users")
    sessions = relationship("UserSessionModel", back_populates="user", cascade="all, delete-orphan")

    # 索引在表定义中通过 __table_args__ 定义
    __table_args__ = (
        Index('idx_users_active', 'is_active'),
        Index('idx_users_verified', 'is_verified'),
        Index('idx_users_created_at', 'created_at'),
    )
```

### 4. 仓储模式 (infrastructure/database/repositories/)

**基础仓储**:
```python
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.infrastructure.database.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: str) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        query = self.db.query(self.model)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)

        return query.offset(skip).limit(limit).all()

    def create(self, obj_in: Dict[str, Any]) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: ModelType, obj_in: Dict[str, Any]) -> ModelType:
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: str) -> bool:
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False
```

**用户仓储**:
```python
from typing import Optional
from sqlalchemy import or_
from app.infrastructure.database.models.user import UserModel
from .base_repository import BaseRepository

class UserRepository(BaseRepository[UserModel]):
    def __init__(self, db):
        super().__init__(UserModel, db)

    def get_by_email(self, email: str) -> Optional[UserModel]:
        return self.db.query(self.model).filter(
            self.model.email == email,
            self.model.deleted_at.is_(None)
        ).first()

    def get_by_username(self, username: str) -> Optional[UserModel]:
        return self.db.query(self.model).filter(
            self.model.username == username,
            self.model.deleted_at.is_(None)
        ).first()

    def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserModel]:
        return self.db.query(self.model).filter(
            self.model.deleted_at.is_(None),
            or_(
                self.model.username.ilike(f"%{query}%"),
                self.model.email.ilike(f"%{query}%"),
                self.model.first_name.ilike(f"%{query}%"),
                self.model.last_name.ilike(f"%{query}%")
            )
        ).offset(skip).limit(limit).all()
```

### 5. 应用服务 (application/services/)

**用户服务**:
```python
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.domain.entities.user import User
from app.infrastructure.database.repositories import UserRepository, RoleRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.security import get_password_hash, verify_password
from app.core.events import emit_event

class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository
    ):
        self.user_repo = user_repository
        self.role_repo = role_repository

    def create_user(self, user_create: UserCreate) -> UserResponse:
        # 检查用户名和邮箱是否已存在
        if self.user_repo.get_by_username(user_create.username):
            raise ValueError("Username already exists")

        if self.user_repo.get_by_email(user_create.email):
            raise ValueError("Email already exists")

        # 创建用户
        user_dict = user_create.dict()
        user_dict["password_hash"] = get_password_hash(user_create.password)
        del user_dict["password"]

        db_user = self.user_repo.create(user_dict)

        # 分配默认角色
        default_role = self.role_repo.get_default_role()
        if default_role:
            self.user_repo.assign_role(db_user.id, default_role.id)

        # 发送事件
        emit_event("user.created", {
            "user_id": str(db_user.id),
            "email": db_user.email,
            "username": db_user.username
        })

        return UserResponse.from_orm(db_user)

    def update_user(
        self,
        user_id: str,
        user_update: UserUpdate,
        current_user: User
    ) -> UserResponse:
        # 权限检查
        if str(current_user.id) != user_id and not current_user.is_superuser:
            raise PermissionError("Cannot update other users")

        db_user = self.user_repo.get_by_id(user_id)
        if not db_user:
            raise ValueError("User not found")

        update_data = user_update.dict(exclude_unset=True)

        # 如果需要更新密码
        if "password" in update_data:
            update_data["password_hash"] = get_password_hash(update_data["password"])
            del update_data["password"]

        updated_user = self.user_repo.update(db_user, update_data)

        emit_event("user.updated", {
            "user_id": user_id,
            "updated_by": str(current_user.id),
            "changes": update_data.keys()
        })

        return UserResponse.from_orm(updated_user)

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        db_user = self.user_repo.get_by_username(username)
        if not db_user:
            # 也尝试通过邮箱查找
            db_user = self.user_repo.get_by_email(username)

        if not db_user:
            return None

        if not verify_password(password, db_user.password_hash):
            return None

        if not db_user.is_active:
            raise ValueError("User account is disabled")

        # 更新最后登录时间
        self.user_repo.update(db_user, {"last_login_at": datetime.utcnow()})

        return User.from_orm(db_user)
```

### 6. API 路由 (api/v1/)

**用户路由示例**:
```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from app.schemas.user import UserResponse, UserCreate, UserUpdate
from app.application.services.user_service import UserService
from app.api.deps import (
    get_current_user,
    require_permission,
    get_user_service
)

router = APIRouter()

@router.post("/", response_model=UserResponse)
async def create_user(
    user_in: UserCreate,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_permission("users.create"))
):
    """创建新用户"""
    try:
        user = user_service.create_user(user_in)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_permission("users.list"))
):
    """获取用户列表"""
    if search:
        users = user_service.search_users(search, skip, limit)
    else:
        users = user_service.get_users(skip, limit)
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_permission("users.read"))
):
    """获取单个用户"""
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_in: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_permission("users.update"))
):
    """更新用户信息"""
    try:
        user = user_service.update_user(user_id, user_in, current_user)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_permission("users.delete"))
):
    """删除用户（软删除）"""
    success = user_service.delete_user(user_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
```

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

## 开发指南

### 1. 本地开发
```bash
# 安装依赖
pip install -e .

# 启动数据库
docker-compose up -d postgres redis

# 运行迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload
```

### 2. 测试运行
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/unit/test_user_service.py

# 生成测试覆盖率报告
pytest --cov=app --cov-report=html
```

### 3. 代码质量
```bash
# 代码格式化
black app/
isort app/

# 类型检查
mypy app/

# 安全检查
bandit -r app/
```

---
*本文档是后端架构的权威参考，所有后端开发必须遵循此架构设计。架构变更需要更新此文档并通知相关团队。*