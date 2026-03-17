"""
数据库会话管理
SQLAlchemy 异步会话配置和生命周期管理
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app.config import settings

# 声明式基类
Base = declarative_base()

# 全局数据库引擎
engine = create_async_engine(
    str(settings.DATABASE_URL),
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,  # 连接池健康检查
    pool_recycle=3600,   # 连接回收时间（秒）
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 避免提交后属性过期
    autoflush=False,         # 手动控制flush
)


async def get_db_session() -> AsyncSession:
    """
    获取数据库会话
    使用方式: async with get_db_session() as session:
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    初始化数据库
    创建所有表（仅用于开发环境）
    """
    async with engine.begin() as conn:
        # 在生产环境中应该使用Alembic迁移，而不是直接创建表
        if settings.DEBUG:
            from app.infrastructure.database.models import (
                base,  # 导入所有模型以注册它们
            )
            await conn.run_sync(Base.metadata.create_all)
            print("数据库表创建完成")
        else:
            print("生产环境请使用Alembic迁移")


async def close_db() -> None:
    """
    关闭数据库连接
    应用关闭时调用
    """
    await engine.dispose()
    print("数据库连接已关闭")


# 测试连接
async def test_connection() -> bool:
    """
    测试数据库连接
    返回连接是否成功
    """
    try:
        async with engine.connect() as conn:
            # 执行简单的查询测试连接
            result = await conn.execute("SELECT 1")
            await result.close()
            return True
    except Exception as e:
        print(f"数据库连接测试失败: {e}")
        return False